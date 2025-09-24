### Running the application ###

To run the application run: `python .\main.py`

### Overview of the application ###
This a web API Calculator. It has two different classes. The `main.py` is used for API management and the `calculator.py` is used for the logic behind the calculator.

The project uses the FastAPI framework. If you are not familiar you can read more about it [here](https://fastapi.tiangolo.com/)

### Workflow of the application ###
1. User visitis the site and goes ahead to execute an action through the designated endpoints.

2. Application retrieves the user's details:
    1. It first checks if the request coming has an associated cookie with it that belongs to the already identified users. If not it creates a new user and assigns him a UID.

3. Application tracks the user's submitted action and holds a list of the actions submitted.

4. Users wants to compute the sequence and visits the `/compute` endpoint.

5. Application executes the `compute` function, retrieves the user's list of actions along with the details of each one and then dynimically computes the result based on that history.

### Project Key Takeways ###

### Future Work ### 
