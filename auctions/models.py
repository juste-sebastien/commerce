from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    watchlist = models.ManyToManyField("Auction", blank=True, related_name="listings")


class Auction(models.Model):
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
    image = models.URLField(null=True, blank=True, default="")
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

    def get_end_date(self, current, duration):
        end = current + timedelta(days=duration)
        return end

    def update_remaining_time(self, current):
        time = self.get_end_date(self.creation_date, self.duration) - current
        if self.is_valid_time(time):
            self.remaining = str(time)[:-7]
            return True
        else:
            self.status = False
            return False

    def is_valid_time(self, time):
        if time > timedelta():
            return True
        return False

    def update_winner(self, bid):
        self.winner = bid.user.username
        return self.winner


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    def __str__(self):
        return (
            f"{self.id}: {self.auction.title} by {self.user.username} at {self.price}"
        )


class Comment(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, default="New comment")
    date = models.DateField(auto_now_add=True)
    content = models.TextField(max_length=500)

    def __str__(self):
        return f"{self.id}: {self.user.username} {self.date}"
