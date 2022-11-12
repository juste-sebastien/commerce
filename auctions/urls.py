from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listings/create", views.create, name="listings_create"),
    path("listings/<int:listing_id>", views.get_listing, name="listing_view"),
    path("listings/<int:auction_id>", views.close_auction, name="close_listing"),
    path("watchlist/", views.watchlist, name="watchlist"),
]
