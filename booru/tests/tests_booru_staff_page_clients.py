# -*- coding: utf-8 -*-
import tempfile
from collections import Counter
from io import BytesIO
from urllib.parse import urlparse

import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import Client, RequestFactory, TestCase
from PIL import Image

from booru.models import Post


class StaffPageClientsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def create_test_user(self, name="Test", password="123"):
        user = get_user_model().objects.create_user(name, password=password)
        user.save()
        return user

    # Staff page
    def test_request_staff_page_by_anonymous_client(self):
        c = Client()
        response = c.get('/staff_page/')
        self.assertEqual(302, response.status_code)

    def test_request_staff_page_by_logged_normal_client(self):
        user = self.create_test_user()
        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/')
        self.assertEqual(302, response.status_code)

    def test_request_staff_page_by_logged_staff_client(self):
        user = self.create_test_user()
        user.is_staff = True
        user.save()

        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/')
        self.assertEqual(200, response.status_code)

    # Mass Rename
    def test_request_mass_rename_by_anonymous_client(self):
        c = Client()
        response = c.get('/staff_page/mass_rename')
        self.assertEqual(302, response.status_code)

    def test_request_mass_rename_by_logged_normal_client(self):
        user = self.create_test_user()
        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/mass_rename')
        self.assertEqual(302, response.status_code)

    def test_request_mass_rename_by_logged_staff_no_perm_client(self):
        user = self.create_test_user()
        user.is_staff = True
        user.save()
        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/mass_rename')
        self.assertEqual(302, response.status_code)

    def test_request_mass_rename_by_logged_staff_with_perm_client(self):
        user = self.create_test_user()
        user.is_staff = True
        permission = Permission.objects.get(codename='mass_rename')
        user.user_permissions.add(permission)
        user.save()
        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/mass_rename')
        self.assertEqual(200, response.status_code)

    # Configuration
    def test_request_mass_rename_by_anonymous_client(self):
        c = Client()
        response = c.get('/staff_page/configuration')
        self.assertEqual(302, response.status_code)

    def test_request_mass_rename_by_logged_normal_client(self):
        user = self.create_test_user()
        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/configuration')
        self.assertEqual(302, response.status_code)

    def test_request_mass_rename_by_logged_staff_no_perm_client(self):
        user = self.create_test_user()
        user.is_staff = True
        user.save()
        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/configuration')
        self.assertEqual(302, response.status_code)

    def test_request_mass_rename_by_logged_staff_with_perm_client(self):
        user = self.create_test_user()
        user.is_staff = True
        permission = Permission.objects.get(codename='change_configurations')
        user.user_permissions.add(permission)
        user.save()
        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/configuration')
        self.assertEqual(200, response.status_code)
