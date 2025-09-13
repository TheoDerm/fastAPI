"""
Key concepts:

1. The API endpoints syntax
2. The decorators: Add some extra funtionality to the code, without relating directly to the function itself: 
   Example: def repeat_decorator(times):
                def decorator(func):
                        def wrapper(name):
                        for _ in range(times):
                                print("Before the function call") #This is the important part
                                result = func(name)
                                print("After the function call")  #This is the important part
                        return result
                        return wrapper
                return decorator

3. Dependency Injection: a) Eliminates Global State Problems -> each user has its own calculator
                         b) Better testability as before I had a global calculator that was being used by other tests
                         c) Better resource management: Before  -> Global calculator lived in memory for ever
                                                        With DI -> Controlled instance lifetime (per request)
                         d) Scalability, each request gets its own isolated calculator instance 
                         d) Explicit dependencies: Before I had a hidden gloab dependency, with DI it's clear what each endpoint requires
                         e) Better error handling: With DI you can add dependency-specific error handling 

                         
QUESTIONS:
1. Doesn't working with DI mean that I will need to use async functions since we are serving multiple users now concurrentlly?                         
"""






from fastapi import FastAPI, HTTPException,status, Depends
from typing import Union
from pydantic import BaseModel
from calculator import Calculator
app = FastAPI()
current_value: float = 0.0
# calculator = Calculator()

def handle_errors(func):
        def wrapper(num: float):
                try: 
                        return func(num)        # Call the original function and return the result
                except (ValueError, OverflowError) as e:
                        raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return wrapper

# Change the design to work with Dependency Injection:
def get_calculator() -> Calculator:
        return Calculator()


@app.get("/")
def root():
        return {"message": "Server is working"}


@app.get("/currentValue")
def currentValue(calc: Calculator = Depends(get_calculator)):
        return {"Current Value": calc.getCurrentValue()}

@app.get("/add/{num}")
@handle_errors
def add(num:float, calc: Calculator = Depends(get_calculator)):
        return calc.add(num)

@app.get("/sub/{num}")
@handle_errors
def sub(num:float, calc: Calculator = Depends(get_calculator)):
        return calc.substract(num)

@app.get("/multiply/{num}")
@handle_errors
def multiply(num:float, calc: Calculator = Depends(get_calculator)):
        return calc.multiply(num)

@app.get("/divide/{num}")
@handle_errors
def divide(num:float, calc: Calculator = Depends(get_calculator)):
        return calc.divide(num)

@app.get("/clear")
def clear(calc: Calculator = Depends(get_calculator)):
        return calc.clear()
