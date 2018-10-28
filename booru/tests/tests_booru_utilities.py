# -*- coding: utf-8 -*-
import re
import tempfile
from collections import Counter
from urllib.parse import urlparse

import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase
from django.test.utils import override_settings
from booru.utils import space_splitter
from booru.utils import space_joiner
from booru.utils import compare_strings

class UtilitiesTests(TestCase):
    fixtures = []

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_space_splitter_generates_tags_from_string(self):
        tag_string = "test1 test2 test:test_3 test_4"
        generated_tags = space_splitter(tag_string)
        expected_generated_tags = ["test1", "test2", "test:test_3", "test_4"]
        self.assertEqual(generated_tags, expected_generated_tags)

    def test_history_diff(self):
        old_string = "test1 test2 test3"
        new_string = "test2 test3 test4"
        expected = {"added": ["test4"], "removed": ["test1"], "equal": ["test2", "test3"]}

        result = compare_strings(old_string, new_string)
        self.assertEqual(sorted(result["added"]), sorted(expected["added"]))
        self.assertEqual(sorted(result["removed"]), sorted(expected["removed"]))
        self.assertEqual(sorted(result["equal"]), sorted(expected["equal"]))
