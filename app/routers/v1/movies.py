from typing import Annotated, List
from fastapi import BackgroundTasks, Depends, APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from app.auth.logic import get_current_user
from app.schemas.user import *
from app.schemas.movie import *
from app.data_access.queries import *
from dotenv import load_dotenv
import os
from app.data_access.queries import *
from app.utils.utils import get_user_interest_df
import joblib

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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


@router.get("/")
async def main():
    """
    Redirects to the API documentation page.

    Returns:
    - RedirectResponse: Redirects the client to the API documentation.
    """
    return RedirectResponse(url="/docs")


@router.get("/movies_recommendation")
async def recommend_resources(token: Annotated[str, Depends(oauth2_scheme)], username: str = Query(default=""), domain: str = Query(default="gmail")) -> list:
    """
    Endpoint to generate and fetch movie recommendations for a user based on their email.
    Constructs the user's email from the provided username and domain, then fetches a list of random movie recommendations.

    Parameters:
    - token (Annotated[str, Depends(oauth2_scheme)]): The JWT token to validate.
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

@router.get("/search_movies")
async def search_resources(token: Annotated[str, Depends(oauth2_scheme)], title: str = Query(default=""), page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1)) -> list:
    """
    Searches for movies by their title with pagination support.

    Parameters:
    - token (Annotated[str, Depends(oauth2_scheme)]): The JWT token to validate.
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



@router.post("/favorite_movies")
async def add_favorite_resource(token: Annotated[str, Depends(oauth2_scheme)], background_tasks: BackgroundTasks, newFavorite: NewFavorite) -> NewFavorite:
    """
    Adds a new favorite movie for a user and triggers background generation of new movie recommendations.

    Parameters:
    - token (Annotated[str, Depends(oauth2_scheme)]): The JWT token to validate.
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

      
      
@router.delete("/favorite_movies")
async def delete_favorite_resource(token: Annotated[str, Depends(oauth2_scheme)], background_tasks: BackgroundTasks, username: str = Query(default=""), domain: str = Query(default="gmail"), movie_id: int = Query()):
    """
    Removes a movie from a user's favorites based on the movie ID and updates their recommendations.

    Parameters:
    - token (Annotated[str, Depends(oauth2_scheme)]): The JWT token to validate.
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

@router.delete("/reset_favorite_movies")
async def reset_user_favorites_and_recommendations(token: Annotated[str, Depends(oauth2_scheme)], username: str = Query(default=""), domain: str = Query(default="gmail")) -> dict:
    """
    Deletes all favorite movies and recommendations for a user, identified by their email address.

    Parameters:
    - token (Annotated[str, Depends(oauth2_scheme)]): The JWT token to validate.
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
    
      
@router.get("/favorite_movies")
async def read_favorite_movies(token: Annotated[str, Depends(oauth2_scheme)], username: str = Query(default=""), domain: str = Query(default="gmail"), title: str = Query(default=""), page_size: int = Query(default=20, ge=1),  page: int = Query(default=1, ge=1)):
    """
    Retrieves all favorite movies for a user based on their email address.

    Parameters:
    - username (str): The username part of the user's email.
    - domain (str): The domain part of the user's email.

    Returns:
    - A list of Movie models representing the user's favorite movies.
    
    Raises:
    - HTTPException: If the operation fails.
    """
    email = f"{username}@{domain}"
    offset = (page - 1) * page_size 

    movies = get_all_favorites_movies_by_email(email, title, page_size, offset)
    
    if not movies:
        raise HTTPException(status_code=404, detail=f"No favorite movies found for {email}.")
    return movies


@router.post("/users/", response_description="Create a new user", response_model=UserCreate)
async def create_user_endpoint(user: UserCreate):
    """
    Create a new user with email, username, full name, and hashed password.
    """
    result = create_user(user.email, user.username, user.password)
    if not result:
        raise HTTPException(status_code=400, detail="User could not be created.")
    return user

@router.get("/users/", response_description="Read all users")
async def read_all_users_endpoint():
    """
    Read and return all users.
    """
    users = read_all_users()
    if users is None:
        raise HTTPException(status_code=404, detail="No users found.")
    return users

    