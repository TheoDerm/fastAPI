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

ISSUES:
1. With DI and when you create a new instance for each user -> this creates problem with my current calculator. Keep it simple for now.

TO DO:
1. Difference between errors and exceptions -> see which is best suited
2. Do it for multiple users -> read about concurrency, async functions etc
3. See a bit better the testing, part

"""


from fastapi import FastAPI, HTTPException,status, Request
from typing import Dict, List, Optional
from pydantic import BaseModel
from calculator import Calculator
from dataclasses import dataclass
from datetime import datetime



app = FastAPI()
calculator = Calculator()
current_value: float = 0.0

@dataclass
class Action():
        action_type: str
        value: str
        details: str
        timestamp: str


action_history: Dict[str, List[Action]] = {}


def handle_errors(func):
        def wrapper(num: float):
                try: 
                        return func(num)        # Call the original function and return the result
                except (ValueError, OverflowError) as e:
                        raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        return wrapper

def track_action(ip: str, value: str, action: str, details: str):
        if ip not in action_history:
                action_history[ip] = []

        # New action
        new_action = Action(
                action_type= action,
                value= value,
                details = details,
                timestamp=datetime.now().isoformat()
        )

        action_history[ip].append(new_action)

        # Keep up to 50 actions
        if len(action_history[ip]) > 50:
                action_history[ip].pop(0)

def get_IP(req: Request):
        client_host = req.headers.get(
            "x-forwarded-for",
            req.client.host if req.client else "unknown"
        )
        return client_host

@app.get("/")
def root() -> Dict[str, str]:
        return {"message": "Server is working"}


@app.get("/currentValue")
def currentValue(req: Request):
        track_action(get_IP(req),"None", "get_current_value", f"value: {calculator.getCurrentValue()}")
        return {"Current Value": calculator.getCurrentValue()}

@handle_errors
@app.get("/add/{num}")
def add(num:float, req: Request ):
        result = calculator.add(num)
        track_action(get_IP(req), str(num), "add", f"{calculator.getCurrentValue() - num} + {num} = {result}")
        return result

@handle_errors
@app.get("/sub/{num}")
def sub(num:float, req:Request ):
        result = calculator.substract(num)
        track_action(get_IP(req), str(num), "subtrack", f"{calculator.getCurrentValue() + num} - {num} = {result}")
        return result
@handle_errors
@app.get("/multiply/{num}")
def multiply(num:float, req: Request ):
        result = calculator.multiply(num)
        track_action(get_IP(req), str(num),"multiply", f"{calculator.getCurrentValue() / num} * {num} = {result}")
        return result

@handle_errors
@app.get("/divide/{num}")
def divide(num:float, req:Request):
        result = calculator.divide(num)
        track_action(get_IP(req), str(num), "divide", f"{calculator.getCurrentValue() * num} / {num} = {result}")
        return result

@app.get("/clear")
def clear(req: Request):
        result = calculator.clear()
        track_action(get_IP(req),"None", "clear_output", f"value: {result}")
        return result

@app.get("/my_action_history")
def get_action_history(req: Request):
        ip = get_IP(req)
        print("Testing:", ip)
        if ip not in action_history:
                return {"Message": "No history was found for your ip"}
        
        return {
                        "ip": ip,
                        "actions": [action for action in action_history[ip]]
                }
                
        
