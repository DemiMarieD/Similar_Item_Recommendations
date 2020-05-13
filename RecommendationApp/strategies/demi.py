import pandas as pd
import tmdbsimple as tmdb
import json
from pathlib import Path


def method(data, movie_id):
    pass

def using_tmdb_recommendations(data, movie_id):
    try:
        tmdb_recommendations = data[movie_id]['recommendations']  # list of tmdb ids
        recommened_movies = []  # list of tuple: id, avgRating
        for key, value in data.items():
            movielense_id = key
            if value['tmdbMovieId'] in tmdb_recommendations:
                recommened_movies.append((movielense_id, value['avgRating']))

        # get top 5
        sorted_by_avgRating = sorted(recommened_movies, key=lambda tup: tup[1], reverse=True)

        if len(sorted_by_avgRating) > 5:
            sorted_by_avgRating = sorted_by_avgRating[:5]

        similar_movies = []  # only movielenseID
        for tuple in sorted_by_avgRating:
            similar_movies.append(tuple[0])

        return similar_movies

    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))
        return None


# ****** FOR TESTING ********

# Data we need for display
def getMovieData():
    big_movie_dict = {}
    pathlist = Path("../data/extracted_content_ml-latest/").glob('**/*.json')
    for path in pathlist:
        path_in_str = str(path)
        # print(path_in_str)
        f_input = open(path_in_str, 'r', encoding="utf8")
        content_dict = json.load(f_input)
        movielensId = content_dict['movielensId']
        big_movie_dict[movielensId] = content_dict

    movie_data = {}

    for key, value in big_movie_dict.items():
        # each movies has a dict
        movie_data[key] = {}

        # disclamer: not all the movies contain tmdb information in ectracted_content files e.g. 1107
        # ---------- general information
        movie_data[key]['movielensId'] = value['movielensId']
        movie_data[key]['tmdbMovieId'] = value['movielens']['tmdbMovieId']
        movie_data[key]['title'] = value['movielens']['title']
        if 'tmdb' in value:
            movie_data[key]['poster_path'] = value['tmdb']['poster_path']
        else:
            movie_data[key]['poster_path'] = None

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
            movie_data[key]['keywords'] = value['tmdb']['keywords']
            movie_data[key]['recommendations'] = value['tmdb']['recommendations']
            movie_data[key]['overview'] = value['tmdb']['overview']
        else:
            movie_data[key]['keywords'] = None
            movie_data[key]['recommendations'] = None
            movie_data[key]['overview'] = None

        movie_data[key]['summaries'] = value['imdb']['summaries']
        movie_data[key]['plotSummary'] = value['movielens']['plotSummary']

        #todo add additional needed data!

    return movie_data


def main():
    movieID = input("Please enter movie ID: ")
    movie_data = getMovieData()
    using_tmdb_recommendations(movie_data, int(movieID))
    #method(data, userID)


if __name__ == '__main__':
    main()

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
