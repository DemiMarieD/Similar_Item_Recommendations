import pandas as pd
import tmdbsimple as tmdb
import json
from pathlib import Path
import nltk
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from requests import HTTPError
import pickle

from RecommendationApp.strategies import demi
from RecommendationApp.strategies import eda
from RecommendationApp.strategies.sebastian import Image_Based_Recommender


# ***************** Global VARs ************************
serialized_movie_data_path = 'RecommendationApp/data/serialized/serialized_movie_data.obj'
movie_data = {}
tmdb.API_KEY = '1fe2d017037a1445b9122ea2dcd42d41'
nltk.download('punkt')
nltk.download('stopwords')

# ***************** DATA IMPORTs ************************

# NOTE: I think the extracted_content_dict has ALL except the rating and users details
#       ! (it does contain the avg rating + count),
#       if we need more details we could add the rating to the dict and make a new dict for the users ?!
#       But I think we might not even need it.


# Loads a serialized object
def load_serialized_movie_data(path):
    with open(path, 'rb') as serialized_file:
        serialized_movie_data : dict = pickle.load(serialized_file)
    for key, value in serialized_movie_data.items():
        movie_data[key] = value


# Dumps a an object as serialized file
def serialize_movie_data_file(path, data):
    with open(path, 'wb') as serialized_file:
        pickle.dump(data, serialized_file, pickle.HIGHEST_PROTOCOL)


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

    counter = 0
    for key, value in big_movie_dict.items():
        print("Current movie id: " + str(key))
        # each movies has a dict
        movie_data[key] = {}

        # disclamer: not all the movies contain tmdb information in ectracted_content files e.g. 1107

        # ---------- general information
        movie_data[key]['movielensId'] = value['movielensId']
        movie_data[key]['tmdbMovieId'] = value['movielens']['tmdbMovieId']
        movie_data[key]['title'] = value['movielens']['title']
        movie_data[key]['genres'] = value['movielens']['genres']
        movie_data[key]['actors'] = value['movielens']['actors']
        movie_data[key]['directors'] = value['movielens']['directors']
        movie_data[key]['releaseYear'] = value['movielens']['releaseYear']

        if 'imdb' in value:
            movie_data[key]['productionCompanies'] = value['imdb']['productionCompanies']
            movie_data[key]['color'] = value['imdb']['color']
        else:
            movie_data[key]['productionCompanies'] = None
            movie_data[key]['color'] = None

        if 'tmdb' in value:
            movie_data[key]['adult'] = value['tmdb']['adult']
        else:
            movie_data[key]['adult'] = None


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
            movie_data[key]['similar'] = value['tmdb']['similar']
            movie_data[key]['overview'] = value['tmdb']['overview']
        else:
            movie_data[key]['keywords'] = None
            movie_data[key]['recommendations'] = None
            movie_data[key]['overview'] = None

        # Use the summaries to create a list of words / tokens to compare

        movie_data[key]['summaries'] = value['imdb']['summaries']
        plotSummary = value['movielens']['plotSummary']
        movie_data[key]['plotSummary'] = plotSummary
        # !!! This takes a few min !!!
        if plotSummary is not None:
            movie_data[key]['wordsOfSum'] = clean_string(plotSummary)
        else:
            movie_data[key]['wordsOfSum'] = None
        # !!! This takes a few min !!!
        if plotSummary is not None:
            sum_word_list = []
            stemmer = nltk.PorterStemmer()
            text_tokens = word_tokenize(plotSummary)
            for token in text_tokens:
                if token not in stopwords.words('english'):
                    sum_word_list.append(stemmer.stem(token))
            movie_data[key]['word_list'] = sum_word_list
        else:
            movie_data[key]['word_list'] = None

        # ---------------
        # todo add additional needed data!

        # Add poster paths for image-based recommendations
        try:
            tmdbMovie = tmdb.Movies(value['movielens']['tmdbMovieId'])
            tmdbMovie.info()
            if tmdbMovie.poster_path != None:
                movie_data[key]['poster'] = "https://image.tmdb.org/t/p/w342" + tmdbMovie.poster_path
            else:
                movie_data[key]['poster'] = None
        except HTTPError:
            print("Poster could not be requested from API for movie id: " + str(value['movielens']['tmdbMovieId']))
            movie_data[key]['poster'] = None

        # -------------- Status
        counter = counter + 1
        print("Setup done: " + str(round((counter / len(big_movie_dict)) * 100, 2)) + "%")

def clean_string(text):
    text = ''.join([word for word in text if word not in string.punctuation])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in stopwords.words('english')])
    return text

