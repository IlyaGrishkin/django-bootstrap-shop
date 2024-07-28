from decimal import Decimal

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from rest_framework import viewsets

from shop import settings
from store.models import Book, Like, CommentBook, Rating
from django.shortcuts import render, get_object_or_404, redirect

from django.shortcuts import render

from django.views.generic import UpdateView, CreateView
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import api_view, permission_classes

from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.viewsets import ModelViewSet

from store.forms import NewBookForm, RatingForm, CommentForm, SearchBookForm, CartForm
from store.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, book, quantity=1, override_quantity=False):
        book_id = str(book.id)
        if book_id not in self.cart:
            self.cart[book_id] = {'quantity': 0, 'price': str(book.price)}
        if override_quantity:
            self.cart[book_id]['quantity'] = quantity
        else:
            self.cart[book_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, book_id):
        del self.cart[str(book_id)]
        self.save()

    def __iter__(self):
        book_ids = self.cart.keys()
        books = Book.objects.filter(id__in=book_ids)
        cart = self.cart.copy()
        for book in books:
            self.cart[str(book.id)]['book'] = book
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum([item['quantity'] for item in self.cart.values()])

    def get_total_price(self):
        return sum([item['total_price'] for item in self.cart.values()])

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()


@require_POST
def cart_add(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    print(request.POST)
    form = CartForm(request.POST)
    print(form)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(book, quantity=cd['quantity'], override_quantity=cd['override'])
        print(cart)
        return redirect('/cart/detail/')
    else:
        return HttpResponse('ERROR')


def cart_detail(request):
    cart = Cart(request)
    cart_form = CartForm
    for item in cart:
        item['update_quantity_form'] = CartForm(initial={'quantity': item['quantity'],
                                                         'override': True})
    return render(request, 'store/cart_detail.html', context={'cart': cart, 'cart_form': cart_form})


def cart_remove(request, pk):
    cart = Cart(request)
    cart.remove(pk)
    return redirect('/cart/detail/')


def login_view(request):
    return render(request, 'store/login.html')


def user_register_view(request):
    login = request.POST['login']
    password = request.POST['password']
    check = request.POST['checkbox']
    # ToDo is_valid(login), is_valid(password)
    if str(check) == 'on':
        user = User.objects.create_user(str(login), '', str(password))
        user.save()
    return HttpResponse('Created')


# ToDO  owner = request.user (auth needed)
class BookCreateViewSet(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        new_book = NewBookForm(request.POST, request.FILES)
        print(request.POST)
        if new_book.is_valid():
            name = new_book.cleaned_data['name']
            price = new_book.cleaned_data['price']
            writer = new_book.cleaned_data['writer']
            image = new_book.cleaned_data['image']
            description = new_book.cleaned_data['description']
            book = Book.objects.create(name=name, price=price, writer=writer, image=image, description=description)
            book.save()
            return render(request, 'home.html')
        else:
            return render(request, 'error.html')


def home(request):
    queryset = Book.objects.all()
    context = {
        'books': queryset,
        'like': Like.objects.all(),
        'search_form': SearchBookForm,
    }
    return render(request, 'store/home.html', context)


def add_book(request):
    return render(request, 'store/add_book_page.html')


def book_detail(request, pk):
    book = Book.objects.get(id=pk)
    if CommentBook.objects.filter(book_id=pk):
        comment_for_book = CommentBook.objects.filter(book_id=pk).last().comment
    else:
        comment_for_book = 'Пока нет комментариев'
    rates = []
    all_ratings_for_book = Rating.objects.filter(book_id=pk)
    if all_ratings_for_book:
        for rate in all_ratings_for_book:
            rates.append(int(rate.value))
        res = sum(rates) / len(rates)
    else:
        res = 'Пока нет оценок'
    context = {
        'book': book,
        'book_id': pk,
        'rating_form': RatingForm(),
        'comment_form': CommentForm(),
        'cart_form': CartForm(),
        'ratings': Rating.objects.filter(book_id=pk),
        'average_rating': res,
        'comment': comment_for_book,
        'Total': Like.objects.filter(book_id=pk).count()

    }
    return render(request, "store/book_detail.html", context)


def add_comment(request, pk):
    new_comment = CommentForm(request.POST)
    book = Book.objects.get(id=pk)
    if new_comment.is_valid():
        text = new_comment.cleaned_data['comment']
        comment = CommentBook(user=None, comment=text, book=book)
        comment.save()
        return HttpResponse('Added')
    else:
        return HttpResponse('Invalid')


@api_view(['POST'])
def search_book(request):
    if request.method == 'POST':
        search_form = SearchBookForm(request.POST)
        if search_form.is_valid():
            name = search_form.cleaned_data['name']
            queryset = Book.objects.filter(name__contains=name)
            print(f'Q: {queryset}')
            if queryset:
                context = {
                    'filtered_books': queryset,
                }
                return render(request, 'store/search_results.html', context)
            else:
                return HttpResponse('Not found')
        else:
            return HttpResponse('Error')
    return HttpResponse('Error 2')
