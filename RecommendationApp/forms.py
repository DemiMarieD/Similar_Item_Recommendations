from django import forms

from RecommendationApp.old_operations import checkUserId

class user_id_form(forms.Form):
    movie_id = forms.CharField(label="Movie Id")

   # def is_valid(self):
   #     try:
   #         int(self.data["movie_id"])
   #         if checkUserId(self.data["movie_id"]):
   #             return super().is_valid()
   #         else:
   #             self.add_error('movie_id', 'Movie Id not found')
   #             return False
   #     except:
   #         self.add_error('movie_id', 'Movie Id needs to be a number')
   #         return False
#