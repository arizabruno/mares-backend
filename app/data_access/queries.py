from app.auth.password import get_password_hash
from app.data_access.db_connection import Database
from datetime import datetime, timedelta
import pytz
import pandas as pd



def execute_query(query, params=None, fetch="all", commit=False):
    """
    Executes a given SQL query with optional parameters and manages the database connection.
    Returns the results as a list of dictionaries after transforming them into a pandas DataFrame,
    with column names corresponding to the SQL table columns.

    Parameters:
    - query (str): The SQL query to execute.
    - params (tuple|dict|None): Optional parameters to pass with the query. Default is None.
                                If provided, it should be a tuple or dict of parameters you wish to bind to the query.
    - fetch (str): Determines how the results are fetched post-query execution. Default is "all".
                   Acceptable values are:
                   - "all": Fetches all rows of a query result, returns a list of dictionaries.
                   - "one": Fetches the first row of a query result, returns a list containing a single dictionary.
    - commit (bool): Specifies whether to commit the transaction. Default is False.
                     If True, the changes made by the query will be committed to the database.

    Returns:
    - On successful execution and fetch="all" or fetch="one", returns a list of dictionaries representing the fetched rows.
    - On successful execution with commit=True, returns True.
    - If an exception occurs during query execution, prints the error and returns None.
    """
    connection = Database.get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if fetch == "one" and commit:
                connection.commit()
                rows = [cursor.fetchone()]
                if not rows or rows[0] is None:  # Check if no data was fetched or fetchone() found no rows
                    return []  # Return an empty list
                col_names = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=col_names)
                return df.to_dict('records')
            if commit:
                connection.commit()
                return True
            if fetch in ("all", "one"):
                rows = cursor.fetchall() if fetch == "all" else [cursor.fetchone()]
                if not rows or rows[0] is None:  # Check if no data was fetched or fetchone() found no rows
                    return []  # Return an empty list
                col_names = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=col_names)
                return df.to_dict('records')  # Convert DataFrame to list of dicts
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        Database.return_connection(connection)


def search_movie_by_title(user_id: int | None = None, title: str = "", page_size: int = 20, offset: int = 0) -> list:
    """
    Searches for movies by title in the database, using a case-insensitive search pattern, excluding movies
    that are already marked as favorites by the specified user.

    Parameters:
    - user_id (int): The user ID for whom to exclude favorite movies.
    - title (str): The search term for the movie title. The function searches for any titles that contain this term,
                   regardless of case.
    - page_size (int): The maximum number of movie records to return in one response. Default is 20.
                       This parameter controls the 'LIMIT' clause in the SQL query.
    - offset (int): The offset from the start of the result set to begin returning records. Default is 0.
                    This parameter controls the 'OFFSET' clause in the SQL query and is used for pagination.

    Returns:
    - list: A list of tuples representing the movie records that match the search criteria. Each tuple contains
            the complete details of a movie as stored in the `movies_details` table.
            The function returns an empty list if no matches are found or in case of an error.
    """

    if user_id is None:
        query = "SELECT DISTINCT * FROM movies_details WHERE LOWER(title) LIKE LOWER(%s) LIMIT %s OFFSET %s;"
        params = (f'%{title}%', page_size, offset)
    else:
        query = """
        SELECT DISTINCT md.* FROM movies_details md
        LEFT JOIN movies_favorites mf ON md.movie_id = mf.movie_id AND mf.user_id = %s
        WHERE LOWER(md.title) LIKE LOWER(%s) AND mf.movie_id IS NULL
        ORDER BY md.movie_id ASC
        LIMIT %s OFFSET %s;
        """
        params = (user_id, f'%{title}%', page_size, offset)

    return execute_query(query, params=params)



def add_favorite_movie(movie_id: int, user_id: int):
    """
    Adds a movie to a user's list of favorite movies in the database, if it's not already in the list.

    Parameters:
    - movie_id (int): The unique identifier of the movie to add to the user's favorites.
    - user_id (int): The id of the user, used to identify their list of favorite movies.

    Returns:
    - True if the transaction was committed successfully, indicating that the movie was added to the favorites.
    - None if an error occurred during the query execution or if the movie is already in the user's list of favorites.
    """

    query = """
    INSERT INTO movies_favorites (movie_id, user_id, created_at)
    SELECT %s, %s, CURRENT_TIMESTAMP
    WHERE NOT EXISTS (
        SELECT 1 FROM movies_favorites WHERE movie_id = %s AND user_id = %s
    );
    """

    params = (movie_id, user_id, movie_id, user_id)

    return execute_query(query, params=params, commit=True)


