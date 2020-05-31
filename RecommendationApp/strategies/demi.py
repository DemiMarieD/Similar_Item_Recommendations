from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer


def using_tmdb_similarity(data, movie_id):
    try:
        tmdb_recommendations = data[movie_id]['similar']  # list of tmdb ids
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



def using_genre(data, movie_id):
    reference_genres = data[movie_id]['genres']  # list of string
    recommended_movies = []  # list of tuple: id, avgRating
    for m_id, value in data.items():
        if m_id != movie_id:
            genres = data[m_id]['genres']
            if genres is not None:
                intersection_set = set.intersection(set(reference_genres), set(genres))

                # if more then half of the keywords overlap
                if len(intersection_set) == len(reference_genres):
                    # print("overlap " + str(len(intersection_set)))
                    popularity = value['popularity']
                    if popularity is not None:
                        recommended_movies.append((m_id, popularity))    # using popularity here (might not work for every movie e.g. 1170

    result = get_top_5(recommended_movies)
    return result


# ------------------------------ CONTENT RELATED

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



def using_content_analysis(data, movie_id):
    try:
        plotSummary = data[movie_id]['wordsOfSum']  # by movielense
        similarity_tupels = [] # key = movieID; value= sim
        for key, value in data.items():
            list_plots = []
            list_plots.append(plotSummary)
            if key != movie_id:
                summary = data[key]['wordsOfSum']
                if summary is not None:
                    list_plots.append(summary)
                    vectorizer = CountVectorizer().fit_transform(list_plots)
                    vectors = vectorizer.toarray()
                    ref_sum = vectors[0].reshape(1, -1)
                    this_sum = vectors[1].reshape(1, -1)
                    sim = cosine_similarity(ref_sum, this_sum)
                    if sim > 0:
                        similarity_tupels.append((key, sim[0][0]))

        return get_top_5(similarity_tupels)

    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))
        return None
    except TypeError as e:
        print('I got a TypeError - reason "%s"' % str(e))
        return None

# NOT USED ----
def using_content_token(data, movie_id):
    try:
        plot_tokens = data[movie_id]['word_list']
        similarity_tupels = [] # key = movieID; value= sim
        for key, value in data.items():
            pass
            # todo ?

        return get_top_5(similarity_tupels)

    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))
        return None
    except TypeError as e:
        print('I got a TypeError - reason "%s"' % str(e))
        return None



def get_top_5(relevant_movies):
    # get top 5
    sorted_list = sorted(relevant_movies, key=lambda tup: tup[1], reverse=True)
    if len(sorted_list) > 5:
        sorted_list = sorted_list[:5]

    similar_movies = []
    for tuple in sorted_list:
        similar_movies.append(int(tuple[0]))

    return similar_movies


# ----------------------------- SPECIAL METHOD

# A 'big' method
# color needs to be the same
# adult needs to be the same
# year needs to be +10 -5
# genre needs to overlap
# Production Comp / Actor / Director  needs to be one similar
# top 50 on avgRating
# top 5 on popularity
def complex_method(data, movie_id):
    try:
        reference_color = data[movie_id]['color']
        reference_adult = data[movie_id]['adult']  # boolean
        reference_year = int(data[movie_id]['releaseYear'])
        reference_actors = data[movie_id]['actors']  # list of string
        reference_directors = data[movie_id]['directors']  # list of string
        reference_production = data[movie_id]['productionCompanies']  # list of string
        reference_genres = data[movie_id]['genres']  # list of string

        relevant_movies = []  # list of id, points, avgRating, popularity
        for m_id, value in data.items():
            try:
                if m_id != movie_id:
                    color = value['color']
                    adult = value['adult']  # boolean
                    year = value['releaseYear']
                    actors = value['actors']  # list of string
                    directors = value['directors']  # list of string
                    production = value['productionCompanies']  # list of string
                    genres = value['genres']
                    if color == reference_color:
                        if adult == reference_adult:
                            if year != '' and reference_year-10 < int(year) < reference_year+10:
                                genre_intersection = set.intersection(set(reference_genres), set(genres))
                                if len(genre_intersection) > 0:
                                    points = 0
                                    if actors is not None and reference_actors is not None:
                                        actors_intersection = set.intersection(set(reference_actors), set(actors))
                                        if len(actors_intersection) > 0:
                                            points = points+1
                                    if directors is not None and reference_directors is not None:
                                        directors_intersection = set.intersection(set(reference_directors), set(directors))
                                        if len(directors_intersection) > 0:
                                            points = points+1
                                    if production is not None and reference_production is not None:
                                        production_intersection = set.intersection(set(reference_production), set(production))
                                        if len(production_intersection) > 0:
                                            points = points+1

                                    if points > 0:
                                        relevant_movies.append((m_id, points, value['avgRating'], value['popularity']))

            # if one value is None we catch and go to next movie
            except KeyError as e:
                print('I got a KeyError - reason "%s"' % str(e))

            except TypeError as e:
                print('I got a TypeError - reason "%s"' % str(e))


        # sort by points
        sorted_list = sorted(relevant_movies, key=lambda tup: tup[1], reverse=True)
        # get top 100
        if len(sorted_list) > 100:
            sorted_list = sorted_list[:100]

        # sort by avgRating
        sorted_list = sorted(sorted_list, key=lambda tup: tup[2], reverse=True)
        # get top 50
        if len(sorted_list) > 50:
            sorted_list = sorted_list[:50]

        # sort by popularity
        sorted_list = sorted(sorted_list, key=lambda tup: tup[3], reverse=True)
        # get top 5
        if len(sorted_list) > 5:
            sorted_list = sorted_list[:5]

        # get the id's
        similar_movies = []
        for tuple in sorted_list:
            similar_movies.append(int(tuple[0]))

        return similar_movies

    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))
        return None
    except TypeError as e:
        print('I got a TypeError - reason "%s"' % str(e))
        return None
