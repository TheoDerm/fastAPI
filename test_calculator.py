import sys
import unittest
import math
from calculator import Calculator

class TestCalculator(unittest.TestCase):
    
    def setUp(self):
        """Set up a new calculator instance before each test"""
        self.calc = Calculator()
    
    def test_add_positive_numbers(self):
        """Test addition with positive numbers"""
        result = self.calc.add(5.5, 3.2)
        self.assertAlmostEqual(result, 8.7, places=7)
    
    def test_add_negative_numbers(self):
        """Test addition with negative numbers"""
        result = self.calc.add(-5.0, -3.0)
        self.assertEqual(result, -8.0)
    
    def test_add_mixed_numbers(self):
        """Test addition with positive and negative numbers"""
        result = self.calc.add(10.0, -3.5)
        self.assertAlmostEqual(result, 6.5, places=7)
    
    def test_subtract_positive_numbers(self):
        """Test subtraction with positive numbers"""
        result = self.calc.substract(10.0, 3.0)
        self.assertEqual(result, 7.0)
    
    def test_multiply_positive_numbers(self):
        """Test multiplication with positive numbers"""
        result = self.calc.multiply(4.0, 2.5)
        self.assertEqual(result, 10.0)
    
    def test_multiply_by_zero(self):
        """Test multiplication by zero"""
        result = self.calc.multiply(5.0, 0.0)
        self.assertEqual(result, 0.0)
    
    def test_divide_valid_numbers(self):
        """Test division with valid numbers"""
        result = self.calc.divide(10.0, 2.0)
        self.assertEqual(result, 5.0)
    
    def test_divide_by_zero_raises_error(self):
        """Test that division by zero raises ValueError"""
        with self.assertRaises(ValueError) as context:
            self.calc.divide(10.0, 0.0)
        self.assertEqual(str(context.exception), "Division cannot be done with 0")
    
    def test_divide_negative_numbers(self):
        """Test division with negative numbers"""
        result = self.calc.divide(-10.0, 2.0)
        self.assertEqual(result, -5.0)
    
    def test_clear_returns_zero(self):
        """Test that clear operation returns zero"""
        result = self.calc.clear()
        self.assertEqual(result, 0.0)
    
    def test_add_invalid_number_nan(self):
        """Test that adding NaN raises ValueError"""
        with self.assertRaises(ValueError):
            self.calc.add(5.0, float('nan'))
    
    def test_add_invalid_number_inf(self):
        """Test that adding infinity raises ValueError"""
        with self.assertRaises(ValueError):
            self.calc.add(5.0, float('inf'))
    
    def test_overflow_protection_addition(self):
        """Test overflow protection for very large numbers"""
        large_num = sys.float_info.max
        with self.assertRaises(OverflowError):
            self.calc.add(large_num, large_num)
    
    def test_overflow_protection_multiplication(self):
        """Test overflow protection for multiplication"""
        large_num = sys.float_info.max / 2
        with self.assertRaises(OverflowError):
            self.calc.multiply(large_num, 3.0)

if __name__ == '__main__':
    unittest.main()