def delete_favorite_movie(movie_id: int, user_id: int):
    """
    Removes a movie from a user's list of favorite movies in the database.

    Parameters:
    - movie_id (int): The unique identifier of the movie to be removed from the user's favorites.
    - user_id (int): The id of the user, used to identify their list of favorite movies.


    Returns:
    - True if the transaction was committed successfully, indicating that the movie was removed from the favorites.
    - None if an error occurred during the query execution. This can happen if the SQL operation fails for any reason,
      such as database connection issues or syntax errors in the query.
    """

    query = """
    DELETE FROM movies_favorites WHERE movie_id = %s AND user_id = %s;
    """

    params = (movie_id, user_id)

    return execute_query(query, params=params, commit=True)


def get_all_favorites_movies_by_user(user_id:int, title: str = "", page_size: int = 10, offset: int = 0):
    """
    Retrieves detailed information about all favorite movies for a specified user by id.

    Parameters:
    - user_id (int): The id of the user, used to identify their list of favorite movies.


    Returns:
    - list: A list of tuples representing the detailed information of each favorite movie. Each tuple corresponds
                to a row in the 'movies_details' table for a movie that is a favorite of the user.
                The function returns an empty list if the user has no favorite movies or in case of an error.

    """

    query = """
    SELECT m.*
    FROM movies_favorites as f
    INNER JOIN movies_details as m ON m.movie_id = f.movie_id
    WHERE f.user_id = %s AND LOWER(title) LIKE LOWER(%s)
    LIMIT %s OFFSET %s;
    """

    title = f'%{title}%'
    params = (user_id, title, page_size, offset)

    return execute_query(query, params, commit=False)


def delete_all_favorite_movies(user_id: int):
    """
    Deletes all favorite movies for a specific user identified by their id

    Parameters:
    - user_id (int): The id of the user, used to identify their list of favorite movies.

    Returns:
    - The result of the `execute_query` function, which could be True if the operation was successful and the transaction was committed, or None if an error occurred.
    """

    query = """
    DELETE FROM movies_favorites WHERE user_id = %s;
    """

    params = (user_id,)

    return execute_query(query, params=params, commit=True)


def get_preprocessed_movies_by_ids(ids: list[int]) -> list:
    """
    Retrieves movies from the 'movies_preprocessed' table by a list of movie IDs.

    Parameters:
    - ids (list[int]): A list of integer IDs corresponding to movies to retrieve.

    Returns:
    - list: A list of tuples representing the retrieved movie records. Each tuple contains
            all columns from the 'movies_preprocessed' table for each movie that matches the IDs in the given list.
            Returns an empty list if no movies are found or in case of an error.
    """

    placeholders = ', '.join(['%s'] * len(ids))

    query = f"SELECT DISTINCT * FROM movies_preprocessed WHERE movie_id IN ({placeholders})"

    params = tuple(ids)

    return execute_query(query, params=params, commit=False)


def get_all_users_interests() -> list:
    """
    Retrieves all entries from the 'movies_users_interests' table.

    Returns:
    - list: A list of tuples, where each tuple represents a row from the 'movies_users_interests' table,
            containing all the data for each entry. Returns an empty list if the table is empty or in case of an error.
    """

    query = f"SELECT * from movies_users_interests;"

    return execute_query(query, commit=False)


def get_good_rated_movies_by_user_ids(ids: list[int]) -> list:
    """
    Retrieves IDs of movies rated higher than 4.0 by a specific list of users.

    Parameters:
    - ids (list[int]): A list of user IDs to filter the movies by their ratings.

    Returns:
    - list: A list of integers representing the IDs of movies with ratings higher than 4.0 by the specified users.
            Returns an empty list if no movies meet the criteria or in case of an error.
    """
    # Generate a list of placeholders for the query based on the number of user IDs
    placeholders = ', '.join(['%s'] * len(ids))

    # Construct the SQL query
    query = f"SELECT DISTINCT movie_id FROM movies_ratings WHERE user_id IN ({placeholders}) and rating >= 4.0"

    # Execute the query with the list of user IDs
    params = tuple(ids)

    return execute_query(query, params=params, commit=False)

