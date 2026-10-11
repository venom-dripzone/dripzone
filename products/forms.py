
from django import forms


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(
        max_length=150,
        label="Full name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
        }),
    )

    phone = forms.CharField(
        max_length=30,
        label="Phone number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
        }),
    )

    address = forms.CharField(
        label="Delivery address",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter your complete delivery address',
        }),
    )