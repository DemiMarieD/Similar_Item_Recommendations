
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from ast import literal_eval
import tmdbsimple as tmdb

# ******* GLOBAL PARAMETERS *********** #
neighbor_size = 5
top_n = 10

tmdb.API_KEY = '1fe2d017037a1445b9122ea2dcd42d41'



movies = pd.read_table("RecommendationApp/data/ml-1m/movies.dat", "::", engine="python", names=['MovieID', 'Title', 'Genres'])
ratings = pd.read_table("RecommendationApp/data/ml-1m/ratings.dat", "::", engine="python",
                        names=['UserID', 'MovieID', 'Rating', 'Timestamp'])
users = pd.read_table("RecommendationApp/data/ml-1m/users.dat", "::", engine="python",
                      names=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-Code'])
metadata = pd.read_csv(filepath_or_buffer="RecommendationApp/data/movies_metadata.csv", delimiter=",")

# merge all to one -> then make sample and use only this table
data_right = pd.merge(ratings, movies, on='MovieID')
data = pd.merge(users, data_right, on='UserID')  # .sample(50000)  # todo adjust sample size
data = data[['UserID', 'MovieID', 'Title', 'Rating', 'Genres']]
# print(data.head(10))  # to see the user IDs i could try
data_grouped_byUser = data.groupby("UserID")
user_list = list(data["UserID"].unique())
movie_list = list(data["MovieID"].unique())

# Prepare training and test sets
data_copy = data.copy()
# 80% for training
# TODO: Is it necessary to split it here for our purpose?
#   We do not want to evaluate the prediction
train = data_copy.sample(frac=0.8)
test = data_copy.drop(train.index)
# print(train.describe())
# print(test.describe())
# Use UserIDs and MovieIDs as Features, Ratings as Classification
x_train = train[['UserID', 'MovieID']]
y_train = train[['Rating']]
x_test = test[['UserID', 'MovieID']]
y_test = test[['Rating']]
#
# knn = KNeighborsClassifier()
# knn.fit(x_train, y_train)
# KNeighborsClassifier(n_neighbors=neighbor_size)


# Can be used to check the predictions
# print(knn.predict(x_test.head(10)))
# print(y_test.head(10))

def checkUserId(userId):
    if int(userId) in user_list:
        return True
    else:
        return False


def recommendations(userID):
    # todo calculate top 20 recommendations for user
    # Use the UserId and all movies he has not rated as input
    userData = data_grouped_byUser.get_group(userID)
    ratedMoviesByUser = set(userData["MovieID"])
    # Retrieve all movies the user has not rated
    unratedMoviesByUser = set(movie_list) - ratedMoviesByUser

    # Input data will have the form [['UserID', 'MovieID'], ['UserID', 'MovieID'], ...]
    inputData = []
    for unratedMovie in unratedMoviesByUser:
        inputData.append([userID, unratedMovie])
    # Convert to DataFrame
    userMovieDf = pd.DataFrame(inputData, columns=['UserID', 'MovieID'])

    # TODO: Even if unrealistic, add check if the input is empty

    # Predict and append ratings to the input DataFrame. Now it has the form:
    # [['UserID', 'MovieID', 'Rating'], ['UserID', 'MovieID', 'Rating'], ...]
    # where 'Rating' is the predicted rating
    userMovieDf['Rating'] = knn.predict(userMovieDf)
    print(userMovieDf)

    sortedPredictions = userMovieDf.sort_values(by=['Rating'], ascending=False)

    # Take the top‐20 list of the ranked list
    if len(sortedPredictions) > 20:
        top_20_predictions = sortedPredictions[:20]
    else:
        top_20_predictions = sortedPredictions
    print(top_20_predictions)
    return top_20_predictions
    # The recommendations can be computed with your nearest‐neighbor algorithm or 
    # using some existing library that, e.g., implements a matrix factorization approach. 
    # For this  have a look at https://mc.ai/overview‐of‐matrix‐factorisation‐techniques‐using‐python‐2/ 


# Expects the DataFrame with predictions as input
# Form: [['UserID', 'MovieID', 'Rating'], ['UserID', 'MovieID', 'Rating'], ...]
# Returns a dictionary with needed metadata
def enrichWithMetaData(top_20_predictions):
    resultDict = {}
    for index, row in top_20_predictions.iterrows():
        movieId = row["MovieID"]
        metadataForMovie = metadata.iloc[index]
        # Extract the needed metadata
        # TODO: Add more if necessary
        # literal_eval()  is necessary to interprete the list as list. In the CSV everything is a string
        genres = literal_eval(metadataForMovie["genres"])
        genresList = list()
        for genre in genres:
            genresList.append(genre["name"])
        title = metadataForMovie["title"]
        synopsys = metadataForMovie["overview"]
        releaseDate = metadataForMovie["release_date"]
        # retrieve the poster path from tmdb api
        tmdbMovie = tmdb.Movies(metadataForMovie["imdb_id"])
        tmdbMovie.info()
        # TODO: This could be changed to retrieve the path via API
        # TODO: Adapt size if necessary
        posterPath = ""
        if tmdbMovie.poster_path != None:
            posterPath = "https://image.tmdb.org/t/p/w342" + tmdbMovie.poster_path
        # Get actors for movie (cast)
        tmdbMovie.credits()
        movieCast = list()
        for castMember in tmdbMovie.cast:
            movieCast.append(castMember["name"])

        # Add metadata to result dictionary, use movieId as key
        resultDict[movieId] = {"genres": genresList, "title": title, "posterPath": posterPath, "synopsis": synopsys, "releaseDate": releaseDate, "actors": movieCast}

    return resultDict
