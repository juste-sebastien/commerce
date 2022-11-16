from django import forms

from .models import *


class CreateListingsForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ["title", "description", "image", "category", "duration", "price"]


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["price"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["title", "content"]


class CategoryForm(forms.Form):
    select = forms.ChoiceField(choices=Auction.CATEGORY_CHOICES)
    select.widget.attrs.update({"class": "form-select form-select-lg mb-3"})