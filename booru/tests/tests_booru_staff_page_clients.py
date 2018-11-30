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
from rolepermissions.checkers import has_permission
from rolepermissions.permissions import revoke_permission
from rolepermissions.roles import assign_role, clear_roles

from booru.models import Post


class StaffPageClientsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def create_test_user(self, name="Test", password="123", is_staff=False):
        user = get_user_model().objects.create_user(name, password=password, is_staff=is_staff)
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
        user = self.create_test_user(is_staff=True)

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
        user = self.create_test_user(is_staff=True)
        clear_roles(user)
        assign_role(user, 'janitor')
        revoke_permission(user, 'mass_rename')
        self.assertFalse(has_permission(user, 'mass_rename'))

        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/mass_rename')
        self.assertEqual(302, response.status_code)

    def test_request_mass_rename_by_logged_staff_with_perm_client(self):
        user = self.create_test_user(is_staff=True)
        self.assertTrue(has_permission(user, 'mass_rename'))

        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/mass_rename')
        self.assertEqual(200, response.status_code)

    # Configuration
    def test_request_configuration_by_anonymous_client(self):
        c = Client()
        response = c.get('/staff_page/configuration')
        self.assertEqual(302, response.status_code)

    def test_request_configuration_by_logged_normal_client(self):
        user = self.create_test_user()
        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/configuration')
        self.assertEqual(302, response.status_code)

    def test_request_configuration_by_logged_staff_no_perm_client(self):
        user = self.create_test_user(is_staff=True)
        clear_roles(user)
        assign_role(user, 'janitor')
        revoke_permission(user, 'change_configurations')
        self.assertFalse(has_permission(user, 'change_configurations'))

        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/configuration')
        self.assertEqual(302, response.status_code)

    def test_request_configuration_by_logged_staff_with_perm_client(self):
        user = self.create_test_user(is_staff=True)
        self.assertTrue(has_permission(user, 'change_configurations'))
        c = Client()
        logged_in = c.login(username='Test', password='123')
        response = c.get('/staff_page/configuration')
        self.assertEqual(200, response.status_code)
