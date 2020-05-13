from django.shortcuts import render, redirect
from RecommendationApp.forms import user_id_form
from RecommendationApp.operations import getTop5s
from RecommendationApp.operations import setup

def index(request):
    # todo maybe add "Please wait we are preparing the side" where we do some set up ?!
    setup()  #not called here
    return redirect('/welcome')

def netflix(request):
    return render(request, "netflix_temp.html")

def welcome_view(request):
    # todo change: input from userId to movie title, doesnt need to match perfectly! (error message not needed!?)
    # create a form instance and populate it with data from the request:
    input_form = user_id_form(request.POST or None)

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
       if input_form.is_valid():
            # process the data in form.cleaned_data as required
            id = input_form.cleaned_data["movie_id"]
            # redirect to a new URL:
            return redirect('/welcome/' + id)

    # if not post or not valid
    return render(request, "welcome.html", {'input_form': input_form})


def movie_selection(request, movie_title):
    # todo do we need a second page or do we do this on the 'welcome' page?!
    # todo display movies that are connected to the movie_title
    movie_options = 0  # import operations.getMovieOptions(movie_title)
    return render(request, "movie_selection.html", movie_options)


def recommendation_view(request, id):
    # todo get list of top-5 most similar items, from at least 5 different functions
    # make to recommendations_dict, key = methodNumber, value = dict with method key
    recommendation_dict = getTop5s(id)
    method_one_dict = {}
    # this method might not have worked for every movie e.g. 1107
    if 1 in recommendation_dict:
        method_one_dict = recommendation_dict[1]
        # The dictionary contains entries with movie ids as keys
        # e.g. 1947: {'title': 'My Life in Pink', 'posterPath': 'https://image.tmdb.org/t/p/w342/f5bySDXIX09A3tbtTYHbXK1V0Nf.jpg'}
        # print(method_one_dict)

    context = {"similar_movies_1": method_one_dict.items()}
    return render(request, "similar_movies.html", context)
