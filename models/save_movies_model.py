from dotenv import load_dotenv
import os
from utils.utils import *
from models.similar_users_recommender import SimilarUsersRecommenders
import pandas as pd
import joblib

# Loading environment variables
load_dotenv()

# Google Cloud Platform project details
GCP_PROJECT = os.getenv('GCP_PROJECT')
GCP_MOVIES_DATASET =  os.getenv('GCP_MOVIES_DATASET')
GCP_MOVIES_PREPROCESSED_TABLE =  os.getenv('GCP_MOVIES_PREPROCESSED_TABLE')
GCP_MOVIES_USERS_INTERESTS_TABLE =  os.getenv('GCP_MOVIES_USERS_INTERESTS_TABLE')

if __name__ == "__main__":
    
    # Getting data
    favorite_movies_ids = [1, 2]
    
    # Summarizing user
    prep_fav_movies = get_preprocessed_resources_by_id(GCP_PROJECT,GCP_MOVIES_DATASET,GCP_MOVIES_PREPROCESSED_TABLE,favorite_movies_ids)
    user_interest = get_user_interest_df(prep_fav_movies)
    
        
    # Getting training data
    all_users_interests = get_users_interests(GCP_PROJECT,GCP_MOVIES_DATASET,GCP_MOVIES_USERS_INTERESTS_TABLE)
    
    # Getting similar users
    recommender = SimilarUsersRecommenders()
    recommender.fit(all_users_interests)

    # Assuming `knn_model` is your fitted KNN model
    recommender_filename = 'models/movies_similar_users_recommender.pkl'

    # Save the model
    joblib.dump(recommender, recommender_filename)     