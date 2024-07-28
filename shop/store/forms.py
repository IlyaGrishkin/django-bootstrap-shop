from django import forms
from store.models import Book, Rating, CommentBook

BOOK_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


class CartForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=BOOK_QUANTITY_CHOICES, coerce=int, initial=(1, '1'), label='Количество')
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class NewBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['name', 'price', 'writer', 'description', 'image', ]


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']
        labels = {
            'value': 'Оценить',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentBook
        fields = ('comment',)


class SearchBookForm(forms.Form):
    name = forms.CharField(max_length=200)
    labels = {
        'name': 'Найти',
    }
