
def using_tmdb_recommendations(data, movie_id):
    try:
        tmdb_recommendations = data[movie_id]['recommendations']  # list of tmdb ids
        recommened_movies = []  # list of tuple: id, avgRating
        for key, value in data.items():
            movielense_id = key
            if value['tmdbMovieId'] in tmdb_recommendations:
                recommened_movies.append((movielense_id, value['avgRating']))

        return get_top_5(recommened_movies)

    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))
        return None
    except TypeError as e:
        print('I got a TypeError - reason "%s"' % str(e))
        return None


def using_keywords(data, movie_id):
    try:
        reference_keywords = data[movie_id]['keywords']  # list of string
        recommened_movies = []  # list of tuple: id, avgRating
        for m_id, value in data.items():
            if m_id != movie_id:
                keywords = data[m_id]['keywords']
                if keywords is not None:
                    intersection_set = set.intersection(set(reference_keywords), set(keywords))

                    # if more then half of the keywords overlap
                    if len(intersection_set) > 1:   # I get very low results in overlap
                        # print("overlap " + str(len(intersection_set)))
                        recommened_movies.append((m_id, value['avgRating']))

        result = get_top_5(recommened_movies)
        return result

    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))
        return None
    except TypeError as e:
        print('I got a TypeError - reason "%s"' % str(e))
        return None



def get_top_5(relevant_movies):
    # get top 5
    sorted_by_avgRating = sorted(relevant_movies, key=lambda tup: tup[1], reverse=True)

    if len(sorted_by_avgRating) > 5:
        sorted_by_avgRating = sorted_by_avgRating[:5]

    similar_movies = []  # value:  title
    for tuple in sorted_by_avgRating:
        similar_movies.append(int(tuple[0]))

    return similar_movies