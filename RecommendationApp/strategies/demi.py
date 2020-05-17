from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

def using_genre(data, movie_id):
    reference_genres = data[movie_id]['genres']  # list of string
    recommended_movies = []  # list of tuple: id, avgRating
    for m_id, value in data.items():
        if m_id != movie_id:
            genres = data[m_id]['genres']
            if genres is not None:
                intersection_set = set.intersection(set(reference_genres), set(genres))

                # if more then half of the keywords overlap
                if len(intersection_set) > len(reference_genres)/2:  # I get very low results in overlap
                    # print("overlap " + str(len(intersection_set)))
                    recommended_movies.append((m_id, value['popularity']))    # using popularity here (might not work for every movie e.g. 1170

    result = get_top_5(recommended_movies)
    return result

def using_content_analysis(data, movie_id):
    try:
        #overview = data[movie_id]['overview']   # by tmdb
        #summaries = data[movie_id]['summaries']  # list of strings by imdb
        #reference_words = data[movie_id]['word_list']

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
    sorted_list = sorted(relevant_movies, key=lambda tup: tup[1], reverse=True)

    if len(sorted_list) > 5:
        sorted_list = sorted_list[:5]

    similar_movies = []  # value:  title
    for tuple in sorted_list:
        similar_movies.append(int(tuple[0]))

    return similar_movies