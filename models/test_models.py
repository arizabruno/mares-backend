from dotenv import load_dotenv
import os
from utils.utils import *
import pandas as pd
import joblib

# Loading environment variables
load_dotenv()

# Google Cloud Platform project details
GCP_PROJECT = os.getenv('GCP_PROJECT')
GCP_MOVIES_DATASET = os.getenv('GCP_MOVIES_DATASET')
GCP_MOVIES_PREPROCESSED_TABLE =  os.getenv('GCP_MOVIES_PREPROCESSED_TABLE')
GCP_MOVIES_RATINGS_TABLE = os.getenv('GCP_MOVIES_RATINGS_TABLE')
GCP_MOVIES_DETAILS_TABLE = os.getenv('GCP_MOVIES_DETAILS_TABLE')
# Load the model at startup
model_filename = 'models/movies_similar_users_recommender.pkl'

try:
    model = joblib.load(model_filename)
except FileNotFoundError:
    print(f"Model file not found: {model_filename}. Please check the file path.")
    raise SystemExit


if __name__ == "__main__":
    
    # Getting data
    favorite_movies_ids = [109487]
    
    # Summarizing user
    prep_fav_movies = get_preprocessed_resources_by_id(GCP_PROJECT, GCP_MOVIES_DATASET, GCP_MOVIES_PREPROCESSED_TABLE, favorite_movies_ids)
    user_interest = get_user_interest_df(prep_fav_movies)

    movies_model_filename = 'models/movies_similar_users_recommender.pkl'
    model = joblib.load(movies_model_filename)

    similar_users = model.recommend_similar_users(user_interest)
        
    # Getting similar users favorite movies
    movies_ids_recommendations = get_good_rated_resources_by_users_ids(GCP_PROJECT, GCP_MOVIES_DATASET, GCP_MOVIES_RATINGS_TABLE, similar_users)
    
    favorites_ids_set = set(favorite_movies_ids)
    recommendations_ids_set = set(movies_ids_recommendations)
    final_recommendation_ids = list(recommendations_ids_set - favorites_ids_set)
    
    # Getting movies by id
    movies_recommendation = get_resources_from_ids(GCP_PROJECT, GCP_MOVIES_DATASET, GCP_MOVIES_DETAILS_TABLE, final_recommendation_ids)
    
    for m in movies_recommendation[:20]:
        print(m["title"])
    
    