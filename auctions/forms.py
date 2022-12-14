from django import forms

from .models import *


class CreateListingsForm(forms.ModelForm):
    """
    A class used to represent a form for create a new listing based on its model

    ...

    Attributes
    ----------

    Methods
    -------

    """
    class Meta:
        model = Auction
        fields = ["title", "description", "image", "category", "duration", "price"]
        labels = {
            "title": "Title of the Auction",
            "description": "Description",
            "image": "Image",
            "category": "Category",
            "duration": "Duration",
            "price": "Start Price"
        }
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-label form-control",
                "style": "margin-bottom: 10px;"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-label form-control",
                "style": "margin-bottom: 10px;"
            }),
            "image": forms.URLInput(attrs={
                "class": "form-label form-control",
                "style": "margin-bottom: 10px;"
            }),
            "category": forms.Select(attrs={
                "class": "form-label form-control",
                "style": "margin-bottom: 10px;"
            }),
            "duration": forms.Select(attrs={
                "class": "form-label form-control",
                "style": "margin-bottom: 10px;"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-label form-control",
                "style": "margin-bottom: 10px;"
            })
        }


class BidForm(forms.ModelForm):
    """
    A class used to represent a form to add a bid to an auction based on its model

    ...

    Attributes
    ----------

    Methods
    -------

    """
    class Meta:
        model = Bid
        fields = ["price"]
        labels = {
            "price": "Bid's amount"
        }
        widgets = {
            "price": forms.NumberInput(attrs={
                "class": "form-control col-md-8",
                "style": "margin-bottom: 10px;"
            })
        }


class CommentForm(forms.ModelForm):
    """
    A class used to represent a form to add a comment to an auction based on its model

    ...

    Attributes
    ----------

    Methods
    -------

    """
    class Meta:
        model = Comment
        fields = ["title", "content"]
        labels = {
            "title": "Title of your Comment",
            "content": "Your Comment"
        }
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-control",
                "style": "margin-bottom: 10px;"
            }),
            "title": forms.TextInput(attrs={
                "class": "form-label form-control",
                "style": "margin-bottom: 10px;"
            })
        }


class CategoryForm(forms.Form):
    """
    A class used to represent a form for create a new listing based on its model

    ...

    Attributes
    ----------
    select: Field
        A ChoiceField for choosing the category of an auction

    Methods
    -------

    """
    select = forms.ChoiceField(choices=Auction.CATEGORY_CHOICES)
    select.widget.attrs.update({"class": "form-select form-select-lg mb-3"})