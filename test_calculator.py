import unittest
from fastapi.testclient import TestClient
from main import app, calculator
from calculator import Calculator

class TestMainAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and reset calculator before each test"""
        self.client = TestClient(app)
        # Reset the global calculator to ensure test isolation
        calculator.current_value = 0.0
    
    def tearDown(self):
        """Clean up after each test"""
        calculator.current_value = 0.0
    
    def test_root_endpoint(self):
        """Test the root endpoint returns correct message"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Server is working"})
    
    def test_current_value_endpoint_initial(self):
        """Test current value endpoint returns initial value (0.0)"""
        response = self.client.get("/currentValue")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"Current Value": 0.0})
    
    def test_add_endpoint_valid_number(self):
        """Test add endpoint with valid number"""
        response = self.client.get("/add/5.5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 5.5)
    
    def test_add_sequence_preserves_state(self):
        """Test that sequential operations preserve state (benefit of global state)"""
        response1 = self.client.get("/add/10.0")
        self.assertEqual(response1.json(), 10.0)
        
        response2 = self.client.get("/add/5.0")
        self.assertEqual(response2.json(), 15.0)
        
        # Verify current value reflects the accumulated state
        current_response = self.client.get("/currentValue")
        self.assertEqual(current_response.json(), {"Current Value": 15.0})
    
    def test_subtract_endpoint(self):
        """Test subtract endpoint"""
        # Set initial value first
        self.client.get("/add/20.0")
        response = self.client.get("/sub/5.0")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 15.0)
    
    def test_multiply_endpoint(self):
        """Test multiply endpoint"""
        self.client.get("/add/4.0")  # Set to 4 first
        response = self.client.get("/multiply/3.0")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 12.0)
    
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
    
    def test_complex_operation_sequence(self):
        """Test a complex sequence of operations"""
        operations = [
            ("/add/10", 10.0),
            ("/multiply/2", 20.0),
            ("/sub/5", 15.0),
            ("/divide/3", 5.0),
            ("/add/100", 105.0)
        ]
        
        for endpoint, expected_result in operations:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), expected_result)
        
        # Final verification
        current_response = self.client.get("/currentValue")
        self.assertEqual(current_response.json(), {"Current Value": 105.0})
    
    def test_invalid_input_returns_validation_error(self):
        """Test that invalid input returns appropriate error"""
        response = self.client.get("/add/abc")  # Not a number
        self.assertEqual(response.status_code, 422)  # FastAPI validation error
    
    def test_error_handling_decorator_works(self):
        """Test that the @handle_errors decorator works for all endpoints"""
        # Test division by zero
        response = self.client.get("/divide/0.0")
        self.assertEqual(response.status_code, 400)
        
        # Test invalid number (should be caught by FastAPI before reaching our decorator)
        response = self.client.get("/add/invalid")
        self.assertEqual(response.status_code, 422)

class TestCalculatorGlobalState(unittest.TestCase):
    """Tests specifically for the global state behavior"""
    
    def setUp(self):
        calculator.current_value = 0.0
    
    def test_global_state_persistence(self):
        """Test that the calculator maintains state across multiple requests"""
        # This test demonstrates the "feature" of global state
        with TestClient(app) as client:
            client.get("/add/5.0")
            client.get("/add/3.0")
            response = client.get("/currentValue")
            self.assertEqual(response.json(), {"Current Value": 8.0})
    
    def test_state_is_shared_between_tests(self):
        """Demonstration that state is shared (this is why we reset in setUp)"""
        # This test shows why we need to reset in setUp/tearDown
        calculator.current_value = 100.0  # Modify state
        
        # The next test will start with this modified state unless we reset

if __name__ == '__main__':
    unittest.main()