from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    A class used to represent a user

    ...

    Attributes
    ----------
    watchlist: Field
        ManyToManyField to store all the auctions that the user saved 

    Methods
    -------

    """
    watchlist = models.ManyToManyField("Auction", blank=True, related_name="listings")


class Auction(models.Model):
    """
    A class used to represent an auction

    ...

    Attributes
    ----------
    CATEGORY_CHOICES: list
        List of tuples to store the categories
    DURATION_CHOICES: list
        List of tuples to store possibles durations of an auction
    title: str
        Title of an auction
    description: str
        Description of an auction
    creation_date: datetime
        The date and time of creation of an auction
    image: str
        URL of a distant image to illustrate the auction
    user: User
        ForeignKey of a User representation
    duration: int
        Corresponding to a DURATION_CHOICES
    category: str
        Corresponding to a CATEGORY_CHOICES
    price: Decimal
        The starting price of an auction
    status: boolean
        True if the auction is active
        False if not
    remaining: str
        The rest active time of an auction
    winner: str
        User that have won the auction
    bids: Field
        ManyToManyField to store all bids of an auction
    comments: Field
        ManyToManyField to store all comments of an auction

    Methods
    -------
    get_end(current, duration):
        Return end date of an auction

    update_remaining_time(current):
        Return True self.remaining could be update
        False if not and update self.status to False too

    is_valid_time(time):
        Return True if time is higher than current
        False if not

    update_winner(bid):
        Update the winner of the auction

    """
    HOUSE = "HOU"
    MOTORS = "MOT"
    PROPERTY = "PPT"
    HOBBIES = "HOB"
    INFORMATION_TECHNOLOGY = "IT"
    MUSIC = "MUS"
    BOOK = "BOK"

    CATEGORY_CHOICES = [
        (HOUSE, "All for your House"),
        (MOTORS, "Car, Moto, Boat"),
        (PROPERTY, "Houses, flats, manors"),
        (HOBBIES, "Hobbies"),
        (INFORMATION_TECHNOLOGY, "Laptop, Desktop, Mobile Phone"),
        (MUSIC, "CD, Musical Intrusments"),
        (BOOK, "Books, Comics,..."),
    ]

    ONE = 1
    THREE = 3
    SEVEN = 7
    FOURTEEN = 14

    DURATION_CHOICES = [
        (ONE, "1 day"),
        (THREE, "3 days"),
        (SEVEN, "7 days"),
        (FOURTEEN, "14 days"),
    ]

    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    image = models.URLField(null=True, blank=True, default="https://cdn.onlinewebfonts.com/svg/img_391144.png", )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    duration = models.IntegerField(choices=DURATION_CHOICES)
    category = models.CharField(
        max_length=3, choices=CATEGORY_CHOICES, default=INFORMATION_TECHNOLOGY
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    status = models.BooleanField(default=True)
    remaining = models.CharField(max_length=32, blank=True)
    winner = models.CharField(max_length=64, blank=True)
    bids = models.ManyToManyField("Bid", blank=True, related_name="bids")
    comments = models.ManyToManyField("Comment", blank=True, related_name="comments")

    def __str__(self):
        return f"{self.id}: {self.title} by {self.user}"

    def get_end_date(self):
        """
        Add self.duration to self.creation_date

        Parameters
        ----------

        Return
        ------
        end: datetime
            The end date of an auction
        """
        end = self.creation_date + timedelta(days=self.duration)
        return end

    def update_remaining_time(self, current):
        """
        Update the remaining time of an auction

        If the time is in the current time self.remaining is updated
        If not self.status set to False to deactivate auction

        Parameters
        ----------
        current : datetime
            The current date

        Return
        ------
        True: boolean
            if is time is in current
        False: boolean
            if time out of current

        """
        time = self.get_end_date() - current
        if self.is_valid_time(time):
            self.remaining = str(time)[:-7]
            return True
        else:
            self.status = False
            return False

    def is_valid_time(self, time):
        """
        Check if time is higher or lower than current

        Parameters
        ----------
        time: datetime
            Represent the rest duration time of an auction

        Return
        ------
        True: boolean
            If time passed in argument is higher than current time
        Fals: boolean
            If not
        """
        if time > timedelta():
            return True
        return False

    def update_winner(self, bid):
        """
        Set the winner of an auction

        Parameters
        ----------
        bid: Bid
            A Bid object

        Return
        ------
        self.winner: str
            Represent the username of the winner of an auction
        """
        self.winner = bid.user.username
        return self.winner


class Bid(models.Model):
    """
    A class used to represent a bid

    ...

    Attributes
    ----------
    auction: Auction
        ForeignKey of an Auction representation
    auction_date: datetime
        The date and time for a bid place to an auction
    user: User
        ForeignKey of a User representation
    price: Decimal
        The current price of an auction


    Methods
    -------

    """
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    def __str__(self):
        return (
            f"{self.id}: {self.auction.title} by {self.user.username} at {self.price}"
        )


class Comment(models.Model):
    """
    A class used to represent a Comment

    ...

    Attributes
    ----------
    auction: Auction
        ForeignKey of an Auction representation
    date: datetime
        The date of a comment
    user: User
        ForeignKey of a User representation
    title: str
        Title of a comment
    content: str
        The comment himself


    Methods
    -------

    """
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, default="New comment")
    date = models.DateField(auto_now_add=True)
    content = models.TextField(max_length=500)

    def __str__(self):
        return f"{self.id}: {self.user.username} {self.date}"
