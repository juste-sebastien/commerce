from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction
from .forms import CreateListingsForm

from datetime import datetime

def index(request):
    print(Auction.objects.all())
    return render(request, "auctions/index.html", {
        "listings": Auction.objects.all(),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        form = CreateListingsForm(request.POST)
        form.instance.user = request.user
        if request.POST["image"] == []:
            request.POST["image"] = 'https://cdn.onlinewebfonts.com/svg/img_391144.png'
        print(request.POST)
        if form.is_valid():
            form.save()
            print('valid')
            return HttpResponseRedirect(reverse("index"))
        else:
            print(form.errors)
            form = CreateListingsForm()
            return render(request, "auctions/listings.html", {
            "form": form
            })
    else:
        form = CreateListingsForm()
        return render(request, "auctions/listings.html", {
            "form": form
        })