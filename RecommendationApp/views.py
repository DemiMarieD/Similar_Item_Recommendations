from django.shortcuts import render, redirect
from RecommendationApp.forms import search_form
from RecommendationApp.operations import getTop5s
from RecommendationApp.operations import getMovieDetails
from RecommendationApp.operations import setup
from RecommendationApp.operations import getMovieOptions


def index(request):
    setup()
    return redirect('/welcome')


def netflix(request):
    return render(request, "netflix_temp.html")


def welcome_view(request):
    # create a form instance and populate it with data from the request:
    input_form = search_form(request.POST or None)
    movie_options = {}

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
       if input_form.is_valid():
            # process the data in form.cleaned_data as required
            search = input_form.cleaned_data["search_text"]
            movie_options = getMovieOptions(search)


    context = {"movies": movie_options, 'input_form': input_form}
    # if not post or not valid
    return render(request, "movie_selection.html", context)


def movie_selection(request, movie_title):
    movie_options = getMovieOptions(movie_title)
    context = {"movies": movie_options}
    return render(request, "movie_selection.html", context)


def recommendation_view(request, id):
    # make to recommendations_dict, key = method_name, value = dict of movies with their details
    similar_movies_dicts = getTop5s(id)
    context = {"similar_movies_dicts": similar_movies_dicts.items(), "reference_movie": getMovieDetails([id]).items()}

    return render(request, "similar_movies.html", context)
