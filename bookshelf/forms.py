from django import forms
from django.forms import ModelForm, CharField, TextInput
from .models import Book, Profile


class BookEdit(ModelForm):
    # TODO: Update book form now is not working
    class Meta:
        model = Book
        fields = '__all__'


class BorrowerCardNumberForm(forms.Form):
    card_number = CharField(max_length=13,
                            widget=TextInput(attrs={'type': 'number',
                                                    'placeholder': 'Card number',
                                                    }),
                            label='')

    # class Meta:
    #     model = Profile
    #     fields = ['card_number']
