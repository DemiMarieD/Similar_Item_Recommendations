from django.shortcuts import render, redirect
from RecommendationApp.forms import user_id_form
from RecommendationApp.old_operations import recommendations
from RecommendationApp.old_operations import enrichWithMetaData

def index(request):
    # todo maybe add "Please wait we are preparing the side" where we do some set up ?!
    # import operations.setup()
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
            id = input_form.cleaned_data["user_id"]
            # redirect to a new URL:
            return redirect('/welcome/' + id)

    # if not post or not valid
    return render(request, "welcome.html", {'input_form': input_form})

def movie_selection(request, movie_title):
    # todo do we need a second page or do we do this on the 'welcome' page?!
    # todo display movies that are connected to the movie_title
    movie_options = 0  # import operations.getMovieOptions(movie_title)
    return render(request, "movie_selection.html", movie_options)


def recommendation_view(request):
    # todo get list of top-5 most similar items, from at least 5 different functions
    # make to recommendations_dict, key = methodNumber, value = method call
    # import operations.getTop5s(id)
    # return render(request, "recommendations.html", recommendations_dict)

    # If you are using DataFrames keep in mind that Django needs a dictionary as the context  variable. 
    # So use the to_dict() function to convert it.
    recommendations_df = recommendations(id)
    recommendation_dict = enrichWithMetaData(recommendations_df)
    # print(recommendation_dict)
    # The dictionary contains entries with movie ids as keys
    # e.g. 1947: {'genres': ['Drama', 'Comedy'], 'title': 'My Life in Pink', 'posterPath': '/f5bySDXIX09A3tbtTYHbXK1V0Nf.jpg',
    # 'sysopsis': "Ludovic is a small boy who cross-dresses and generally acts like a girl, talks of marrying his neighbor's son
    # and can not understand why everyone is so surprised about it. His actions lead to problems for him and his family.",
    # 'releaseDate': '1956-07-14'}
    context = {"recommendations": recommendation_dict.items()}
    return render(request, "recommendations.html", context)
