from django import forms

from RecommendationApp.old_operations import checkUserId

class user_id_form(forms.Form):
    user_id = forms.CharField(label="User Id")

    def is_valid(self):
        try:
            int(self.data["user_id"])
            if checkUserId(self.data["user_id"]):
                return super().is_valid()
            else:
                self.add_error('user_id', 'User Id not found')
                return False
        except:
            self.add_error('user_id', 'User Id needs to be a number')
            return False
