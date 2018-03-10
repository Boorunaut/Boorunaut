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

from booru.models import Category
from booru.forms import CreatePostForm, EditPostForm, TagListSearchForm, AliasCreateForm, ImplicationCreateForm


class CreateBooruFormTests(TestCase):

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

    def create_test_image_file(self):
        im = Image.new(mode='RGB', size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, format='JPEG')
        im_io.seek(0)

        image = InMemoryUploadedFile(
            im_io, None, 'random-name.jpg', 'image/jpeg', im_io.getbuffer().nbytes, None
        )

        return image

    def test_create_post_form(self):
        image_mock = self.create_test_image_file()

        form_data = {'tags': 'test1 test2', 'source': 'http://a.com'}
        file_data = {'image': image_mock}
        form = CreatePostForm(form_data, file_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual('http://a.com', form.cleaned_data['source'])
        self.assertEqual(['test1', 'test2'], form.cleaned_data['tags'])
        self.assertEqual(image_mock, form.cleaned_data['image'])

    def test_create_post_form(self):
        form_data = {'rating': 2, 'parent': 1, 'source': 'http://a.com', 'tags': 'test3 test4'}
        form = EditPostForm(form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual('http://a.com', form.cleaned_data['source'])
        self.assertEqual(['test3', 'test4'], form.cleaned_data['tags'])
        self.assertEqual(2, form.cleaned_data['rating'])
        self.assertEqual(1, form.cleaned_data['parent'])
    
    def test_tag_list_search_form(self):
        category = Category.objects.create(label="general", title_singular="General", title_plural="General")

        form_data = {'category': category.pk, 'tags': 'test5 test6'}
        form = TagListSearchForm(form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual('test5 test6', form.cleaned_data['tags'])
        self.assertEqual(category, form.cleaned_data['category'])

    def test_alias_create_form(self):
        form_data = {'from_tag': 'test1', 'to_tag': 'test2'}
        form = AliasCreateForm(form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual('test1', form.cleaned_data['from_tag'])
        self.assertEqual('test2', form.cleaned_data['to_tag'])

    def test_implication_create_form(self):
        form_data = {'from_tag': 'test3', 'to_tag': 'test4'}
        form = ImplicationCreateForm(form_data)
        
        self.assertTrue(form.is_valid())
        self.assertEqual('test3', form.cleaned_data['from_tag'])
        self.assertEqual('test4', form.cleaned_data['to_tag'])
