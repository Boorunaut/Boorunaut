# -*- coding: utf-8 -*-
import base64
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
from django.urls import reverse
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
        image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
        image_bytes = base64.b64decode(image_base64)
        image_file = tempfile.NamedTemporaryFile(suffix='.png')
        image_file.write(image_bytes)

        image_mock = ImageFile(image_file)
        tags = ['test1', 'test2']
        source = "http://example.org"

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
        post = self.create_test_post(user)

        c = Client()
        post = reverse('booru:post_detail', args=(post.id,))
        response = c.get(post)
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

        upload_url = reverse('booru:upload')
        response = c.post(upload_url, data)
        del image

        post_url = reverse('booru:post_detail', args=(1,))    
        self.assertEqual(200, response.status_code)
