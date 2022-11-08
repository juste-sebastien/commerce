from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


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
        (BOOK, "Books, Comics,...")
    ]

    title = models.CharField(max_length=64)
    description = models.TextField(max_length=500, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    image = models.URLField(blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    duration = models.IntegerField(default=7)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES, default=INFORMATION_TECHNOLOGY)
    start_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)


class Comment(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=500)