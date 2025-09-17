"""
TO DO:
1. Difference between errors and exceptions -> see which is best suited
2. See a bit better the testing, part
3. Test the app and read about async more - do I need to handle tasks when the app shutsdown?

"""


from fastapi import FastAPI, HTTPException,status, Request, Response
from typing import Dict, List, Optional
from pydantic import BaseModel
from calculator import Calculator
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def cleanup_users_task(app: FastAPI):
        asyncio.create_task(user_cleanup())
        yield

app = FastAPI()

@dataclass
class Action():
        action_type: str
        value: str
        details: str
        timestamp: str

@dataclass
class User():
        uid: str
        calculator: Calculator  # Associated calculator
        creation_date : datetime 
        exp_date: int           # Associatted cookie expiry date
        actions: List[Action]

user_list: Dict[str,User] = {}



async def user_cleanup():
        while True:
                await asyncio.sleep(3*60)       # Run every 3 minutes

                current_time = datetime.now()
                cleanups_counter = 0

                expired_users = [                       #It is more secure, timedelta handles some error prone things automatically, time zones, leap seconds etc.
                        uid for uid, user in user_list.items()          
                        if current_time > user.creation_date + timedelta(seconds=user.exp_date)         
                ]

                for uid in expired_users:
                        del user_list[uid]
                        cleanups_counter += 1
                if cleanups_counter > 0:
                        print(f"Cleaned up {cleanups_counter} expired users. Total users: {len(user_list)}")

def track_action(user: User, value: str, action: str):
        try: 
                calculator = user.calculator
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

                user.actions.append(new_action)

                # Keep up to 50 actions
                if len(user.actions) > 50:
                        user.actions.pop(0)
                
                return result
        except (ValueError, OverflowError) as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def get_user(req: Request, response: Response):
        uid = req.cookies.get("user_id")

        if not uid:
                uid = str(uuid.uuid4())
                cookie_expiry_date = 10*60 

                # Create the cookie
                response.set_cookie(
                        key="user_id",
                        value=uid,
                        max_age=cookie_expiry_date,  
                        httponly=True,
                        samesite="lax"
                )

                #Create new user
                new_user = User(
                        uid = uid,
                        calculator= Calculator(),
                        creation_date = datetime.now(),
                        exp_date= cookie_expiry_date,
                        actions= []
                )
                user_list[uid] = new_user
        return user_list[uid]






@app.get("/")
def root() -> Dict[str, str]:
        return {"message": "Server is working"}


@app.get("/currentValue")
def currentValue(req: Request, response: Response):
        user = get_user(req, response)
        return track_action(user,"None", "get_current_value")

@app.get("/add/{num}")
def add(num:float, req: Request, response: Response ):
        user = get_user(req, response)
        return track_action(user, str(num), "add")

@app.get("/sub/{num}")
def sub(num:float, req:Request, response: Response ):
        user = get_user(req, response)
        return track_action(user, str(num), "subtract")

@app.get("/multiply/{num}")
def multiply(num:float, req: Request, response: Response ):
        user = get_user(req, response)
        return track_action(user, str(num),"multiply")

@app.get("/divide/{num}")
def divide(num:float, req:Request, response: Response):
        user = get_user(req, response)
        return track_action(user, str(num), "divide")

@app.get("/clear")
def clear(req: Request, response: Response):
        user = get_user(req, response)
        return track_action(user,"None", "clear_output")

@app.get("/my_action_history")
def get_action_history(req: Request, response: Response):
        user = get_user(req, response)
        if len(user.actions) == 0:
                return {"Message": "No history was found for your user"}
        
        return {
                        "user_id": user.uid,
                        "actions": user.actions
                }
               

if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
