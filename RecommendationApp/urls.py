"""Similar_Item_Recommendations URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from RecommendationApp import views

urlpatterns = [
    path('', views.index),
    # netflix example layout
    path('netflix/', views.netflix),
    # welcome page - search movie title
    path('welcome/', views.welcome_view),
    # second page - display top5 most similar movies to the movie chosen
    path('welcome/<int:id>/', views.recommendation_view, name='recommendaitions'),
    path('search/<str:movie_title>/', views.movie_selection, name='movie_selection'),
]
