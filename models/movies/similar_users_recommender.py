from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import numpy as np

class SimilarUsersRecommenders:
    def __init__(self, k: int = 5) -> None:

        self.k = k
        self.model = NearestNeighbors(n_neighbors=k)

    def fit(self, all_users_interests_df) -> None:
        self.all_users_interests_df = all_users_interests_df
        X = self.all_users_interests_df.drop(columns=["userId"])
        self.model.fit(X)

    def recommend_similar_users(self, user_interests_df):
        
        distances, indices = self.model.kneighbors(user_interests_df, n_neighbors=self.k)
        similar_users = self.all_users_interests_df.loc[indices[0]].userId.tolist()
        
        return similar_users
