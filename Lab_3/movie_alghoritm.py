import sys
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

def load_data():
    """Load CSV data into Pandas objects"""
    movies_df = pd.read_csv('movies.csv')
    users_df = pd.read_csv('users.csv')
    ratings_df = pd.read_csv('ratings.csv')
    return movies_df, users_df, ratings_df


def create_user_movie_matrix(ratings_df):
    """Create user-movie matrix.

    :param ratings_df: Pandas dataframe object, returned by load_data() function
    """
    ratings_matrix = ratings_df.pivot_table(index='user_id', columns='movie_id', values='rating').fillna(0)
    return ratings_matrix


def cluster_users(ratings_matrix, n_clusters=5):
    """Cluster users based on movie rating.

    :param ratings_matrix: ratings matrix returned by function create_user_movie_matrix
    :param n_clusters: number of clusters
    """
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    clusters = kmeans.fit_predict(ratings_matrix)
    ratings_matrix['cluster'] = clusters
    return ratings_matrix, clusters


def get_recommendations_for_user(user_id, ratings_df, movies_df, clustered_ratings_matrix, n_recommendations=5):
    """Find n-recommendations for a user.

    :param user_id: user id
    :param ratings_df: Pandas dataframe object, returned by load_data() function
    :param movies_df: Pandas dataframe object, returned by create_user_movie_matrix() function
    :param clustered_ratings_matrix: clustered ratings matrix
    :param n_recommendations: number of recommendations
    """
    user_cluster = clustered_ratings_matrix.loc[user_id, 'cluster']

    user_rated_movies = set(ratings_df[ratings_df['user_id'] == user_id]['movie_id'])
    cluster_users_ids = clustered_ratings_matrix[clustered_ratings_matrix['cluster'] == user_cluster].index
    cluster_movies = ratings_df[
        ratings_df['user_id'].isin(cluster_users_ids) & ~ratings_df['movie_id'].isin(user_rated_movies)]

    recommended_movies = cluster_movies.groupby('movie_id')['rating'].mean().sort_values(ascending=False).head(
        n_recommendations)
    recommended_movies_titles = movies_df[movies_df['movie_id'].isin(recommended_movies.index)]['title'].tolist()

    return recommended_movies_titles


movies_df, users_df, ratings_df = load_data()
ratings_matrix = create_user_movie_matrix(ratings_df)

n_clusters = 5
clustered_ratings_matrix, clusters = cluster_users(ratings_matrix, n_clusters)

user_id = sys.argv[1]
recommendations = get_recommendations_for_user(int(user_id), ratings_df, movies_df, clustered_ratings_matrix)
print(f"Rekomendowane filmy dla użytkownika {user_id}:", recommendations)
