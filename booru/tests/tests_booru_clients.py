# -*- coding: utf-8 -*-
import tempfile
from collections import Counter
from io import BytesIO
from urllib.parse import urlparse

import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, User
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import Client, RequestFactory, TestCase
from PIL import Image

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

    def create_test_post(self, user):
        image_mock = ImageFile(tempfile.NamedTemporaryFile(suffix='.png'))
        tags = ['test1', 'test2']
        source = "http://example.org"

        test_post = Post.objects.create(uploader=user, image=image_mock,
                                        source=source, tags=tags)
        return test_post

    def test_request_index_by_anonymous_client(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(200, response.status_code)

    def test_request_post_list_by_anonymous_client(self):
        c = Client()
        response = c.get('/post/list/')
        self.assertEqual(200, response.status_code)

    def test_request_post_detail_by_anonymous_client(self):
        user = self.create_test_user()
        post = self.create_test_post(user)

        c = Client()
        response = c.get('/post/view/{}/'.format(post.id))
        self.assertEqual(200, response.status_code)

    def test_post_was_created_by_logged_client(self):
        user = self.create_test_user()
        user.is_staff = True
        user.save()

        c = Client()
        c.login(username=user.username, password="123")

        im = Image.new(mode='RGB', size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, format='JPEG')
        im_io.seek(0)

        image = InMemoryUploadedFile(
            im_io, None, 'random-name.jpg', 'image/jpeg', im_io.getbuffer().nbytes, None
        )

        data = {"image": image,
                "tags": "test3 test4",
                "source": "http://example.org/testing"}

        response = c.post('/upload/', data)
        del image
    
        self.assertEqual(302, response.status_code)
        self.assertEqual('/post/view/{}/'.format(1), response.url)
