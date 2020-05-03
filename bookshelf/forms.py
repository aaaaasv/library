from django import forms
from django.forms import ModelForm, CharField, TextInput
from .models import Book, Profile, PaperBook, ElectronicBook


class BookEdit(ModelForm):
    class Meta:
        model = PaperBook
        # fields = '__all__'
        exclude = ['type']

class EBookEdit(ModelForm):
    class Meta:
        model = ElectronicBook
        exclude = ('type', 'status', 'file_format', 'link')
        # fields = '__all__'

class EBookCreate(ModelForm):
    class Meta:
        model = ElectronicBook
        exclude = ('type', 'status')


class BorrowerCardNumberForm(forms.Form):
    card_number = CharField(max_length=13,
                            widget=TextInput(attrs={'type': 'number',
                                                    'placeholder': 'Card number',
                                                    }),
                            label='')

    # class Meta:
    #     model = Profile
    #     fields = ['card_number']
