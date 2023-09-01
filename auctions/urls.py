from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('createlisting/', views.create_listing, name='createlisting'),
    path('activelistings/', views.active_listings, name='activelistings'),
    path('<int:auction_id>', views.listing_page, name='listingpage'),
    path('bid', views.bid, name='bid'),
    path('new_comments/<str:auction_id>',
         views.new_comments, name='new_comments'),
    path("useraccount/", views.user_account, name="useraccount"),
    path("auctionlistingdata/", views.AuctionListingsData.as_view()),
    path("auctionlistingdata/<id>/", views.AuctionListingData.as_view()),
    path("usersdata/", views.users_data),
    path('userdata/<id>/', views.user_data)
]
