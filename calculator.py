import math
import sys
class Calculator:

    def __init__(self) -> None:
        self.current_value = 0.0
    
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
     
    def add(self, num: float) -> float:
        # Check valid  number
        if not self._is_valid_number(num):
            raise ValueError(f"invalid numer: {num}")
        
        if self._would_overflow(self.current_value, num, "+"):
            raise OverflowError("Result would overflow")
        
        self.current_value += num
        return self.current_value
    
    def substract(self, num:float) -> float:
        return self.add(-num)

    def multiply(self, num:float ) -> float:
        # Check valid  number
        if not self._is_valid_number(num):
            raise ValueError(f"invalid numer: {num}")
        
        if self._would_overflow(self.current_value, num, "*"):
            raise OverflowError("Result would overflow")
        self.current_value *= num
        return self.current_value
    
    def divide(self, num:float ) -> float:
        # Check valid  number
        if not self._is_valid_number(num):
            raise ValueError(f"invalid numer: {num}")
        if num == 0:
            raise ValueError("Division cannot be done with 0")
        if self._would_overflow(self.current_value, num, "/"):
            raise OverflowError("Result would overflow")
        self.current_value /= num
        return self.current_value
    
    def getCurrentValue(self) -> float:
        return self.current_value
    
    def clear(self):
        self.current_value = 0.0
        return self.current_value

