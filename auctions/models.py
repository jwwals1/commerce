from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    product_name = models.CharField(max_length=50, blank=False)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    product_image = models.ImageField(
        null=True, blank=True, upload_to="images/")
    brief_description = models.CharField(
        max_length=200, blank=True, default=0.0)
    seller_name = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sellername", blank=True, null=True)

    def __str__(self):
        return f"Product Name: {self.product_name}, Seller Name: {self.seller_name} "


class Bid(models.Model):
    auction = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, null=True)
    bid_price = models.DecimalField(max_digits=6, decimal_places=2)
    bidder_name = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bidder")
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder_name} bid ${self.bid_price}"


class Comment(models.Model):
    auction = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, null=True, blank=True)
    user_comment = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_comment")
    comment_text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_comment} on {self.auction}"
