from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import CreateListingForm, CommentForm, BidForm
from .models import AuctionListing, Comment, Bid
from auctions.forms import CreateListingForm
from .models import User, AuctionListing
from django.contrib import messages
from .serializers import AuctionListingSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, APIView
from rest_framework import status

# Homepage with all auctions and their name, seller name, description and price.


def index(request):
    auctions = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {'auctions': auctions})


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


@login_required(login_url="login")
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST, request.FILES)
        if form.is_valid():
            product_name = form.cleaned_data['product_name']
            brief_description = form.cleaned_data['brief_description']
            price = form.cleaned_data['price']
            product_image = form.cleaned_data['product_image']
            listing = AuctionListing(
                seller_name=User.objects.get(pk=request.user.id),
                product_name=product_name,
                brief_description=brief_description,
                price=price,
                product_image=product_image
            )
            listing.save()
            messages.info(request, "Successfully created an Auction")
        else:
            return render(request, 'auctions/createlisting.html', {'form': form})

    return render(request, 'auctions/createlisting.html', {
        "form": CreateListingForm(),
    })


# Page with all auctions and details including picture.
def active_listings(request):
    auctions = AuctionListing.objects.all()
    return render(request, 'activelistings.html', {
        "auctions": auctions,
    })


# Page with individual auctions and all details including hightest bid and comments.
def listing_page(request, auction_id):
    auction = AuctionListing.objects.get(pk=auction_id)
    comments = Comment.objects.filter(auction=auction_id)
    bid_times = Bid.objects.filter(auction=auction_id).count()
    hightest_bid = Bid.objects.filter(
        auction=auction_id).order_by('-bid_price').first()
    if hightest_bid is not None:
        bid_information = f"The highest bidder is {hightest_bid}."
    else:
        bid_information = None
    return render(request, 'auctions/listingpage.html', {
        "auction": auction,
        "comments": comments,
        "comment_form": CommentForm(),
        "bid_form": BidForm(),
        "bid_times": bid_times,
        "bid_information": bid_information
    })


@login_required(login_url="login")
def bid(request):
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            bid_price = float(form.cleaned_data["bid_price"])
            auction_id = request.POST.get("auction_id")
            auction = AuctionListing.objects.get(pk=auction_id)
            bidder_name = User.objects.get(id=request.user.id)
            hightest_bid = Bid.objects.filter(
                auction=auction_id).order_by('-bid_price').first()
            # Validating new bid is higher than previous highest bid
            if hightest_bid is None or bid_price > hightest_bid.bid_price:
                new_bid = Bid(auction=auction,
                              bidder_name=bidder_name, bid_price=bid_price)
                new_bid.save()
                auction.price = bid_price
                auction.save()
            # If not send message to user that bid must be higher.
            else:
                messages.info(request, "Bid must be higher than price")
                return HttpResponseRedirect('/' + auction_id)

            return HttpResponseRedirect('/' + auction_id)

        else:
            return render(request, 'auctions/createlisting.html')
    return HttpResponseRedirect('/' + auction_id)


@login_required(login_url="login")
def new_comments(request, auction_id):
    auction = AuctionListing.objects.get(pk=auction_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment_cleaned = form.cleaned_data
            comment = Comment(
                user_comment=User.objects.get(pk=request.user.id),
                auction=auction,
                **comment_cleaned
            )
            comment.save()

        else:
            return render(request, 'auctions/createlisting.html')
    return HttpResponseRedirect("/" + auction_id)


# User personal page with their auctions and bids.
@login_required(login_url="login")
def user_account(request):
    auction_sellings = AuctionListing.objects.filter(
        seller_name=request.user.id).all()
    all_bids = Bid.objects.filter(
        bidder_name=request.user.id).all()

    return render(request, 'auctions/useraccount.html', {
        "auction_sellings": auction_sellings,
        "all_bids": all_bids,
    })

# Class based view rendering all auctions api using django restframework.


class AuctionListingsData(APIView):
    def get(self, request):
        queryset = AuctionListing.objects.all()
        serializer = AuctionListingSerializer(queryset, many=True)
        return Response(serializer.data)

    # Create an auction using django restframework
    def post(self, request):
        serializer = AuctionListingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Class based view rendering individual auction api using django restframework.
class AuctionListingData(APIView):
    def get(self, request, id):
        auction_listing = get_object_or_404(AuctionListing, pk=id)
        serializer = AuctionListingSerializer(auction_listing)
        return Response(serializer.data)

    # Update an auction using django restframework
    def put(self, request, id):
        auction_listing = get_object_or_404(AuctionListing, pk=id)
        serializer = AuctionListingSerializer(
            auction_listing, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Function based view rendering all users and their id using django restframework.
@api_view()
def users_data(request):
    queryset = User.objects.all()
    serializer = UserSerializer(queryset, many=True)
    return Response(serializer.data)


# Function based view rendering individual users and their id using django restframework.
@api_view()
def user_data(request, id):
    userdata = get_object_or_404(User, pk=id)
    serializer = UserSerializer(userdata)
    return Response(serializer.data)
