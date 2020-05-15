import pandas as pd
import tmdbsimple as tmdb
import json
from pathlib import Path
from RecommendationApp.strategies import demi
from RecommendationApp.strategies import eda
from RecommendationApp.strategies import sebastian

# ***************** Global VARs ************************

tmdb.API_KEY = '1fe2d017037a1445b9122ea2dcd42d41'
movie_data = {}


# ***************** DATA IMPORTs ************************

# NOTE: I think the extracted_content_dict has ALL except the rating and users details
#       ! (it does contain the avg rating + count),
#       if we need more details we could add the rating to the dict and make a new dict for the users ?!
#       But I think we might not even need it.

# Data we need for display
def create_movie_data_dict():
    # global movie_data
    big_movie_dict = {}
    pathlist = Path("RecommendationApp/data/extracted_content_ml-latest/").glob('**/*.json')
    for path in pathlist:
        path_in_str = str(path)
        # print(path_in_str)
        f_input = open(path_in_str, 'r', encoding="utf8")
        content_dict = json.load(f_input)
        movielensId = content_dict['movielensId']
        big_movie_dict[movielensId] = content_dict

    for key, value in big_movie_dict.items():
        # each movies has a dict
        movie_data[key] = {}

        # disclamer: not all the movies contain tmdb information in ectracted_content files e.g. 1107

        # ---------- general information
        movie_data[key]['movielensId'] = value['movielensId']
        movie_data[key]['tmdbMovieId'] = value['movielens']['tmdbMovieId']
        movie_data[key]['title'] = value['movielens']['title']

        # ---------- to get popularity
        if 'tmdb' in value:
            movie_data[key]['popularity'] = value['tmdb']['popularity']
            movie_data[key]['tmdb_vote_average'] = value['tmdb']['vote_average']
            movie_data[key]['tmdb_vote_count'] = value['tmdb']['vote_count']
        else:
            movie_data[key]['popularity'] = None
            movie_data[key]['tmdb_vote_average'] = None
            movie_data[key]['tmdb_vote_count'] = None

        movie_data[key]['avgRating'] = value['movielens']['avgRating']
        movie_data[key]['numRatings'] = value['movielens']['numRatings']

        # ---------- content information for Demi
        if 'tmdb' in value:
            keyword_tuple_list = value['tmdb']['keywords']
            movie_data[key]['keywords'] = []
            for tuple in keyword_tuple_list:
                movie_data[key]['keywords'].append(tuple['name'])  # create a list of keyword names

            movie_data[key]['recommendations'] = value['tmdb']['recommendations']
            movie_data[key]['overview'] = value['tmdb']['overview']
        else:
            movie_data[key]['keywords'] = None
            movie_data[key]['recommendations'] = None
            movie_data[key]['overview'] = None

        movie_data[key]['summaries'] = value['imdb']['summaries']
        movie_data[key]['plotSummary'] = value['movielens']['plotSummary']

        # todo add additional needed data!


# ***********************************************************

def setup():
    # todo try to set up most things, train algo etc.
    # check what data we need and prepare just that
    create_movie_data_dict()
    print('Set up done')


def getMovieOptions(movie_title):
    # todo get a list of movies with similar titles
    pass


def getMovieDetails(movies_list):
    movies_dict = {}  # key movie_id, value dict of movie details
    for movie in movies_list:
        movies_dict[movie] = {}  # dict for movie details

        # Movie Title
        movies_dict[movie]['title'] = movie_data[movie]['title']
        movies_dict[movie]['plotSummary'] = movie_data[movie]['plotSummary']

        # Poster Path
        tmdbMovie = tmdb.Movies(movie_data[movie]['tmdbMovieId'])
        tmdbMovie.info()
        if tmdbMovie.poster_path != None:
            movies_dict[movie]['poster_path'] = "https://image.tmdb.org/t/p/w342" + tmdbMovie.poster_path

        # todo add other movie details we need to displaying

    return movies_dict


def getTop5s(movie_id):

    resultDict = {} # key = Method Name, value = dict of similar movies and details

    # ------------ Method One ------------
    top5_method1 = demi.using_tmdb_recommendations(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method1 != None:
        method1_movies = getMovieDetails(top5_method1)
        resultDict['Based on tmdb'] = method1_movies.items()
    else:
        resultDict['Based on tmdb'] = None  # will show a info text that the method did not work

    # ------------ Method Two ------------
    top5_method2 = demi.using_keywords(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method2 != None:
        method2_movies = getMovieDetails(top5_method2)
        resultDict['Based on keywords'] = method2_movies.items()
    else:
        resultDict['Based on keywords'] = None  # will show a info text that the method did not work

    # top5_2 = eda.method(data, id)
    # top5_3 = sebastian.method(data, id)

    return resultDict

# NOTES
# Movie Data
# dict[<movieId>]
#     dict['tmdb']
#         dict['title'] -> value: string
#         dict['poster_path'] -> value: string
#         dict['popularity'] -> value: int
#         dict['vote_average'] -> value: int
#         dict['vote_count'] -> value: int
#
#     dict['movielensId'] -> value: int
#
#     dict['movielens']
#         dict['tmdbMovieId'] -> value: int
#         dict['avgRating'] -> value: int
#         dict['numRatings'] -> value: int


# Relevant / Interesting Data for me
# dict[<movieId>]
#     dict['tmdb']
#         dict['keywords'] -> value: list of tuple name, id
#         dict['recommendations'] -> value: list of movieIds
#         dict['overview'] -> value: string
#
#     dict['imdb']
#         dict['synopsis'] -> value: string
#         dict['summaries'] -> value: list of strings
#
#     dict['movielensId'] -> value: int id
#
#     dict['movielens']
#         dict['plotSummary'] -> value: string == dict['imdb']['synopsis']
