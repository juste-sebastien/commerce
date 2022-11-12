from decimal import *

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .models import User, Auction
from .forms import *


def index(request):
    return render(
        request,
        "auctions/index.html",
        {
            "listings": Auction.objects.all(),
        },
    )


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
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
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
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        form = CreateListingsForm(request.POST)
        form.instance.user = request.user
        form.instance.creation_date = timezone.now()
        if request.POST["image"] == []:
            form.instance.image = "https://cdn.onlinewebfonts.com/svg/img_391144.png"
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            print(form.errors)
            form = CreateListingsForm()
            return render(request, "auctions/listings.html", {"form": form})
    else:
        form = CreateListingsForm()
        return render(request, "auctions/listings.html", {"form": form})


def get_listing(request, listing_id):
    bid_form = BidForm()
    auction = Auction.objects.get(pk=listing_id)

    try: 
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        user = request.user
        button_text = ""
    else:
        if is_in_watchlist(auction, user):
            button_text = "Add to Watchlist"
        else:
            button_text = "Remove from Watchlist"

    remaining_time = str(auction.get_remaining_time(timezone.now()))[:-7]
    message = True

    if request.method == "POST":
        if "bid" in request.POST:
            message = is_valid_bid(request, auction)
        else:
            button_text, message = modify_watchlist(auction, user)
    return render(
        request,
        "auctions/current_listing.html",
        {
            "auction": auction,
            "user": user,
            "users": User.objects.all(),
            "remaining_time": remaining_time,
            "bid_form": bid_form,
            "message": message,
            "watchlist_text": button_text,
        },
    )


def is_valid_bid(request, auction):
    new_price = request.POST["price"]
    if Decimal(new_price) > auction.price:
        auction.price = new_price
        auction.save()
        return True
    return False


def is_in_watchlist(auction, user):
    watchlist = user.watchlist
    if auction in user.watchlist.all():
        return True
    else:
        return False


def modify_watchlist(auction, user):
    statement = is_in_watchlist(auction, user)
    if statement:
        user.watchlist.remove(auction)
        user.save()
        return "Add from Watchlist", True
    elif not statement:
        user.watchlist.add(auction)
        user.save()
        return "Delete from Watchlist", True
    return "Error! Reload page", False
    

@login_required
def watchlist(request):
    user = User.objects.get(username=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist": user.watchlist.all(),
        "username": user.username.capitalize(),
    })


@login_required
def close_auction(request):
    print(request.POST)