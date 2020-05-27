from django import forms

from RecommendationApp.old_operations import checkUserId

class user_id_form(forms.Form):
    movie_id = forms.CharField(label="Movie Id")



class search_form(forms.Form):
    search_text = forms.CharField(label="",
                                  widget=forms.TextInput(attrs={'placeholder':'Movie title',
                                                                'style': 'border-radius: 3px; padding: 5px; width: 35%'}))

