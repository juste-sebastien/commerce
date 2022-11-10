from django import forms

from .models import Auction

class CreateListingsForm(forms.ModelForm):

    class Meta:
        model = Auction
        fields = ["title", "description", "image", "category", "duration", "price"]