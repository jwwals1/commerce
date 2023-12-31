from django import forms
from django.forms import ModelForm
from .models import AuctionListing, Comment, Bid


class CreateListingForm(forms.ModelForm):
    product_name = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={
            'style': 'border-radius: 10px;',
        }))

    brief_description = forms.CharField(max_length=300, widget=forms.TextInput(
        attrs={
            'style': 'border-radius: 10px;'
        }))

    price = forms.DecimalField(max_digits=6, min_value=2, widget=forms.TextInput(
        attrs={
            'style': 'border-radius: 10px;'
        }))

    product_image = forms.ImageField(required=False)

    class Meta:
        model = AuctionListing
        fields = ['product_name', 'brief_description', 'price',
                  'product_image']


class CommentForm(forms.ModelForm):
    comment_text = forms.CharField(label="Comment", widget=forms.TextInput(
        attrs={'placeholder': 'Make Comment',
               'style': 'border-radius: 10px;'
               }))

    class Meta:
        model = Comment
        fields = ["comment_text"]


class BidForm(forms.ModelForm):
    bid_price = forms.DecimalField(max_digits=6, decimal_places=2, widget=forms.TextInput(
        attrs={'placeholder': 'Make Bid',
               'style': 'border-radius: 10px;',
               }))

    class Meta:
        model = Bid
        fields = ['bid_price']
