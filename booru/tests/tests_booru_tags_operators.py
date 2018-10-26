# -*- coding: utf-8 -*-
import django
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.test import TestCase
from django.db.models import Q

import tempfile
from booru.models import Post
from booru.views import tags_list
from booru.utils import parse_and_filter_tags

def create_test_user():
    user = get_user_model().objects.create_user('Test', password="123")
    user.save()
    return user

def create_test_post(user, tags=[]):
    image_mock = ImageFile(tempfile.NamedTemporaryFile(suffix='.png'))
    source = "http://example.org"

    test_post = Post.objects.create(uploader=user, image=image_mock,
                                    source=source)
    
    for tag in tags:
        test_post.tags.add(tag)

    return test_post

class UtilitiesTests(TestCase):
    post_one = None
    post_two = None
    post_three = None

    @classmethod
    def setUpClass(cls):
        mock_user = create_test_user()
        
        cls.post_one = create_test_post(mock_user, ['test1', 'test2', 'test3'])
        cls.post_two = create_test_post(mock_user, ['test1', 'test2', 'test4', 'test5'])
        cls.post_three = create_test_post(mock_user, ['test1', 'test4', 'test6'])

        super().setUpClass()
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_tag_search_one_result(self):
        posts = parse_and_filter_tags('test3')

        self.assertEqual(list(posts), [self.post_one])

    def test_tag_search_three_results(self):
        posts = parse_and_filter_tags('test1')

        self.assertEqual(list(posts), [self.post_one, self.post_two, self.post_three])

    def test_tag_search_and_operation_result_none(self):
        posts = parse_and_filter_tags('test3 test5')

        self.assertEqual(list(posts), [])

    def test_tag_search_and_operation_result_one(self):
        posts = parse_and_filter_tags('test4 test6')

        self.assertEqual(list(posts), [self.post_three])

    def test_tag_search_and_or_operations_between_two_tags(self):
        posts = parse_and_filter_tags('test3 ~test5')

        self.assertEqual(list(posts), [])

    def test_tag_search_two_or_operation_between_two_tags(self):
        posts = parse_and_filter_tags('~test3 ~test6')

        self.assertEqual(list(posts), [self.post_one, self.post_three])

    def test_tag_search_not_operation_between_two_tags(self):
        posts = parse_and_filter_tags('test1 -test2')

        self.assertEqual(list(posts), [self.post_three])

    def test_tag_search_not_operation_between_three_tags(self):
        posts = parse_and_filter_tags('test1 -test2 -test6')

        self.assertEqual(list(posts), [])

    def test_tag_search_not_operation_between_three_tags_2(self):
        posts = parse_and_filter_tags('test1 -test2 -test3')

        self.assertEqual(list(posts), [self.post_three])

    def test_tag_search_no_tags(self):
        posts = parse_and_filter_tags('')

        self.assertEqual(list(posts), [self.post_one, self.post_two, self.post_three])

