import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')  # - create session for test_create
        self.book1 = Book.objects.create(name='test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book2 = Book.objects.create(name='test book 2', price=23.53, author_name='Author 5')
        self.book3 = Book.objects.create(name='test book Author 1', price=23.53, author_name='Author 2')

        UserBookRelation.objects.create(user=self.user, book=self.book1, like=True, rate=5)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate')
        ).order_by('id')

        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['likes_count'], 1)
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_get_filter(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in=[self.book2.id, self.book3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate')
        ).order_by('id')

        response = self.client.get(url, data={'price': 23.53})
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in=[self.book1.id, self.book3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate')
        ).order_by('id')
        response = self.client.get(url, data={'search': 'Author 1'})
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    # def test_get_ordering(self):
    #     url = reverse('book-list')
    #     response = self.client.get(url, data={'ordering': 'author_name'})
    #     serializer_data = BooksSerializer([self.book1, self.book3, self.book2], many=True).data
    #     self.assertEqual(status.HTTP_200_OK, response.status_code)
    #     print('='*10)
    #     print(response.data)
    #     print('='*10)
    #     print(serializer_data)
    #     print('='*10)
    #     self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in=[self.book1.id, self.book3.id, self.book2.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate')
        ).order_by('id')
        response = self.client.get(url, data={'ordering': 'author_name'})
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        print('='*10)
        print(response.data)
        print('='*10)
        print(serializer_data)
        print('='*10)
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


class BooksRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')  # - create session for test_create
        self.user2 = User.objects.create(username='test_username2')  # - create session for test_create
        self.book1 = Book.objects.create(name='test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book2 = Book.objects.create(name='test book 2', price=23.53, author_name='Author 5')

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        data = {
            "like": True,

        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertTrue(relation.like)

        data = {
            "in_bookmarks": True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        data = {
            "rate": 3,

        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertEqual(3, relation.rate)
