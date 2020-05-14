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

    # make to recommendations_dict, key = method_name, value = dict of movies with their details
    similar_movies_dicts = getTop5s(id)
    context = {"similar_movies_dicts": similar_movies_dicts.items()}  # todo add reference movies

    return render(request, "similar_movies.html", context)
