from pandas import np
import numpy as np

def levenshtein_ratio_and_distance(s, t, ratio_calc = False):

    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)


    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,
                                 distance[row][col-1] + 1,
                                 distance[row-1][col-1] + cost)
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return Ratio
    else:

        return None

# This method recommend movies based on similar title and genres
def using_title(data, movie_id):
    try:
        reference_title = data[movie_id]['title']
        reference_genres = data[movie_id]['genres']
        recommened_movies = []  # list of tuple: id, avgRating
        for m_id, value in data.items():
            if m_id != movie_id:
                title = data[m_id]['title']
                genres = data[m_id]['genres']
                if title is not None and genres is not None:
                    genre_intersection = set.intersection(set(reference_genres), set(genres))
                    if len(genre_intersection) > 0:
                        Distance_title = levenshtein_ratio_and_distance(reference_title, title, ratio_calc=True)
                        recommened_movies.append((m_id, Distance_title))

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
