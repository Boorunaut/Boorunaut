# -*- coding: utf-8 -*-
import base64
import tempfile

import django
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.db.models import Q
from django.test import TestCase

from booru.models import Post, ScoreVote
from booru.utils import parse_and_filter_tags
from booru.views import tags_list


def create_test_user(username='Test'):
    user = get_user_model().objects.create_user(username, password="123")
    user.save()
    return user

def create_test_post(user, tags=[]):
    image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
    image_bytes = base64.b64decode(image_base64)
    image_file = tempfile.NamedTemporaryFile(suffix='.png')
    image_file.write(image_bytes)

    image_mock = ImageFile(image_file)
    source = "http://example.org"

    test_post = Post.objects.create(uploader=user, media=image_mock,
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
        mock_user_two = create_test_user("Test2")

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

        self.assertEqual(list(posts), [self.post_three, self.post_two, self.post_one])

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

        self.assertEqual(list(posts), [self.post_three, self.post_one])

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

        self.assertEqual(list(posts), [self.post_three, self.post_two, self.post_one])

    def test_tag_search_status_pending(self):
        posts = parse_and_filter_tags('status:pending')
        self.assertEqual(list(posts), [self.post_three, self.post_two, self.post_one])

    def test_tag_search_status_approved(self):
        posts = parse_and_filter_tags('status:approved')
        self.post_two.status = Post.APPROVED
        self.post_two.save()
        self.assertEqual(list(posts), [self.post_two])

    def test_tag_search_status_deleted(self):
        self.post_two.status = Post.DELETED
        self.post_two.save()
        posts = parse_and_filter_tags('status:deleted')
        self.assertEqual(list(posts), [self.post_two])
    
    def test_tag_search_status_score_zero(self):
        posts = parse_and_filter_tags('score:0')
        self.assertEqual(list(posts), [self.post_three, self.post_two, self.post_one])

    def test_tag_search_status_score_one(self):
        posts = parse_and_filter_tags('score:1')
        user = get_user_model().objects.get(username="Test")
        ScoreVote.objects.create(account=user, post=self.post_three, point=1)
        self.assertEqual(list(posts), [self.post_three])
    
    def test_tag_search_status_score_greater_than_zero(self):
        posts = parse_and_filter_tags('score:>0')
        user = get_user_model().objects.get(username="Test")
        ScoreVote.objects.create(account=user, post=self.post_one, point=1)
        ScoreVote.objects.create(account=user, post=self.post_three, point=0)
        self.assertEqual(list(posts), [self.post_one])

    def test_tag_search_status_score_greater_than_one(self):
        posts = parse_and_filter_tags('score:>1')
        user = get_user_model().objects.get(username="Test")
        user_two = get_user_model().objects.get(username="Test2")
        ScoreVote.objects.create(account=user, post=self.post_three, point=1)
        ScoreVote.objects.create(account=user_two, post=self.post_three, point=1)
        self.assertEqual(list(posts), [self.post_three])
    
    def test_tag_search_status_score_less_than_zero(self):
        posts = parse_and_filter_tags('score:<0')
        user = get_user_model().objects.get(username="Test")
        user_two = get_user_model().objects.get(username="Test2")
        ScoreVote.objects.create(account=user, post=self.post_two, point=-1)
        ScoreVote.objects.create(account=user_two, post=self.post_two, point=-1)
        self.assertEqual(list(posts), [self.post_two])
    
    def test_tag_search_status_score_less_than_one(self):
        posts = parse_and_filter_tags('score:<1')
        user = get_user_model().objects.get(username="Test")
        user_two = get_user_model().objects.get(username="Test2")
        ScoreVote.objects.create(account=user, post=self.post_two, point=-1)
        ScoreVote.objects.create(account=user_two, post=self.post_two, point=1)
        self.assertEqual(list(posts), [self.post_two])
    
    def test_tag_search_rating_safe(self):
        posts = parse_and_filter_tags('rating:safe')
        posts_abbreviation = parse_and_filter_tags('rating:s')
        self.post_one.rating = Post.SAFE
        self.post_one.save()
        self.assertEqual(list(posts), list(posts_abbreviation))
        self.assertEqual(list(posts), [self.post_one])
    
    def test_tag_search_rating_questionable(self):
        posts = parse_and_filter_tags('rating:questionable')
        posts_abbreviation = parse_and_filter_tags('rating:q')
        self.post_two.rating = Post.QUESTIONABLE
        self.post_two.save()
        self.assertEqual(list(posts), list(posts_abbreviation))
        self.assertEqual(list(posts), [self.post_two])
    
    def test_tag_search_rating_explicit(self):
        posts = parse_and_filter_tags('rating:explicit')
        posts_abbreviation = parse_and_filter_tags('rating:e')
        self.post_three.rating = Post.EXPLICIT
        self.post_three.save()
        self.assertEqual(list(posts), [self.post_three])
    
    def test_tag_search_rating_none(self):
        posts = parse_and_filter_tags('rating:none')
        posts_abbreviation = parse_and_filter_tags('rating:n')
        self.post_three.rating = Post.SAFE
        self.post_three.save()
        self.assertEqual(list(posts), list(posts_abbreviation))
        self.assertEqual(list(posts), [self.post_two, self.post_one])
    
    def test_tag_search_order_by_score(self):
        posts = parse_and_filter_tags('order:score')
        user = get_user_model().objects.get(username="Test")
        user_two = get_user_model().objects.get(username="Test2")
        ScoreVote.objects.create(account=user, post=self.post_one, point=-1)
        ScoreVote.objects.create(account=user, post=self.post_two, point=-1)
        ScoreVote.objects.create(account=user_two, post=self.post_two, point=1)
        ScoreVote.objects.create(account=user, post=self.post_three, point=1)
        ScoreVote.objects.create(account=user_two, post=self.post_three, point=1)
        self.assertEqual(list(posts), [self.post_three, self.post_two, self.post_one])

    def test_tag_search_order_by_score_asc(self):
        posts = parse_and_filter_tags('order:score_asc')
        user = get_user_model().objects.get(username="Test")
        user_two = get_user_model().objects.get(username="Test2")
        ScoreVote.objects.create(account=user, post=self.post_one, point=-1)
        ScoreVote.objects.create(account=user, post=self.post_two, point=-1)
        ScoreVote.objects.create(account=user_two, post=self.post_two, point=1)
        ScoreVote.objects.create(account=user, post=self.post_three, point=1)
        ScoreVote.objects.create(account=user_two, post=self.post_three, point=1)
        self.assertEqual(list(posts), [self.post_one, self.post_two, self.post_three])
