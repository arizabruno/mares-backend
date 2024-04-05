from pydantic import BaseModel
from typing import List

class Favorites(BaseModel):
    """
    Schema representing a user's list of favorite movies.

    Attributes:
        ids (List[int]): A list of movie IDs that the user has marked as favorites. This allows for quick retrieval and management of a user's favorite movies.
    """
    ids: List[int]

class NewFavorite(BaseModel):
    """
    Schema for adding a new favorite movie to a user's list.

    Attributes:
        movie_id (int): The ID of the movie to be added to the user's list of favorites. This ensures that the movie can be uniquely identified within the system.
        email (str): The email address of the user adding the movie to their list of favorites. This links the action to a specific user account.
    """
    movie_id: int
    
    
class MovieDetails(BaseModel):
    movie_id: int
    title: str
    image_path: str
    year: int
    avg_rating: float
    rating_count: int
    genres: str
    summary: str
    duration: int
    popularity_score: float
    tmdb_id: int
    imdb_id: int