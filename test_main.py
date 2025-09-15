import unittest
from fastapi.testclient import TestClient
from main import app
from calculator import Calculator

class TestMainAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test client before each test"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test the root endpoint returns correct message"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Server is working"})
    
    def test_current_value_endpoint(self):
        """Test current value endpoint returns initial value"""
        response = self.client.get("/currentValue")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"Current Value": 0.0})

    def test_add_endpoint_valid_number(self):
        """Test add endpoint with valid number"""
        response = self.client.get("/add/5.5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 5.5)

    
    def test_subtract_endpoint_valid_number(self):
        """Test subtract endpoint with valid number"""
        response = self.client.get("/sub/3.2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), -3.2)
    
    def test_multiply_endpoint_valid_number(self):
        """Test multiply endpoint after setting value"""
        self.client.get("/add/4.0")  # Set to 4 first
        response = self.client.get("/multiply/2.5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 10.0)
    
    def test_divide_endpoint_valid_number(self):
        """Test divide endpoint with valid number"""
        self.client.get("/add/10.0")  # Set to 10 first
        response = self.client.get("/divide/2.0")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 5.0)
    
    def test_divide_by_zero_returns_error(self):
        """Test divide by zero returns HTTP error"""
        response = self.client.get("/divide/0.0")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Division cannot be done with 0", response.json()["detail"])
    
    def test_clear_endpoint_resets_value(self):
        """Test clear endpoint resets calculator"""
        self.client.get("/add/15.0")  # Set to 15
        response = self.client.get("/clear")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 0.0)
        
        # Verify current value is actually reset
        current_response = self.client.get("/currentValue")
        self.assertEqual(current_response.json(), {"Current Value": 0.0})
    
    def test_invalid_input_returns_error(self):
        """Test that invalid input returns appropriate error"""
        response = self.client.get("/add/abc")  # Not a number
        self.assertEqual(response.status_code, 422)  # FastAPI validation error

if __name__ == '__main__':
    unittest.main()