import math
import sys
class Calculator:

    def __init__(self) -> None:
        pass
    
    def _is_valid_number(self, num: float) -> bool:
        return not math.isnan(num) and not math.isinf(num)
    
    def _would_overflow(self, current_value: float, b: float, symbol: str) -> bool:
        try:
            if symbol == "+":
                result = current_value + b 
            elif symbol == "*":
                result = current_value * b
            else:
                result = current_value / b 
            return not math.isfinite(result)
        except OverflowError:
            return True
     
    def add(self,num1:float, num2: float) -> float:
        # Check valid  number
        if not self._is_valid_number(num2):
            raise ValueError(f"invalid numer: {num2}")
        
        if self._would_overflow(num1, num2, "+"):
            raise OverflowError("Result would overflow")
        
        return num1+num2
    
    def substract(self, num1:float, num2: float) -> float:
        return self.add(num1,-num2)

    def multiply(self, num1:float, num2: float ) -> float:
        # Check valid  number
        if not self._is_valid_number(num2):
            raise ValueError(f"invalid numer: {num2}")
        
        if self._would_overflow(num1, num2, "*"):
            raise OverflowError("Result would overflow")

        return num1*num2
    
    def divide(self, num1:float, num2: float ) -> float:
        # Check valid  number
        if not self._is_valid_number(num2):
            raise ValueError(f"invalid numer: {num2}")
        if num2 == 0:
            raise ValueError("Division cannot be done with 0")
        if self._would_overflow(num1, num2, "/"):
            raise OverflowError("Result would overflow")
        
        return num1 / num2
    
    
    def clear(self):
        return 0.0

