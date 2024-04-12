from sklearn.neighbors import NearestNeighbors

class SimilarUsersRecommenders:
    def __init__(self) -> None:
        self.model = NearestNeighbors()

    def fit(self, all_users_interests_df) -> None:
        self.all_users_interests_df = all_users_interests_df
        X = self.all_users_interests_df.drop(columns=["userId"])
        self.model.fit(X)

    def recommend_similar_users(self, user_interests_df, k = 5):

        distances, indices = self.model.kneighbors(user_interests_df, n_neighbors=k)
        similar_users = self.all_users_interests_df.loc[indices[0]].userId.tolist()

        return similar_users
