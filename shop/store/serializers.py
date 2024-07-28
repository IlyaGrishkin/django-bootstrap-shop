from rest_framework import serializers
from store.models import Book


class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ['name', 'price', 'writer']
