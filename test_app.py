# Import the Flask application instance from your main app module.
from app import app
# Import the unittest module for creating and running tests.
import unittest
# Import json for parsing JSON responses.
import json

# Define a test case class for your JWKS server by inheriting from unittest.TestCase.
class JWKSserverTestCase(unittest.TestCase):
    # Set up method is called before each test method to set up test environment.
    def setUp(self):
        # Initialize a test client for your Flask application.
        self.app = app.test_client()
        # Enable testing mode. Exceptions will be propagated rather than handled by the Flask app.
        self.app.testing = True

    # Test method for the JWKS endpoint to ensure it's functioning as expected.
    def test_jwks_endpoint(self):
        # Send a GET request to the /jwks endpoint.
        response = self.app.get('/jwks')
        # Assert that the HTTP status code of the response is 200 (OK).
        self.assertEqual(response.status_code, 200)
        # Parse the response data from JSON format.
        data = json.loads(response.data)
        # Assert that the response data is a dictionary (as expected for JWKS).
        self.assertTrue(isinstance(data, dict))

    # Test method for the /auth endpoint without the "expired" query parameter.
    def test_auth_endpoint_without_expired(self):
        # Send a POST request to the /auth endpoint.
        response = self.app.post('/auth')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)

    # Test method for the /auth endpoint with the "expired" query parameter set to true.
    def test_auth_endpoint_with_expired(self):
        # Send a POST request to the /auth endpoint with the "expired" query parameter.
        response = self.app.post('/auth?expired=true')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # Assert that a 'token' is present in the response data, even for expired tokens.
        self.assertIn('token', data)

# This block checks if the script is being run directly and then calls unittest.main() 
# which runs all of the tests.
if __name__ == '__main__':
    unittest.main()