# ***********************************************************

def setup():
    # todo try to set up most things, train algo etc.
    if Path(serialized_movie_data_path).is_file():
        # Serialized object exists, load it instead of creating it from scratch
        load_serialized_movie_data(serialized_movie_data_path)
    else:
        # check what data we need and prepare just that
        create_movie_data_dict()
        serialize_movie_data_file(serialized_movie_data_path, movie_data)
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
        if movie_data[movie]['poster'] != None:
            movies_dict[movie]['poster_path'] = movie_data[movie]['poster']

        # todo add other movie details we need to displaying

    return movies_dict


def getTop5s(movie_id):

    resultDict = {} # key = Method Name, value = dict of similar movies and details

    # ------------ Method Zero, One  - to eval ------------
    # Method Zero ------------
    top5_method0 = demi.using_tmdb_similarity(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method0 != None:
        method0_movies = getMovieDetails(top5_method0)
        resultDict['Based on tmdb_similarity'] = method0_movies.items()
    else:
        resultDict['Based on tmdb_similarity'] = None  # will show a info text that the method did not work

    # Method One ------------
    top5_method1 = demi.using_tmdb_recommendations(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method1 != None:
        method1_movies = getMovieDetails(top5_method1)
        resultDict['Based on tmdb_recommendations'] = method1_movies.items()
    else:
        resultDict['Based on tmdb_recommendations'] = None  # will show a info text that the method did not work

    # ------------ Method Two , Three a) / b)  - content-based ------------

    # Method Two ------------ DOESNT WORK A COUPLE OF TIMES (NO KEYWORD OVERLAPS)
    top5_method2 = demi.using_keywords(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method2 != None:
        method2_movies = getMovieDetails(top5_method2)
        resultDict['Based on keywords'] = method2_movies.items()
    else:
        resultDict['Based on keywords'] = None  # will show a info text that the method did not work

    # Method Three ------------ IS NOT SO GOOD
    top5_method3 = demi.using_content_analysis(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method3 != None:
        method3_movies = getMovieDetails(top5_method3)
        resultDict['Based on Plot Summary'] = method3_movies.items()
    else:
        resultDict['Based on Plot Summary'] = None  # will show a info text that the method did not work

    # todo alternative to three


    # ------------ Method Four ------------ LOW DISCOVERY BECAUSE OF USING POPULATION FOR RANKING
    top5_method4 = demi.using_genre(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method4 != None:
        method4_movies = getMovieDetails(top5_method4)
        resultDict['Based on Genre'] = method4_movies.items()
    else:
        resultDict['Based on Genre'] = None  # will show a info text that the method did not work
        
    # ------------ Method Five ------------ DOESN'T WORK FOR SOME MOVIES(NO SAME TITLE)
    top5_method5 = eda.using_title(movie_data, movie_id)
    if top5_method5 != None:
        method5_movies = getMovieDetails(top5_method5)
        resultDict['Based on Title'] = method5_movies.items()
    else:
        resultDict['Based on Title'] = None

    # ------------ Method Six, Seven, Eight - image-based ------------
    image_based_recommender = Image_Based_Recommender(movie_data)
    # Brightness
    top5_method6 = image_based_recommender.using_poster_brightness(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method6 != None:
        method6_movies = getMovieDetails(top5_method6)
        resultDict['Based on Poster Brightness'] = method6_movies.items()
    else:
        resultDict['Based on Poster Brightness'] = None  # will show a info text that the method did not work

    # Contrast
    top5_method7 = image_based_recommender.using_poster_contrast(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method7 != None:
        method7_movies = getMovieDetails(top5_method7)
        resultDict['Based on Poster Contrast'] = method7_movies.items()
    else:
        resultDict['Based on Poster Contrast'] = None  # will show a info text that the method did not work

    # Colour
    top5_method8 = image_based_recommender.using_poster_colour_histogram(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method8 != None:
        method8_movies = getMovieDetails(top5_method8)
        resultDict['Based on Poster Colour Histogram'] = method8_movies.items()
    else:
        resultDict['Based on Poster Colour Histogram'] = None  # will show a info text that the method did not work


    # --------------- Method 9 - complex method-------
    top5_method9 = demi.complex_method(movie_data, movie_id)  # returns list of (5) movie id's
    if top5_method9 != None:
        method9_movies = getMovieDetails(top5_method9)
        resultDict['Based on Multiple Factors'] = method9_movies.items()
    else:
        resultDict['Based on Multiple Factors'] = None  # will show a info text that the method did not work


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
