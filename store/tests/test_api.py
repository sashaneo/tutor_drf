import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')  # - create session for test_create
        self.book1 = Book.objects.create(name='test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book2 = Book.objects.create(name='test book 2', price=23.53, author_name='Author 5')
        self.book3 = Book.objects.create(name='test book Author 1', price=23.53, author_name='Author 2')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book1, self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 23.53})
        serializer_data = BooksSerializer([self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BooksSerializer([self.book1, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'author_name'})
        serializer_data = BooksSerializer([self.book1, self.book3, self.book2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Programming in Python 3",
            "price": 150,
            "author_name": "Mark Summerfield"

        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)  # - login test_username
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)


    def test_update(self):
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": 30,
            "author_name": self.book1.author_name

        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)  # - login test_username
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # self.book1 = Book.objects.get(id=self.book1.id) - can be simpler, see below
        self.book1.refresh_from_db()
        self.assertEqual(30, self.book1.price)

    # create test for delete, and for get book using id

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": 30,
            "author_name": self.book1.author_name

        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)  # - login test_username
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        # self.book1 = Book.objects.get(id=self.book1.id) - can be simpler, see below
        # print(response.data)
        self.book1.refresh_from_db()
        self.assertEqual(25, self.book1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": 30,
            "author_name": self.book1.author_name

        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)  # - login test_username
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # self.book1 = Book.objects.get(id=self.book1.id) - can be simpler, see below
        # print(response.data)
        self.book1.refresh_from_db()
        self.assertEqual(30, self.book1.price)




