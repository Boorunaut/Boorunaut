from django.test import TestCase
from django.test.utils import override_settings
from booru.utils import space_splitter
from booru.utils import compare_strings
from booru.templatetags.number_converter import number_converter

class TemplateTagsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def test_number_converter(self):
        self.assertEqual(number_converter(1), '1')
        self.assertEqual(number_converter(10), '10')
        self.assertEqual(number_converter(100), '100')
        self.assertEqual(number_converter(1000), '1K')
        self.assertEqual(number_converter(2500), '2.5K')
        self.assertEqual(number_converter(80010), '80K')
        self.assertEqual(number_converter(100000), '100K')
        self.assertEqual(number_converter(1000000), '1M')
