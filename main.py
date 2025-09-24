"""
TO DO:
1. The compute function, the variable there, does it mean we store state in the main.py.
If it existed in the Calculator.py would that mean it holds state?

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






@dataclass
class Action():
        action_type: str
        value: str
        timestamp: str

@dataclass
class User():
        uid: str
        creation_date : datetime 
        exp_date: int           # Associatted cookie expiry date
        actions: List[Action]

user_list: Dict[str,User] = {}

@asynccontextmanager
async def cleanup_users_task(app: FastAPI):
        asyncio.create_task(user_cleanup())
        yield

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
def compute(calc: Calculator, user: User) :
        try:    
                result: float =  0.0
                for action in user.actions:
                        value = action.value
                        if action.action_type == "add":
                                result = calc.add(result, float(value))
                        elif action.action_type == "subtract":
                                result = calc.substract(result,float(value))
                        elif action.action_type == "multiply":
                                result = calc.multiply(result,float(value))
                        elif action.action_type == "divide":
                                result = calc.divide(result,float(value))
                        elif action.action_type == "clear_output":
                                result = calc.clear()
                        else: 
                                raise ValueError(f"Unknown action detected: {action.action_type}")
                return result
        except (ValueError, OverflowError) as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 

def track_action(calc: Calculator, user: User, value: str, action: str):   
        
        if action == "divide" and float(value) == 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= str("Cannot divide with 0, try again"))
        # New action
        new_action = Action(
                action_type= action,
                value= value,
                # details = details,
                timestamp=datetime.now().isoformat()
        )

        user.actions.append(new_action)

        # Keep up to 50 actions
        if len(user.actions) > 50:
                user.actions.pop(0)
        
        return {"Message": "Operation Succesful"}
        


def get_user(req: Request, response: Response):
        uid = req.cookies.get("user_id")

        if not uid or uid not in user_list:
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
                        creation_date = datetime.now(),
                        exp_date= cookie_expiry_date,
                        actions= []
                )
                user_list[uid] = new_user
        return user_list[uid]





def createApp(calc: Calculator) -> FastAPI:
        app = FastAPI()
        
        @app.get("/")
        def root() -> Dict[str, str]:
                return {"Message": "Server is working"}


        @app.get("/currentValue")
        def currentValue(req: Request, response: Response):
                user = get_user(req, response)
                return track_action(calc,user,"None", "get_current_value")

        @app.get("/add/{num}")
        def add(num:float, req: Request, response: Response ):
                user = get_user(req, response)
                return track_action(calc,user, str(num), "add")

        @app.get("/sub/{num}")
        def sub(num:float, req:Request, response: Response ):
                user = get_user(req, response)
                return track_action(calc,user, str(num), "subtract")

        @app.get("/multiply/{num}")
        def multiply(num:float, req: Request, response: Response ):
                user = get_user(req, response)
                return track_action(calc,user, str(num),"multiply")

        @app.get("/divide/{num}")
        def divide(num:float, req:Request, response: Response):
                user = get_user(req, response)
                return track_action(calc,user, str(num), "divide")

        @app.get("/clear")
        def clear(req: Request, response: Response):
                user = get_user(req, response)
                return track_action(calc,user,"None", "clear_output")

        @app.get("/my_action_history")
        def get_action_history(req: Request, response: Response):
                user = get_user(req, response)
                if len(user.actions) == 0:
                        return {"Message": "No history was found for your user"}
                
                return {
                                "user_id": user.uid,
                                "actions": user.actions
                        }
        
        @app.get("/compute")
        def get_compute(req: Request, response: Response):
                user = get_user(req, response)
                return compute(calc, user)
        
        return app



if __name__ == "__main__":
        import uvicorn
        calc = Calculator()
        
        app = createApp(calc)

        uvicorn.run(app, host="127.0.0.1", port=8000)