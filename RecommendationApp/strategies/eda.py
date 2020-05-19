from fuzzywuzzy import fuzz
def using_title(data, movie_id):
    try:
        reference_title = data[movie_id]['title']  
        recommened_movies = []  # list of tuple: id, avgRating
        for m_id, value in data.items():
            if m_id != movie_id:
                title = data[m_id]['title']
                if title is not None:
                    # takes out the common string
                    Ratio = fuzz.token_set_ratio(reference_title.lower(), title.lower())   # token set ratio compare strings that are widely differing lengths
                    if Ratio > 75: # percentage of ratio (higher value exclude movies that must be recommended)
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
