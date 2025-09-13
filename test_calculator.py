import unittest
import math
from calculator import Calculator

class TestCalculator(unittest.TestCase):
    
    def setUp(self):
        """Set up a new calculator instance before each test"""
        self.calc = Calculator()
    
    def test_initial_value(self):
        """Test that calculator starts at 0"""
        self.assertEqual(self.calc.getCurrentValue(), 0.0)
    
    def test_add_positive_number(self):
        """Test addition with positive numbers"""
        result = self.calc.add(5.5)
        self.assertEqual(result, 5.5)
        self.assertEqual(self.calc.getCurrentValue(), 5.5)
    
    def test_add_negative_number(self):
        """Test addition with negative numbers"""
        result = self.calc.add(-3.2)
        self.assertEqual(result, -3.2)
    
    def test_subtract_positive_number(self):
        """Test subtraction with positive numbers"""
        self.calc.add(10.0)
        result = self.calc.substract(3.0)
        self.assertEqual(result, 7.0)
    
    def test_multiply_positive_numbers(self):
        """Test multiplication with positive numbers"""
        self.calc.add(5.0)
        result = self.calc.multiply(2.0)
        self.assertEqual(result, 10.0)
    
    def test_divide_valid_number(self):
        """Test division with valid numbers"""
        self.calc.add(10.0)
        result = self.calc.divide(2.0)
        self.assertEqual(result, 5.0)
    
    def test_divide_by_zero_raises_error(self):
        """Test that division by zero raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.calc.divide(0.0)
        self.assertEqual(str(context.exception), "Division cannot be done with 0")
    
    def test_add_invalid_number_nan(self):
        """Test that adding NaN raises ValueError"""
        with self.assertRaises(ValueError):
            self.calc.add(float('nan'))
    
    def test_add_invalid_number_inf(self):
        """Test that adding infinity raises ValueError"""
        with self.assertRaises(ValueError):
            self.calc.add(float('inf'))
    
    def test_clear_resets_value(self):
        """Test that clear operation resets to zero"""
        self.calc.add(15.0)
        self.calc.clear()
        self.assertEqual(self.calc.getCurrentValue(), 0.0)
    
    def test_sequence_of_operations(self):
        """Test a sequence of mixed operations"""
        self.calc.add(10.0)      # 10
        self.calc.substract(2.0) # 8
        self.calc.multiply(3.0)  # 24
        self.calc.divide(4.0)    # 6
        self.assertEqual(self.calc.getCurrentValue(), 6.0)

if __name__ == '__main__':
    unittest.main()