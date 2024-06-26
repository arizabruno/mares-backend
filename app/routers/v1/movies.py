from typing import Annotated
from fastapi import BackgroundTasks, Depends, APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from app.auth.logic import get_current_user
from app.schemas.token import TokenData
from app.schemas.user import *
from app.schemas.movie import *
from app.data_access.queries import *
from dotenv import load_dotenv
import os
from app.data_access.queries import *
from app.utils.utils import get_user_interest_df
import joblib
from jose import JWTError, jwt

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Model Loading
movies_model_filename = 'models/movies_similar_users_recommender.pkl'

try:
    movies_model = joblib.load(movies_model_filename)
except Exception as e:
    print(f"Model file not found: {movies_model_filename}. Please check the file path.")
    raise SystemExit


def generate_movies_recommendations(user_id: int):
    """
    Generates and updates movie recommendations for a user based on their favorite movies.

    Parameters:
    - user_id (int): The id of the user, used to identify their list of favorite movies.

    Raises:
    - HTTPException: If there's an error in fetching the favorites, if the favorites list is too short,
                     or if there's an error during the recommendation process.
    """
    try:
        # Retrieve favorite movies for the user
        resources = get_all_favorites_movies_by_user(user_id)

        if resources == None:
            return []

        favorite_resources_ids = [m['movie_id'] for m in resources]


        # Check if there are enough favorite movies to generate recommendations
        if len(favorite_resources_ids) < 1:
            reset_movies_recommendations(user_id)
            return []

        # Preprocess favorite movies to summarize user interests
        prep_fav_resources = get_preprocessed_movies_by_ids(favorite_resources_ids)
        df = pd.DataFrame(prep_fav_resources)
        user_interest = get_user_interest_df(df)

        # Use model to find similar users
        ks_attempts = [5,10,15,20,25,30,35,40,45,50]

        good_rated_movies = []

        MINIMUM_RECOMMENDATIONS = 20

        for k in ks_attempts:
            similar_users = movies_model.recommend_similar_users(user_interest, k)

            # Get recommendations from similar users' good-rated movies

            recs = get_good_rated_movies_by_user_ids(similar_users)

            if(len(recs) >= MINIMUM_RECOMMENDATIONS):
                good_rated_movies = recs
                break

        if not good_rated_movies or len(good_rated_movies) < MINIMUM_RECOMMENDATIONS:
            reset_movies_recommendations(user_id)
            return []

        movies_ids_recommendations = [m['movie_id'] for m in good_rated_movies]

        # Filter out already favorite movies
        favorites_ids_set = set(favorite_resources_ids)
        recommendations_ids_set = set(movies_ids_recommendations)
        final_recommendation_ids = list(recommendations_ids_set - favorites_ids_set)

        # Limit the number of recommendations
        MAX_RECS = 30
        if len(final_recommendation_ids) > MAX_RECS:
            final_recommendation_ids = final_recommendation_ids[:MAX_RECS]

        # Update user recommendations
        update_movies_recommendations(final_recommendation_ids, user_id)

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail="An error occurred during the recommendation process.")

@router.get("/recommendation", response_model=List[MovieDetails])
async def recommend_resources(current_user: Annotated[UserInfo, Depends(get_current_user)]) -> list:
    """
    Endpoint to generate and fetch movie recommendations for a user based on their id.

    Parameters:
    - current_user (Annotated[str, Depends(get_current_user)]): The current user extracted from the request JWT.

    Returns:
    - A list of dictionaries, each representing a movie recommendation with details fetched from the database.
    """
    current_user = UserInfo(**current_user)
    generate_movies_recommendations(current_user.user_id)

    try:
        recs = get_all_movies_recommendation(current_user.user_id)
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[MovieDetails])
async def search_resources(current_user: Annotated[UserInfo, Depends(get_current_user)], title: str = Query(default=""), page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1)) -> list:
    """
    Searches for movies by their title with pagination support.

    Parameters:
    - current_user (Annotated[str, Depends(get_current_user)]): The current user extracted from the request JWT.
    - title (str): The title of the movie to search for. Partial matches are supported.
    - page (int): The page number of the search results to retrieve. Defaults to 1. Must be >= 1.
    - page_size (int): The number of search results to return per page. Defaults to 20. Must be >= 1.

    Returns:
    - A list of movies that match the search criteria, with pagination applied. Each movie is represented as a dictionary of details.
    """
    current_user = UserInfo(**current_user)
    offset = (page - 1) * page_size

    try:
        title = title.strip() if title.isspace() else title
        resources = search_movie_by_title(current_user.user_id, title, page_size, offset)
        if not resources:
            return []
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/favorite", response_model=bool)
async def add_favorite_resource(current_user: Annotated[UserInfo, Depends(get_current_user)], background_tasks: BackgroundTasks, movie_id: int) -> NewFavorite:
    """
    Adds a new favorite movie for a user and triggers background generation of new movie recommendations.

    Parameters:
    - current_user (Annotated[str, Depends(get_current_user)]): The current user extracted from the request JWT.
    - background_tasks (BackgroundTasks): FastAPI's background tasks for asynchronous operations.
    - movie_id (int): The movie_id of the new favorite movie.

    Returns:
    - bool: The outcome of the operation

    Raises:
    - HTTPException: If the operation fails, returning a 400 status code with a detailed error message.
    """

    current_user = UserInfo(**current_user)
    success = add_favorite_movie(movie_id, current_user.user_id)

    if success:
        # background_tasks.add_task(generate_movies_recommendations, current_user.user_id)
        return True
    else:
        raise HTTPException(status_code=400, detail="Failed to add the movies to favorites")

