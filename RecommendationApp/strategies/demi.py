
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

        similar_movies = {}  # value:  title
        for tuple in sorted_by_avgRating:
            similar_movie_id = int(tuple[0])
            similar_movies[similar_movie_id] = {}
            similar_movies[similar_movie_id]['title'] = data[similar_movie_id]['title']

        print(similar_movies)
        return similar_movies

    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))
        return None
    except TypeError as e:
        print('I got a TypeError - reason "%s"' % str(e))
        return None

