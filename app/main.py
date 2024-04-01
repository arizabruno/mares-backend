from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from typing import List
from pydantic import BaseModel
import joblib
from data_access.queries import *
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from utils.utils import get_user_interest_df

# Model Definitions
class Favorites(BaseModel):
    ids: List[int]

class NewFavorite(BaseModel):
    movie_id: int
    email: str

# Application Initialization
app = FastAPI()

# CORS Configuration
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "POST", "PUT"],
    allow_headers=["*"],
)

# Model Loading
movies_model_filename = 'models/movies_similar_users_recommender.pkl'

try:
    movies_model = joblib.load(movies_model_filename)
except Exception as e:
    print(f"Model file not found: {movies_model_filename}. Please check the file path.")
    raise SystemExit



def generate_movies_recommendations(email: str):
    """
    Generates and updates movie recommendations for a user based on their favorite movies.

    Parameters:
    - email (str): The email of the user for whom to generate recommendations.

    Raises:
    - HTTPException: If there's an error in fetching the favorites, if the favorites list is too short,
                     or if there's an error during the recommendation process.
    """
    try:
        # Retrieve favorite movies for the user
        resources = get_all_favorites_movies_by_email(email)
        
        if resources == None:
            print("No movies IDs to generate recommendations.")
            return 
            
        favorite_resources_ids = [m['movie_id'] for m in resources]

        # Check if there are enough favorite movies to generate recommendations
        if len(favorite_resources_ids) < 2:
            print("Insufficient movies IDs to generate recommendations.")
            return

        # Preprocess favorite movies to summarize user interests
        prep_fav_resources = get_preprocessed_movies_by_ids(favorite_resources_ids)
        df = pd.DataFrame(prep_fav_resources)
        user_interest = get_user_interest_df(df)

        # Use model to find similar users
        similar_users = movies_model.recommend_similar_users(user_interest)

        # Get recommendations from similar users' good-rated movies
        good_rated_movies = get_good_rated_movies_by_user_ids(similar_users)
        
        if not good_rated_movies or len(good_rated_movies) < 1:
            return
        
        movies_ids_recommendations = [m['movie_id'] for m in good_rated_movies]

        print("!!!", movies_ids_recommendations)
        # Filter out already favorite movies
        favorites_ids_set = set(favorite_resources_ids)
        recommendations_ids_set = set(movies_ids_recommendations)
        final_recommendation_ids = list(recommendations_ids_set - favorites_ids_set)

        # Limit the number of recommendations
        MAX_RECS = 30
        if len(final_recommendation_ids) > MAX_RECS:
            final_recommendation_ids = final_recommendation_ids[:MAX_RECS]

        # Update user recommendations
        update_movies_recommendations(final_recommendation_ids, email)

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail="An error occurred during the recommendation process.")

    
@app.get("/")
async def main():
    """
    Redirects to the API documentation page.

    Returns:
    - RedirectResponse: Redirects the client to the API documentation.
    """
    return RedirectResponse(url="/docs")


