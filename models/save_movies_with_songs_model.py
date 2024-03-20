from dotenv import load_dotenv
import os
from utils.utils import *
from models.similar_movies_recommender import SimilarMoviesRecommenders
import pandas as pd
import joblib

# Loading environment variables
load_dotenv()

# Google Cloud Platform project details
GCP_PROJECT = os.getenv('GCP_PROJECT')
GCP_MOVIES_DATASET =  os.getenv('GCP_MOVIES_DATASET')
GCP_MOVIES_USERS_INTERESTS_TABLE =  os.getenv('GCP_MOVIES_USERS_INTERESTS_TABLE')
GCP_MOVIES_WITH_SOUNDTRACKS_PREPROCESSED_TABLE = os.getenv('GCP_MOVIES_WITH_SOUNDTRACKS_PREPROCESSED_TABLE')

if __name__ == "__main__":
    
    # Getting data
    favorite_movies_ids = [1, 2]
    
    # Summarizing user
    prep_fav_movies = get_preprocessed_resources_by_id(GCP_PROJECT,GCP_MOVIES_DATASET,GCP_MOVIES_WITH_SOUNDTRACKS_PREPROCESSED_TABLE,favorite_movies_ids)    
    
    # Train data
    X = get_table(GCP_PROJECT, GCP_MOVIES_DATASET, GCP_MOVIES_WITH_SOUNDTRACKS_PREPROCESSED_TABLE)

    # Getting similar users
    recommender = SimilarMoviesRecommenders()
    recommender.fit(X)

    # Assuming `knn_model` is your fitted KNN model
    recommender_filename = 'models/similar_movies_recommender.pkl'

    # Save the model
    joblib.dump(recommender, recommender_filename)     