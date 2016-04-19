from django.test import TestCase

class GeneralTests(TestCase):
    def test_general(self):
        self.assertEqual([], [])