@app.get("/recommend")
async def recommend_resources(username: str = Query(default=""), domain: str = Query(default="gmail")) -> list:
    """
    Endpoint to generate and fetch movie recommendations for a user based on their email.
    Constructs the user's email from the provided username and domain, then fetches a list of random movie recommendations.

    Parameters:
    - username (str): The username part of the user's email.
    - domain (str): The domain part of the user's email. Defaults to 'gmail'.

    Returns:
    - A list of dictionaries, each representing a movie recommendation with details fetched from the database.
    """
    email = f"{username}@{domain}"

    try:
        recs = get_random_movies_recommendations_from_user_by_email(email)
        if not recs:
            raise HTTPException(status_code=404, detail="No recommendations found for the specified user.")
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_resources(title: str = Query(default=""), page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1)) -> list:
    """
    Searches for movies by their title with pagination support.

    Parameters:
    - title (str): The title of the movie to search for. Partial matches are supported.
    - page (int): The page number of the search results to retrieve. Defaults to 1. Must be >= 1.
    - page_size (int): The number of search results to return per page. Defaults to 20. Must be >= 1.

    Returns:
    - A list of movies that match the search criteria, with pagination applied. Each movie is represented as a dictionary of details.
    """

    offset = (page - 1) * page_size 

    try:

        resources = search_movie_by_title(title, page_size, offset)
        if not resources:
            return []
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/favorites")
async def add_favorite_resource(background_tasks: BackgroundTasks, newFavorite: NewFavorite) -> NewFavorite:
    """
    Adds a new favorite movie for a user and triggers background generation of new movie recommendations.

    Parameters:
    - background_tasks (BackgroundTasks): FastAPI's background tasks for asynchronous operations.
    - newFavorite (NewFavorite): The new favorite movie information, including its ID and the user's email.

    Returns:
    - NewFavorite: The added favorite movie information if successful.

    Raises:
    - HTTPException: If the operation fails, returning a 400 status code with a detailed error message.
    """

    success = add_favorite_movie(newFavorite.movie_id, newFavorite.email)
    
    if success:
        background_tasks.add_task(generate_movies_recommendations, newFavorite.email)
        return newFavorite
    else:
        raise HTTPException(status_code=400, detail="Failed to add the movies to favorites")

      
      
@app.delete("/favorites")
async def delete_favorite_resource(background_tasks: BackgroundTasks, username: str = Query(default=""), domain: str = Query(default="gmail"), movie_id: int = Query()):
    """
    Removes a movie from a user's favorites based on the movie ID and updates their recommendations.

    Parameters:
    - background_tasks (BackgroundTasks): FastAPI's mechanism for executing functions in the background.
    - username (str): The username part of the user's email.
    - domain (str): The domain part of the user's email, defaults to "gmail".
    - movie_id (int): The unique identifier of the movie to be removed from favorites.

    Returns:
    - dict: A message indicating the outcome of the operation.

    Raises:
    - HTTPException: If the operation to remove the favorite fails.
    """
    email = f"{username}@{domain}"
    
    success = delete_favorite_movie(movie_id, email)
    
    if success:
        background_tasks.add_task(generate_movies_recommendations, email)
        return {"detail": "Successfully deleted the movie from favorites"}
    else:
        raise HTTPException(status_code=400, detail="Failed to delete the movie from favorites")

@app.delete("/reset_favorites")
async def reset_user_favorites_and_recommendations(username: str = Query(default=""), domain: str = Query(default="gmail")) -> dict:
    """
    Deletes all favorite movies and recommendations for a user, identified by their email address.

    Parameters:
    - username (str): The username part of the user's email.
    - domain (str): The domain part of the user's email, defaults to "gmail".

    Returns:
    - dict: A message indicating the outcome of the operation.

    Raises:
    - HTTPException: If the operation to reset the user's favorites and recommendations fails.
    """
    email = f"{username}@{domain}"

    success_favorites = delete_all_favorite_movies_by_email(email)
    
    if success_favorites:
        success_recommendations = delete_all_movies_recommendations_by_email(email)
        if success_recommendations:
            return {"detail": "Successfully deleted the user's favorites and recommendations"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete the user's recommendations")
    else:
        raise HTTPException(status_code=400, detail="Failed to delete the user's favorites")
    
      
@app.get("/favorites")
async def read_favorite_movies(username: str = Query(default=""), domain: str = Query(default="gmail")):
    """
    Retrieves all favorite movies for a user based on their email address.

    Parameters:
    - username (str): The username part of the user's email.
    - domain (str): The domain part of the user's email.

    Returns:
    - A list of Movie models representing the user's favorite movies.
    """
    email = f"{username}@{domain}"
        
    movies = get_all_favorites_movies_by_email(email)
    
    if not movies:
        raise HTTPException(status_code=404, detail=f"No favorite movies found for {email}.")
    return movies


# @app.get("/debugging")
# async def read_favorite_resources(email:str = Query(default=" ")):
#     resources = delete_favorite_movie(4918, email)
#     return resources
