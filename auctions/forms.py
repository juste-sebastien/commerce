from django import forms

from .models import Auction

class CreateListingsForm(forms.Form):
    title = forms.CharField(
        label="title", 
        max_length=64, 
        required=True,
    )
    description = forms.CharField(
        widget=forms.Textarea, 
        label="description", 
        max_length=500,
        required=False
    )
    image = forms.URLField(label="image", required=False)
    category = forms.ChoiceField(label="category", choices=Auction.CATEGORY_CHOICES, required=True)
    duration = forms.ChoiceField(label="duration", choices=Auction.DURATION_CHOICES, required=True)
    start_price = forms.DecimalField(
        label="start_price", 
        max_digits=12, 
        decimal_places=2,
        required=True,
    )