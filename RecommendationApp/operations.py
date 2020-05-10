import pandas as pd
import tmdbsimple as tmdb
import json
from pathlib import Path
from RecommendationApp.strategies import demi
from RecommendationApp.strategies import eda
from RecommendationApp.strategies import sebastian

tmdb.API_KEY = '1fe2d017037a1445b9122ea2dcd42d41'

# ***************** DATA IMPORTs ************************
movies = pd.read_table("data/ml-1m/movies.dat", "::", engine="python",
                       names=['MovieID', 'Title', 'Genres'])
ratings = pd.read_table("data/ml-1m/ratings.dat", "::", engine="python",
                        names=['UserID', 'MovieID', 'Rating', 'Timestamp'])
users = pd.read_table("data/ml-1m/users.dat", "::", engine="python",
                      names=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-Code'])

# merge all to one -> then make sample and use only this table
data_right = pd.merge(ratings, movies, on='MovieID')
data = pd.merge(users, data_right, on='UserID')
data = data[['UserID', 'MovieID', 'Title', 'Rating', 'Genres']]

metadata = pd.read_csv(filepath_or_buffer="data/movies_metadata.csv", delimiter=",")

extracted_content_dict = {}
pathlist = Path("data/extracted_content_ml-latest/").glob('**/*.json')
for path in pathlist:
    path_in_str = str(path)
    print(path_in_str)
    f_input = open(path_in_str, 'r', encoding="utf8")
    content_dict = json.load(f_input)
    movielensId = content_dict['movielensId']
    extracted_content_dict[movielensId] = content_dict


# tmdb_dict = extracted_content_dict[<movieID>]['tmdb']
# imdb_dict = extracted_content_dict[<movieID>]['imdb']
# movielensId = extracted_content_dict[<movieID>]['movielensId']
# movielens_dict = extracted_content_dict[<movieID>]['movielens']
# cast_listOfDict = tmdb_dict['credits']['cast']
# crew_listOfDict = tmdb_dict['credits']['crew']
# genres_listOfDict = tmdb_dict['genres']
# ..... for more look at the .json

# ***********************************************************


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