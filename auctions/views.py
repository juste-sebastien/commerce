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
    for auction in Auction.objects.all():
        update_auction_time(auction)
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
    auction = Auction.objects.get(pk=listing_id)
    update_auction_time(auction)

    try: 
        user = User.objects.get(username=request.user)
    except User.DoesNotExist:
        user = request.user
        button_text = ""
    else:
        if is_in_watchlist(auction, user):
            button_text = "Remove from Watchlist"
        else:
            button_text = "Add to Watchlist"

    message = True

    if request.method == "POST":
        if "bid" in request.POST:
            message = is_valid_bid(request, auction, user)
        elif "comment" in request.POST:
            message = is_valid_comment(request, auction, user)
        else:
            button_text, message = modify_watchlist(auction, user)

    return render(
        request,
        "auctions/current_listing.html",
        {
            "auction": auction,
            "user": user,
            "users": User.objects.all(),
            "bid_form": BidForm(),
            "comment_form": CommentForm(),
            "message": message,
            "watchlist_text": button_text,
            "comments": auction.comments.all(),
        },
    )


def is_valid_bid(request, auction, user):
    new_price = Decimal(request.POST["price"])
    if new_price > auction.price:
        place_bid(new_price, auction, user)
        return True
    return False


def place_bid(price, auction, user):
    auction.price = price
    bid = Bid.objects.create(auction=auction, user=user, auction_date=timezone.now(), price=auction.price)
    bid.save()
    auction.bids.add(bid)
    auction.save()


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
        return "Remove from Watchlist", True
    return "Error! Reload page", False
    

def is_valid_comment(request, auction, user):
    comment = request.POST["content"]
    title = request.POST["title"]
    try:
        new_comment = Comment.objects.create(auction=auction, user=user, title=title, date=timezone.now(), content=comment)
    except:
        return False
    else:
        new_comment.save()
        auction.comments.add(new_comment)
        auction.save()
        return True
    


@login_required
def watchlist(request):
    user = User.objects.get(username=request.user)
    for auction in user.watchlist.all():
        update_auction_time(auction)
    return render(request, "auctions/watchlist.html", {
        "watchlist": user.watchlist.all(),
        "username": user.username.capitalize(),
    })


def update_auction_time(auction):
    """    if not auction.is_valid_time(timezone.now()):
            update_winner(auction)
        else:"""
    if not auction.update_remaining_time(timezone.now()):
        bid = search_bid(auction)
        auction.update_winner(bid)
    auction.save()


def search_bid(auction):
    try:
        bid = Bid.objects.get(auction=auction, price=auction.price)
    except Bid.DoesNotExist:
        print("bid not found")
        return None
    else:
        return bid


@login_required
def close_auction(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    auction.status = False
    bid = search_bid(auction)
    if bid != None:
        auction.winner = auction.update_winner(bid)
    auction.remaining = "Ended"
    auction.save()
    return HttpResponseRedirect((reverse('index')))


@login_required
def comment(request):
    pass