# -*- coding: utf-8 -*-
import tempfile
from collections import Counter
from urllib.parse import urlparse

import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from PIL import Image
from booru.utils import generate_mock_image

from booru.models import Post


class PostClientsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def create_test_user(self):
        user = get_user_model().objects.create_user('Test', password="123")
        user.save()
        return user

    def create_test_post(self, user, id_number=None):
        image_file = generate_mock_image(empty=False)
        image_mock = ImageFile(image_file)
        tags = ['test1', 'test2']
        source = "http://example.org"
        
        if id_number:
            test_post = Post.objects.create(id=id_number, uploader=user, media=image_mock,
                                        source=source, tags=tags)
        else:
            test_post = Post.objects.create(uploader=user, media=image_mock,
                                        source=source, tags=tags)
        return test_post

    def test_request_index_by_anonymous_client(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(200, response.status_code)

    def test_request_post_list_by_anonymous_client(self):
        c = Client()
        post_list = reverse('booru:posts')
        response = c.get(post_list)
        self.assertEqual(200, response.status_code)

    def test_request_post_detail_by_anonymous_client(self):
        user = self.create_test_user()
        post = self.create_test_post(user, 1)

        c = Client()
        post = reverse('booru:post_detail', args=(post.id,))
        response = c.get(post)
        self.assertEqual(200, response.status_code)
        del post

    def test_post_was_created_by_logged_client(self):
        user = self.create_test_user()
        user.is_staff = True
        user.save()

        c = Client()
        c.login(username=user.username, password="123")

        image_file = generate_mock_image()

        data = {"image": image_file,
                "tags": "test3 test4",
                "source": "http://example.org/testing"}

        upload_url = reverse('booru:upload')
        response = c.post(upload_url, data)
        del image_file

        post_url = reverse('booru:post_detail', args=(1,))
        self.assertEqual(200, response.status_code)
