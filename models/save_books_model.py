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
GCP_BOOKS_DATASET =  os.getenv('GCP_BOOKS_DATASET')
GCP_BOOKS_PREPROCESSED_TABLE =  os.getenv('GCP_BOOKS_PREPROCESSED_TABLE')
GCP_BOOKS_USERS_INTERESTS_TABLE =  os.getenv('GCP_BOOKS_USERS_INTERESTS_TABLE')

if __name__ == "__main__":
    
    # Getting data
    favorite_books_ids = [1, 2]
    
    # Summarizing user
    prep_fav_books = get_preprocessed_resources_by_id(GCP_PROJECT,GCP_BOOKS_DATASET,GCP_BOOKS_PREPROCESSED_TABLE,favorite_books_ids)
    user_interest = get_user_interest_df(prep_fav_books)
    
        
    # Getting training data
    all_users_interests = get_users_interests(GCP_PROJECT,GCP_BOOKS_DATASET,GCP_BOOKS_USERS_INTERESTS_TABLE)
    
    # Getting similar users
    recommender = SimilarUsersRecommenders()
    recommender.fit(all_users_interests)

    # Assuming `knn_model` is your fitted KNN model
    recommender_filename = 'models/books_similar_users_recommender.pkl'

    # Save the model
    joblib.dump(recommender, recommender_filename)     