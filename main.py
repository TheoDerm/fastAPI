from fastapi import FastAPI, HTTPException,status
from typing import Union
from pydantic import BaseModel
from calculator import Calculator
app = FastAPI()
calculator = Calculator()

def handle_errors(func):
        def wrapper(num: float):
                try: 
                        return func(num)
                except (ValueError, OverflowError) as e:
                        raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return wrapper


current_value: float = 0.0
@app.get("/")
def root():
        return {"message": "Server is working"}


@app.get("/currentValue")
def currentValue():
        return {"Current Value": calculator.getCurrentValue()}

@app.get("/add/{num}")
@handle_errors
def add(num:float):
        return calculator.add(num)

@app.get("/sub/{num}")
@handle_errors
def sub(num:float):
        return calculator.substract(num)

@app.get("/multiply/{num}")
@handle_errors
def multiply(num:float):
        return calculator.multiply(num)

@app.get("/divide/{num}")
@handle_errors
def divide(num:float):
        return calculator.divide(num)

@app.get("/clear")
def clear():
        calculator.current_value = 0
        return calculator.current_value
