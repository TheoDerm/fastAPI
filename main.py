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
2. Do it for multiple users 
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
users_list: Dict[str, Calculator] = {}

def track_action(ip: str, value: str, action: str):
        try: 
                if ip not in users_list:
                        users_list[ip] = Calculator()
                        action_history[ip] = []
                calculator = users_list[ip]
                initial_value = calculator.getCurrentValue()
                
                if action == "get_current_value":
                        result= initial_value
                        details = f"value: {initial_value}"
                elif action == "add":
                        result = calculator.add(float(value))
                        details = f"{initial_value} + {value} = {result}"
                elif action == "subtract":
                        result = calculator.substract(float(value))
                        details = f"{initial_value} - {value} = {result}"
                elif action == "multiply":
                        result = calculator.multiply(float(value))
                        details = f"{initial_value} * {value} = {result}"
                elif action == "divide":
                        result = calculator.divide(float(value))
                        details = f"{initial_value} / {value} = {result}" 
                elif action == "clear_output":
                        result = calculator.clear()
                        details = f"value: {result}"
                else: 
                        raise ValueError(f"Unknown action: {action}")
                
                # New action
                new_action = Action(
                        action_type= action,
                        value= str(value),
                        details = details,
                        timestamp=datetime.now().isoformat()
                )

                action_history[ip].append(new_action)

                # Keep up to 50 actions
                if len(action_history[ip]) > 50:
                        action_history[ip].pop(0)
                
                return result
        except (ValueError, OverflowError) as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
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
        ip = get_IP(req)
        return track_action(ip,"None", "get_current_value")

@app.get("/add/{num}")
def add(num:float, req: Request ):
        return track_action(get_IP(req), str(num), "add")

@app.get("/sub/{num}")
def sub(num:float, req:Request ):
        return track_action(get_IP(req), str(num), "subtract")

@app.get("/multiply/{num}")
def multiply(num:float, req: Request ):
        return track_action(get_IP(req), str(num),"multiply")

@app.get("/divide/{num}")
def divide(num:float, req:Request):
        return track_action(get_IP(req), str(num), "divide")

@app.get("/clear")
def clear(req: Request):
        return track_action(get_IP(req),"None", "clear_output")

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
                

if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
