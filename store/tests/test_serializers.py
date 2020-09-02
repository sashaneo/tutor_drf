from unittest import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book1 = Book.objects.create(name='test book 1', price=25, author_name='author')
        book2 = Book.objects.create(name='test book 2', price=55, author_name='author')
        data = BooksSerializer([book1, book2], many=True).data
        expected_data = [
            {
                'id': book1.id,
                'name': 'test book 1',
                'price': '25.00',
                'author_name': 'author'


            },
            {
                'id': book2.id,
                'name': 'test book 2',
                'price': '55.00',
                'author_name': 'author'


            }
        ]
        self.assertEqual(expected_data, data)




