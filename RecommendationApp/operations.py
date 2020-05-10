import pandas as pd
import tmdbsimple as tmdb
from RecommendationApp.strategies import demi
from RecommendationApp.strategies import eda
from RecommendationApp.strategies import sebastian

tmdb.API_KEY = '1fe2d017037a1445b9122ea2dcd42d41'


movies = pd.read_table("RecommendationApp/data/ml-1m/movies.dat", "::", engine="python", names=['MovieID', 'Title', 'Genres'])
ratings = pd.read_table("RecommendationApp/data/ml-1m/ratings.dat", "::", engine="python",
                        names=['UserID', 'MovieID', 'Rating', 'Timestamp'])
users = pd.read_table("RecommendationApp/data/ml-1m/users.dat", "::", engine="python",
                      names=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-Code'])
metadata = pd.read_csv(filepath_or_buffer="RecommendationApp/data/movies_metadata.csv", delimiter=",")

# merge all to one -> then make sample and use only this table
data_right = pd.merge(ratings, movies, on='MovieID')
data = pd.merge(users, data_right, on='UserID')
data = data[['UserID', 'MovieID', 'Title', 'Rating', 'Genres']]
# todo add all other information given (metadata)
movie_list = list(data["MovieID"].unique())


def setup():
    # todo try to set up most things, train algo etc.
    pass

def getMovieOptions(movie_title):
    # todo get a list of movies with similar titles
    pass

def getTop5s(movie_id):
    # todo get >5 list of the 5 most similar movies
    # call >5 different functions & combine results in dictionary
     top5_1 = demi.method(data, id)
     top5_2 = eda.method(data, id)
     top5_3 = sebastian.method(data, id)

    # top5_4 = method(id)
    # top5_5 = method(id)



##### possible methods see Notes