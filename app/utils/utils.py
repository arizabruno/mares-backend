import pandas as pd

def get_user_interest_df(prep_resources):
    """
    Processes a DataFrame of user favorite resources to create a summary of user interests.

    Parameters:
    - prep_resources (pd.DataFrame): A DataFrame containing data on user's favorite resources,
                                     including 'movie_id' and 'title' columns among others representing different metrics or features.

    Returns:
    - pd.DataFrame: A single-row DataFrame summarizing the average value of each feature/metric column,
                    excluding 'movie_id' and 'title', with columns sorted alphabetically.
    """
    
    preproc_favorite_resources = prep_resources.drop(columns=["movie_id","title"])
    preproc_favorite_resources = preproc_favorite_resources[sorted(preproc_favorite_resources.columns)]
    user_summary = preproc_favorite_resources.mean().reset_index(drop=True)
    df = pd.DataFrame(user_summary).T
    df.columns = preproc_favorite_resources.columns
    
    return df


