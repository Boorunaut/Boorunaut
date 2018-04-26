# -*- coding: utf-8 -*-
import django
from django.test import TestCase
from booru.utils import verify_and_substitute_alias, search_posts_from_tag_list
from booru.models import PostTag, Alias, Post
from django.db.models import Q

class SearchTests(TestCase):
    fixtures = []

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        test_post = Post.objects.create()
        test_post2 = Post.objects.create()
        test_post3 = Post.objects.create()

        PostTag.objects.create(name="test1", slug="test1")
        PostTag.objects.create(name="test3", slug="test3")
        PostTag.objects.create(name="test4", slug="test4")
        test2 = PostTag.objects.create(name="test2", slug="test2")
        test_two = PostTag.objects.create(name="testtwo", slug="testtwo")
        
        Alias.objects.create(from_tag=test2, to_tag=test_two)

        test_post.tags.add("Test1", "Test3")
        test_post2.tags.add("Test1", "TestTwo")
        test_post3.tags.add("TestTwo", "Test4")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_verify_and_substitute_no_alias(self):
        tag_string = "test1 test3"
        generated_tags = verify_and_substitute_alias(tag_string)

        expected_generated_tags = ["test1", "test3"]
        self.assertEqual(generated_tags, expected_generated_tags)

    def test_verify_and_substitute_alias(self):
        tag_string = "test1 test2"
        generated_tags = verify_and_substitute_alias(tag_string)

        expected_generated_tags = ["test1", "testtwo"]
        self.assertEqual(generated_tags, expected_generated_tags)

    def test_get_single_post_from_tag_list(self):
        tags_list = "test3"

        expected_post = Post.objects.filter(pk=1)

        generated_tags_post = search_posts_from_tag_list(tags_list)

        self.assertEqual(list(generated_tags_post), list(expected_post))

    def test_get_multiple_posts_from_tag_list(self):
        tags_list = "test1"

        expected_post = Post.objects.filter(Q(pk=1)
                                        |   Q(pk=2))

        generated_tags_post = search_posts_from_tag_list(tags_list)

        self.assertEqual(list(generated_tags_post), list(expected_post))

    def test_get_no_posts_from_inexistent_tag_list(self):
        tags_list = "test1 testtwo non_existent"

        expected_post = Post.objects.none()

        generated_tags_post = search_posts_from_tag_list(tags_list)

        self.assertEqual(list(generated_tags_post), list(expected_post))

    def test_get_posts_excluding_tag(self):
        tags_list = "test1 -testtwo"

        expected_post = Post.objects.filter(Q(pk=1))

        generated_tags_post = search_posts_from_tag_list(tags_list)

        self.assertEqual(list(generated_tags_post), list(expected_post))

    def test_get_posts_excluding_multiple_tags(self):
        tags_list = "test1 -testtwo -test3"

        expected_post = Post.objects.none()

        generated_tags_post = search_posts_from_tag_list(tags_list)

        self.assertEqual(list(generated_tags_post), list(expected_post))

    def test_get_posts_with_or_operation_tags(self):
        tags_list = "test3 ~testtwo"

        expected_post = Post.objects.filter(Q(pk=1)
                                        |   Q(pk=2)
                                        |   Q(pk=3))

        generated_tags_post = search_posts_from_tag_list(tags_list)

        self.assertEqual(list(generated_tags_post), list(expected_post))

    def test_get_multiple_posts_from_multiple_tags(self):
        tags_list = "test1 testtwo"

        expected_post = Post.objects.filter(Q(pk=2))
        generated_tags_post = search_posts_from_tag_list(tags_list)

        self.assertEqual(list(generated_tags_post), list(expected_post))
