from rest_framework import serializers
from .models import AuctionListing, User


class AuctionListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionListing
        fields = ['id', 'product_name', 'price', 'created_at',
                  'product_image', 'brief_description', 'seller_name']
    seller_name = serializers.StringRelatedField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