def get_all_movies_recommendation(user_id: int) -> list:
    """
    Get all movies recommendations for a user.

    Parameters:
    - user_id (int): The user ID for whom to exclude favorite movies.

    Returns:
    - list: A list of tuples representing the movie records.
    """

    query = """
    SELECT DISTINCT * FROM (
        SELECT m.*
        FROM movies_recommendations AS r
        INNER JOIN movies_details AS m ON r.movie_id = m.movie_id
        WHERE r.user_id = %s
        ORDER BY RANDOM()
        LIMIT 50
    ) AS subquery
    ORDER BY title ASC;
    """
    params = (user_id,)

    return execute_query(query, params=params)

def reset_movies_recommendations(user_id: int):
    """
    Deletes all movie recommendations for a specific user identified by their id.

    Parameters:
    - user_id (int): The id of the user, used to identify their list of favorite movies.

    Returns:
    - The result of the `execute_query` function, which could be True if the operation was successful and the transaction was committed, or None if an error occurred.
    """

    query = """
    DELETE FROM movies_recommendations WHERE user_id = %s;
    """

    params = (user_id,)

    return execute_query(query, params=params, commit=True)


def update_movies_recommendations(ids: list[int], user_id: int) -> bool:
    """
    Updates the movie recommendations for a user, identified by id, if the last update was more than a specified time ago.

    The function clears the user's current movie recommendations and sets new ones based on the provided movie IDs.
    It first checks if the last recommendation update was more than 1 minute ago to prevent too frequent updates.

    Parameters:
    - ids (list[int]): A list of movie IDs to be set as the new recommendations for the user.
    - user_id (int): The id of the user, used to identify their list of favorite movies.

    Returns:
    - bool: True if the recommendations were successfully updated, False otherwise (e.g., if the update was attempted too soon after the last one).
    """

    # Check for the last recommendation time
    # last_recommended_query = """
    # SELECT MAX(created_at) as last_timestamp
    # FROM movies_recommendations
    # WHERE user_id = %s;
    # """
    # params = (user_id,)
    # last_timestamp_result = execute_query(last_recommended_query, params=params, fetch="one")
    # last_timestamp = last_timestamp_result[0]["last_timestamp"]
    # minimum_time_to_refresh = timedelta(minutes=1)
    # if last_timestamp:
    #     now = datetime.now(pytz.utc)
    #     last_timestamp = last_timestamp.replace(tzinfo=pytz.UTC)
    #     diff = (now - last_timestamp)
    #     if  diff <= minimum_time_to_refresh:
    #         print("Last recommendation was made less than 1 minute ago.")
    #         return False

    # Reset current recommendations
    reset_movies_recommendations(user_id)
    values_placeholders = ", ".join(["(%s, %s, CURRENT_TIMESTAMP)"] * len(ids))
    add_query = f"INSERT INTO movies_recommendations (movie_id, user_id, created_at) VALUES {values_placeholders};"
    params = tuple(val for pair in zip(ids, [user_id] * len(ids)) for val in pair)


    return execute_query(add_query, params=params, commit=True)


def get_random_movies_recommendations_from_user(user_id: int):
    """
    Fetches a random list of 10 movie recommendations for a specific user by their id.

    Parameters:
    - user_id (int): The id of the user, used to identify their list of favorite movies.


    Returns:
    - list: A list of tuples, where each tuple represents the detailed information of a recommended movie.
            Returns an empty list if no recommendations are found or in case of an error.
    """

    query = """
    SELECT * FROM (
        SELECT DISTINCT m.*
        FROM movies_recommendations AS r
        INNER JOIN movies_details AS m ON r.movie_id = m.movie_id
        WHERE r.user_id = %s
    ) AS subquery
    ORDER BY RANDOM()
    LIMIT 10;
    """

    params = (user_id,)

    return execute_query(query, params=params, commit=False)


def delete_all_movies_recommendations(user_id: int):
    """
    Deletes all recommended movies for a specific user identified by their id.

    Parameters:
    - user_id (int): The id of the user, used to identify their list of favorite movies.

    Returns:
    - The result of the `execute_query` function, which could be True if the operation was successful and the transaction was committed, or None if an error occurred.
    """

    query = """
    DELETE FROM movies_recommendations WHERE user_id = %s;
    """

    params = (user_id,)

    return execute_query(query, params=params, commit=True)

def create_guest_user(username:str = 'guest', password:str = 'secret', email:str = 'guest@example.com'):
    """
    Adds a new guest user to the database.

    Returns:
        Union[dict, None]: The newly created user's data, or None if an error occurred.
    """
    hashed_password = get_password_hash(password)
    query = """
    INSERT INTO users (username, hashed_password, email, is_guest) VALUES (%s, %s, %s, true) RETURNING user_id, username, email, is_guest;
    """

    params = (username, hashed_password, email)
    return execute_query(query, params=params, fetch='one', commit=True)[0]

