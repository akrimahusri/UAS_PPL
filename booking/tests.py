from django.test import TestCase


class BookingViewsTests(TestCase):
    def test_landing_page_ok(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
