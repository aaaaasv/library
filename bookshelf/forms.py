from django import forms
from django.forms import ModelForm, CharField, TextInput
from .models import Book, Profile, PaperBook, ElectronicBook

class BookEdit(ModelForm):
    class Meta:
        model = PaperBook
        exclude = ('type', 'borrower', 'reserver', 'reserved_amount', 'status')

class EBookEdit(ModelForm):
    class Meta:
        model = ElectronicBook
        exclude = ('type', 'status')

class EBookCreate(ModelForm):
    class Meta:
        model = ElectronicBook
        exclude = ('type', 'status')

class BookCreate(ModelForm):
    class Meta:
        model = PaperBook
        exclude = ('type', 'borrower', 'reserver', 'reserved_amount', 'status')


class BorrowerCardNumberForm(forms.Form):
    card_number = CharField(max_length=13,
                            widget=TextInput(attrs={'type': 'number',
                                                    'placeholder': 'Card number',
                                                    }),
                            label='')
