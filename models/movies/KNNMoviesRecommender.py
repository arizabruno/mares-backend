from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import numpy as np

class KNNMovieRecommender:
    def __init__(self, n_neighbors: int = 5, algorithm: str = 'brute', metric: str = 'cosine') -> None:
        """
        Initializes a KNNMovieRecommender object with a K-Nearest Neighbors model and a TF-IDF vectorizer.

        Parameters:
        - n_neighbors (int): Number of neighbors to use for kneighbors queries. Default is 5.
        - algorithm (str): Algorithm used to compute the nearest neighbors. Can be 'ball_tree', 'kd_tree', 'brute', or 'auto'. Default is 'brute'.
        - metric (str): Metric used for the distance computation. Default is 'cosine'.

        Attributes:
        - model (NearestNeighbors): The K-Nearest Neighbors model.
        - tfidf_vectorizer (TfidfVectorizer): The TF-IDF vectorizer for text processing.
        - movie_ids (np.ndarray): Array of movie IDs.
        - tfidf_matrix (csr_matrix): Sparse matrix from TF-IDF vectorization.
        """
        self.n_neighbors = n_neighbors
        self.algorithm = algorithm
        self.metric = metric
        self.model = NearestNeighbors(n_neighbors=self.n_neighbors,
                                      algorithm=self.algorithm,
                                      metric=self.metric)
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.movie_ids = None
        self.tfidf_matrix = None

    def fit(self, movie_ids: np.ndarray, titles: np.ndarray, genres: np.ndarray) -> None:
        """
        Fits the KNN model and TF-IDF vectorizer using the movie genres.

        Parameters:
        - movie_ids (np.ndarray): Array of movie IDs.
        - titles (np.ndarray): Array of movie titles. This parameter is currently not used in the method but included for future enhancements.
        - genres (np.ndarray): Array of movie genres used for fitting the TF-IDF vectorizer and the KNN model.

        Returns:
        None
        """
        self.movie_ids = movie_ids
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(genres)
        self.model.fit(self.tfidf_matrix)

    def recommend_for_favorites_by_id(self, favorite_movie_ids: np.ndarray, n_recommendations: int = 5) -> np.ndarray:
        """
        Recommends movies based on a list of favorite movie IDs, using the genres to find similar movies.

        Parameters:
        - favorite_movie_ids (np.ndarray): Array of favorite movie IDs for which recommendations are to be generated.
        - n_recommendations (int): Number of recommendations to return. Default is 5.

        Returns:
        - np.ndarray: Array of recommended movie IDs, based on the input favorites.

        Raises:
        - ValueError: If none of the favorite movie IDs are found in the dataset.
        """
        favorite_indices = np.where(np.isin(self.movie_ids, favorite_movie_ids))[0]

        if favorite_indices.size == 0:
            raise ValueError("None of the favorite movie IDs were found in the dataset.")

        favorite_tfidf = csr_matrix(self.tfidf_matrix[favorite_indices].mean(axis=0))
        distances, indices = self.model.kneighbors(favorite_tfidf, n_neighbors=n_recommendations + len(favorite_indices))

        recommendations_indices = [i for i in indices[0] if i not in favorite_indices][:n_recommendations]
        recommendations = self.movie_ids[recommendations_indices]
        
        return recommendations