def create_user(email: str, username: str, password: str):
    """
    Adds a new user to the database with a hashed password.

    Args:
        username (str): The user's username.
        password (str): The user's plain text password, which will be hashed before storage.
        email (str): The user's email address.

    Returns:
        Union[dict, None]: The newly created user's data, or None if an error occurred.
    """
    hashed_password = get_password_hash(password)
    query = """
    INSERT INTO users (email, username, hashed_password) VALUES (%s, %s, %s)
    """
    params = (email, username, hashed_password)
    return execute_query(query, params=params, commit=True)


def read_all_users():
    """
    Fetches all users from the users table without exposing sensitive information like hashed passwords.

    Returns:
    - The result of the `execute_query` function, which is a list of dictionaries where each dictionary represents a user without their hashed password.
    """
    query = "SELECT user_id, email, username FROM users"
    return execute_query(query, fetch="all")


def read_user_by_id(user_id: int):
    """
    Fetches a single user from the users table by their ID.

    Parameters:
    - user_id (int): The ID of the user to fetch.

    Returns:
    - A list containing a single dictionary representing the user, or an empty list if no user was found. Sensitive information like hashed passwords is not included.
    """
    query = "SELECT user_id, email, username, is_guest FROM users WHERE user_id = %s"
    params = (user_id,)
    return execute_query(query, params=params, fetch="one")[0]


def update_user_info(user_id: int, new_email: str = None, new_username: str = None, new_password: str = None):
    """
    Updates the information of an existing user in the users table based on their ID.

    Parameters:
    - user_id (int): The ID of the user to update.
    - new_email (str, optional): The new email address to update.
    - new_username (str, optional): The new username to update.
    - new_passowrd (str, optional): The new password to update.
    Returns:
    - The result of the `execute_query` function, which could be True if the operation was successful and the transaction was committed, or None if an error occurred.
    """
    updates = []
    params = []

    if new_email:
        updates.append("email = %s")
        params.append(new_email)
    if new_username:
        updates.append("username = %s")
        params.append(new_username)
    if new_password:
        new_hashed_password = get_password_hash(new_password)
        updates.append("hashed_password = %s")
        params.append(new_hashed_password)


    if not updates:
        return None  # No updates to make

    updates.append("is_guest = %s")
    params.append(False)

    params.append(user_id)  # For the WHERE clause
    query = "UPDATE users SET " + ", ".join(updates) + " WHERE user_id = %s"

    return execute_query(query, params=params, commit=True)


def delete_user(user_id: int):
    """
    Deletes a user from the users table using their ID.

    Parameters:
    - user_id (int): The ID of the user to be deleted.

    Returns:
    - The result of the `execute_query` function, which could be True if the operation was successful and the transaction was committed, or None if an error occurred.
    """
    query = "DELETE FROM users WHERE user_id = %s"
    params = (user_id,)
    return execute_query(query, params=params, commit=True)


def read_user_by_username(username: str):
    """
    Fetches a single user from the users table by their username.

    Parameters:
    - username (str): The username of the user to fetch.

    Returns:
    - A list containing a single dictionary representing the user, or an empty list if no user was found. Sensitive information like hashed passwords is not included.
    """
    query = "SELECT user_id, email, username, hashed_password, is_guest FROM users WHERE username = %s"
    params = (username,)
    return execute_query(query, params=params, fetch="one")[0]

def read_user_by_email(email: str):
    """
    Fetches a single user from the users table by their email.

    Parameters:
    - email (str): The email of the user to fetch.

    Returns:
    - A list containing a single dictionary representing the user, or an empty list if no user was found. Sensitive information like hashed passwords is not included.
    """
    query = "SELECT user_id, email, username, hashed_password, is_guest FROM users WHERE email = %s"
    params = (email,)
    return execute_query(query, params=params, fetch="one")[0]

# get_songs_from_favorite_movies
def get_songs_from_favorite_movies(user_id: int):

    query = """
        SELECT songs.*, md.title, md.image_path as movie_image_path
        FROM movies_soundtracks as songs
        INNER JOIN movies_details md on songs.movie_id = md.movie_id
        INNER JOIN movies_favorites as favorites ON favorites.movie_id = songs.movie_id
        WHERE favorites.user_id = %s;
    """
    params = (user_id,)

    return execute_query(query, params, commit=False)
