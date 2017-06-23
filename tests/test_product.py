# test_bucketlist.py

import unittest
import os
import json
from app import create_app, db

class ProductTestCase(unittest.TestCase):
    """This class represents the product test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.product = {'name': 'Marigold'}

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234"):
        """This helper method helps register a test use."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user_data)
    
    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)

    def test_product_creation(self):
        """Test API can create a product (POST request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/products/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.product)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Marigold', str(res.data))

    def test_api_can_get_all_products(self):
        """Test API can get a product (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/products/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.product)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/products/',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        self.assertIn('Marigold', str(res.data))

    def test_api_can_get_product_by_id(self):
        """Test API can get a single product by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/products/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.product)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/products/{}'.format(result_in_json['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Marigold', str(result.data))

    def test_product_can_be_edited(self):
        """Test API can edit an existing product. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/products/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name':'Danone'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/products/1',
            headers=dict(Authorization="Bearer " + access_token),
            data={"name":"Marigold"})
        self.assertEqual(rv.status_code, 200)
        results = self.client().get(
            '/products/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Marigold', str(results.data))

    def test_product_deletion(self):
        """Test API can delete an existing product. (DELETE request). """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/products/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name':'Danone'})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete(
            '/products/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        result = self.client().get(
            '/products/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == "__main__":
    unittest.main()

    