@router.delete("/favorite", response_model=bool)
async def delete_favorite_resource(current_user: Annotated[UserInfo, Depends(get_current_user)],  background_tasks: BackgroundTasks, movie_id: int = Query()):
    """
    Removes a movie from a user's favorites based on the movie ID and updates their recommendations.

    Parameters:
    - current_user (Annotated[str, Depends(get_current_user)]): The current user extracted from the request JWT.
    - background_tasks (BackgroundTasks): FastAPI's mechanism for executing functions in the background.
    - movie_id (int): The unique identifier of the movie to be removed from favorites.

    Returns:
    - bool: The outcome of the operation

    Raises:
    - HTTPException: If the operation to remove the favorite fails.
    """

    current_user = UserInfo(**current_user)
    success = delete_favorite_movie(movie_id, current_user.user_id)

    if success:
        # background_tasks.add_task(generate_movies_recommendations, current_user.user_id)
        return True
    else:
        raise HTTPException(status_code=400, detail="Failed to delete the movie from favorites")

@router.delete("/reset_favorite", response_model=bool)
async def reset_user_favorites_and_recommendations(current_user: Annotated[UserInfo, Depends(get_current_user)]) -> dict:
    """
    Deletes all favorite movies and recommendations for a user, identified by their id.

    Parameters:
    - current_user (Annotated[str, Depends(get_current_user)]): The current user extracted from the request JWT.

    Returns:
    - bool: The outcome of the operation

    Raises:
    - HTTPException: If the operation to reset the user's favorites and recommendations fails.
    """

    current_user = UserInfo(**current_user)
    success_favorites = delete_all_favorite_movies(current_user.user_id)

    if success_favorites:
        success_recommendations = delete_all_movies_recommendations(current_user.user_id)
        if success_recommendations:
            return True
        else:
            raise HTTPException(status_code=400, detail="Failed to delete the user's recommendations")
    else:
        raise HTTPException(status_code=400, detail="Failed to delete the user's favorites")

@router.get("/favorite", response_model=List[MovieDetails])
async def read_favorite_movies(current_user: Annotated[UserInfo, Depends(get_current_user)], title: str = Query(default=""), page_size: int = Query(default=20, ge=1),  page: int = Query(default=1, ge=1)):
    """
    Retrieves all favorite movies for a user based on their id.

    Parameters:
    - current_user (Annotated[str, Depends(get_current_user)]): The current user extracted from the request JWT.


    Returns:
    - A list of Movie models representing the user's favorite movies.

    Raises:
    - HTTPException: If the operation fails.
    """
    current_user = UserInfo(**current_user)

    offset = (page - 1) * page_size

    title = title.strip() if title.isspace() else title

    movies = get_all_favorites_movies_by_user(current_user.user_id, title, page_size, offset)

    return movies


# Get movies soundtracks from table movies_soundtracks based on movie id
@router.get("/favorite_movies_soundtracks/", response_model=List[SongFromMovie])
async def get_movie_soundtracks(current_user: Annotated[UserInfo, Depends(get_current_user)]):
    """
    Retrieves all soundtracks songs from the user favorite movies

    Parameters:
    - current_user (Annotated[str, Depends(get_current_user)]): The current user extracted from the request JWT.

    Returns:
    - A list of SongFromMovie models representing the soundtracks for the movies.

    Raises:
    - HTTPException: If the operation fails.
    """

    current_user = UserInfo(**current_user)
    soundtracks = get_songs_from_favorite_movies(current_user.user_id)

    return soundtracks
