import unittest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request, Response
from main import createApp, Calculator, User, Action, get_user, track_action, compute
from datetime import datetime
import uuid

class TestMainAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test client and calculator before each test"""
        self.calc = Calculator()
        self.app = createApp(self.calc)
        self.client = TestClient(self.app)
    
    def test_root_endpoint(self):
        """Test the root endpoint returns correct message"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"Message": "Server is working"})
    
    def test_add_endpoint_valid_number(self):
        """Test add endpoint with valid number"""
        response = self.client.get("/add/5.5")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Operation Succesful", response.json()["Message"])
    
    def test_subtract_endpoint(self):
        """Test subtract endpoint"""
        response = self.client.get("/sub/3.2")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Operation Succesful", response.json()["Message"])
    
    def test_multiply_endpoint(self):
        """Test multiply endpoint"""
        response = self.client.get("/multiply/2.5")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Operation Succesful", response.json()["Message"])
    
    def test_divide_endpoint_valid_number(self):
        """Test divide endpoint with valid number"""
        response = self.client.get("/divide/2.0")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Operation Succesful", response.json()["Message"])
    
    def test_divide_by_zero_returns_error(self):
        """Test divide by zero returns HTTP error"""
        response = self.client.get("/divide/0.0")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot divide with 0", response.json()["detail"])
    
    def test_clear_endpoint(self):
        """Test clear endpoint"""
        response = self.client.get("/clear")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Operation Succesful", response.json()["Message"])
    
    def test_current_value_endpoint(self):
        """Test current value endpoint"""
        response = self.client.get("/currentValue")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Operation Succesful", response.json()["Message"])
    
    def test_action_history_empty(self):
        """Test action history endpoint with no actions"""
        response = self.client.get("/my_action_history")
        self.assertEqual(response.status_code, 200)
        self.assertIn("No history was found", response.json()["Message"])
    
    def test_compute_endpoint_empty_history(self):
        """Test compute endpoint with no actions"""
        response = self.client.get("/compute")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 0.0)
    
    def test_sequence_of_operations(self):
        """Test a sequence of operations"""
        operations = [
            ("/add/10", 200),
            ("/multiply/2", 200),
            ("/sub/5", 200),
            ("/divide/3", 200)
        ]
        
        for endpoint, expected_status in operations:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, expected_status)
    
    def test_cookie_creation(self):
        """Test that cookies are created for new users"""
        response = self.client.get("/")
        self.assertIn("user_id", response.cookies)
        user_id = response.cookies.get("user_id")
        self.assertIsNotNone(user_id)
        self.assertTrue(len(user_id) > 0)
    
    def test_same_user_across_requests(self):
        """Test that same user is maintained across requests"""
        # First request
        response1 = self.client.get("/add/5")
        user_id1 = response1.cookies.get("user_id")
        
        # Second request with same session
        response2 = self.client.get("/add/3")
        user_id2 = response2.cookies.get("user_id")
        
        self.assertEqual(user_id1, user_id2)

class TestHelperFunctions(unittest.TestCase):
    
    def setUp(self):
        self.calc = Calculator()
    
    def test_compute_empty_actions(self):
        """Test compute function with empty action list"""
        user = User(
            uid="test123",
            creation_date=datetime.now(),
            exp_date=600,
            actions=[]
        )
        result = compute(self.calc, user)
        self.assertEqual(result, 0.0)
    
    def test_compute_sequence_of_actions(self):
        """Test compute function with a sequence of actions"""
        user = User(
            uid="test123",
            creation_date=datetime.now(),
            exp_date=600,
            actions=[
                Action(action_type="add", value="5", timestamp="2024-01-15T10:00:00"),
                Action(action_type="multiply", value="3", timestamp="2024-01-15T10:01:00"),
                Action(action_type="subtract", value="2", timestamp="2024-01-15T10:02:00")
            ]
        )
        result = compute(self.calc, user)
        self.assertEqual(result, (5 * 3) - 2)  # (5 + 0) * 3 - 2 = 13
    
    def test_track_action_valid_operation(self):
        """Test track_action with valid operation"""
        user = User(
            uid="test123",
            creation_date=datetime.now(),
            exp_date=600,
            actions=[]
        )
        result = track_action(self.calc, user, "5", "add")
        self.assertEqual(len(user.actions), 1)
        self.assertEqual(user.actions[0].action_type, "add")
        self.assertEqual(user.actions[0].value, "5")
    
    def test_track_action_division_by_zero(self):
        """Test track_action with division by zero"""
        user = User(
            uid="test123",
            creation_date=datetime.now(),
            exp_date=600,
            actions=[]
        )
        with self.assertRaises(Exception) as context:
            track_action(self.calc, user, "0", "divide")
        self.assertIn("Cannot divide with 0", str(context.exception))

class TestUserManagement(unittest.TestCase):
    
    def test_user_actions_limit(self):
        """Test that user actions are limited to 50"""
        user = User(
            uid="test123",
            creation_date=datetime.now(),
            exp_date=600,
            actions=[]
        )
        
        # Add 60 actions
        for i in range(60):
            action = Action(action_type="add", value=str(i), timestamp="2024-01-15T10:00:00")
            user.actions.append(action)
        
        # Should keep only last 50
        self.assertEqual(len(user.actions), 50)
        self.assertEqual(user.actions[0].value, "10")  # First 10 were removed
        self.assertEqual(user.actions[-1].value, "59")  # Last action is 59

if __name__ == '__main__':
    unittest.main()