from sklearn.neighbors import NearestNeighbors

class SimilarMoviesRecommenders:
    def __init__(self) -> None:
        self.model = NearestNeighbors()

    def fit(self, movies_prep) -> None:
        self.movies_prep = movies_prep
        X = self.movies_prep.drop(columns=["id_","title"])
        self.model.fit(X)

    def recommend_similar_movies(self, user_interests_df, k = 5):
        
        distances, indices = self.model.kneighbors(user_interests_df, n_neighbors=k)
        similar_movies = self.movies_prep.loc[indices[0]].id_.tolist()
        
        return similar_movies
