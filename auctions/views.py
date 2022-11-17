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
    """
    Update rest time of each auction and render the webpage with all active auctions

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request

    Return
    ------
    render():
        The rendering of the index webpage
    """
    for auction in Auction.objects.all():
        update_auction_time(auction)
    try:
        user = User.objects.get(username=request.user)
    except:
        watchlist = 0
    else:
        watchlist = len(user.watchlist.all())
    return render(
        request,
        "auctions/index.html",
        {
            "listings": Auction.objects.all(),
            "category_form": CategoryForm(),
            "len_watchlist": watchlist,
        },
    )


def login_view(request):
    """
    Check if user is an authentic user 

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request

    Return
    ------
    render():
        The rendering of the login webpage
    """
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
    """
    Logout the user and return to index

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request

    Return
    ------
    HttpResponseRedirect():
        Redirect user to index webpage
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    Create a new User

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request

    Return
    ------
    render():
        The rendering of register webpage
    """
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
    """
    Create a new Auction

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request

    Return
    ------
    render():
        The rendering of the index webpage
    """
    user = User.objects.get(username=request.user)
    if request.method == "POST":
        form = CreateListingsForm(request.POST)
        form.instance.user = user
        form.instance.creation_date = timezone.now()
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            form = CreateListingsForm()
            return render(request, "auctions/listings.html", {
                "form": form,
                "len_watchlist": len(user.watchlist.all()),

            })
    else:
        form = CreateListingsForm()
        return render(request, "auctions/listings.html", {
            "form": form,
            "len_watchlist": len(user.watchlist.all()),
        })


def get_listing(request, listing_id):
    """
    Render a selected Auction. Three diferent POST methods are analysed.
        1- bid: to place a bid
        2- comment: to add a comment
        3- watch: to add or remove an auction to the watchlist

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request

    Return
    ------
    render():
        The rendering of the current_listing webpage
    """
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
    print(auction.image, type(auction.image))
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
            "len_watchlist": len(user.watchlist.all()),
            "image": auction.image,
        },
    )


def is_valid_bid(request, auction, user):
    """
    Check if the bid is higher or lower than current price of an auction

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request
    auction: Auction
        Represent an Auction object
    user: User
        Represent a User object

    Return
    ------
    True: boolean
        if the bid is higher to the current auction price
    False: boolean
        if not
    """
    new_price = Decimal(request.POST["price"])
    if new_price > auction.price:
        place_bid(new_price, auction, user)
        return True
    return False


def place_bid(price, auction, user):
    """
    Update the price of the auction

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request
    auction: Auction
        Represent an Auction object
    user: User
        Represent a User object

    """
    auction.price = price
    bid = Bid.objects.create(
        auction=auction, user=user, auction_date=timezone.now(), price=auction.price
    )
    bid.save()
    auction.bids.add(bid)
    auction.save()


def is_in_watchlist(auction, user):
    """
    Check if auction is in user's watchlist

    Parameters
    ----------
    auction: Auction
        Represent an Auction object
    user: User
        Represent a User object

    Return
    ------
    True: boolean
        if the auction is in user's watchlist
    False: boolean
        if not
    """
    watchlist = user.watchlist
    if auction in user.watchlist.all():
        return True
    else:
        return False


def modify_watchlist(auction, user):
    """
    Save a new auction in user's watchlist

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request
    auction: Auction
        Represent an Auction object
    user: User
        Represent a User object

    Return
    ------
    tuple: str, boolean
        str: Represent text of watchlist button
        boolean: if an error occurs or not
    """
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
    """
    Try to add a new comment to an auction

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request
    auction: Auction
        Represent an Auction object
    user: User
        Represent a User object

    Return
    ------
    True: boolean
        if the comment could be saved
    False: boolean
        if fail
    """
    comment = request.POST["content"]
    title = request.POST["title"]
    try:
        new_comment = Comment.objects.create(
            auction=auction,
            user=user,
            title=title,
            date=timezone.now(),
            content=comment,
        )
    except:
        return False
    else:
        new_comment.save()
        auction.comments.add(new_comment)
        auction.save()
        return True


@login_required
def watchlist(request):
    """
    Render watchlist of a user with all his saved auctions

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request

    Return
    ------
    render(): 
        Rendering of watchlist webpage
    """
    user = User.objects.get(username=request.user)
    for auction in user.watchlist.all():
        update_auction_time(auction)
    return render(
        request,
        "auctions/watchlist.html",
        {
            "watchlist": user.watchlist.all(),
            "username": user.username.capitalize(),
            "len_watchlist": len(user.watchlist.all()),
        },
    )


def update_auction_time(auction):
    """
    Update rest time of an auction

    Parameters
    ----------
    auction: Auction
        Represent an Auction object
    """
    if not auction.update_remaining_time(timezone.now()):
        bid = search_bid(auction)
        auction.update_winner(bid)
    auction.save()


def search_bid(auction):
    """
    Check if the bid exist

    Parameters
    ----------
    auction: Auction
        Represent an Auction object

    Return
    ------
    None: NoneType
        if the bid not exist
    bid: Bid
        if bid exist
    """
    try:
        bid = Bid.objects.get(auction=auction, price=auction.price)
    except Bid.DoesNotExist:
        return None
    else:
        return bid


@login_required
def close_auction(request, auction_id):
    """
    Close an auction before the end set when user who's created the auction wants

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request
    auction_id: int
        Represent id of an Auction object

    Return
    ------
    HttpResponseRedirect(): HttpResponseRedirect
        Redirect to index webpage

    """
    auction = Auction.objects.get(id=auction_id)
    auction.status = False
    bid = search_bid(auction)
    if bid != None:
        auction.winner = auction.update_winner(bid)
    auction.remaining = "Ended"
    auction.save()
    return HttpResponseRedirect((reverse("index")))


def categorize(request):
    """
    Render all auctions append to a specific category

    Parameters
    ----------
    request: WSGIRequest
        Represent the browser request

    Return
    ------
    render():
        Rendering of category_listing webpage

    """
    category_filter = request.GET["select"]
    for i in range(len(Auction.CATEGORY_CHOICES)):
        if Auction.CATEGORY_CHOICES[i][0] == category_filter:
            category_index = i
    listings = Auction.objects.filter(category=category_filter)
    user = User.objects.get(username=request.user)
    return render(
        request,
        "auctions/category_listing.html",
        {
            "listings": listings,
            "category": Auction.CATEGORY_CHOICES[category_index][1],
            "len_watchlist": len(user.watchlist.all()),
        }
    )