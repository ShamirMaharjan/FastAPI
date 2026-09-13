from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel

app = FastAPI()

# declare your data model as a class that inherits from BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class ModelName(str, Enum):
    ramnet = "ramnet"
    harrynet = "harrynet"
    lenet = "lenet"

# @ is a decorator it basically uses the function below it
# app is the instance of FastAPI
# get is the operation
# in python HTTP methods are called operations like POST, GET, PUT, DELETE
# path is the path inside the " 
# This is our "path operation function":
# path: is /.
# operation: is get.
# function: is the function below the "decorator" (below @app.get("/")).
# It will be called by FastAPI whenever it receives a request to the URL "/" using a GET operation.
# In this case, it is an async function.
# You could also define it as a normal function instead of async def:
# You can return a dict, list, singular values as str, int, etc.
# You can also return Pydantic models

@app.get("/")
async def root():
    return {"message": "hello shamir"}


# Order matters
# Because path operations are evaluated in order, 
# you need to make sure that the path for /users/me is declared before the one for /users/{user_id}:
# Otherwise, the path for /users/{user_id} would match also for /users/me, 
# "thinking" that it's receiving a parameter user_id with a value of "me".
@app.get("/user/me")
async def get_current_user():
    return {"message": "Shamir"}

@app.get("/user/{id}")
async def get_user_by_id(id: int):
    return {"message": id}

# here q and short are optional query parameters. by default q is none and short is false, if we dont keep None so the parameter 
# will be required.

# @app.get("/items/{item_id}")
# async def get_item_by_id(item_id: str, q: str | None = None, short: bool=False):
#     """Return the requested item identifier."""
#     item = {"item_id": item_id}
#     if q:
#         item.update({"q": q})
#     if not short:
#         item.update(
#             {"description": "This is an amazing item that has a long description"}
#         )
#     return item

# here needy is a required query parameter, if it is not passed in url then the error will be shown.

@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item

fake_items_db = [{"key1": "value1"}, {"key2":"value2"},{"key3": "value3"}, {"key4":"value4"}]

@app.get("/items/")
async def read_items(skip: int=0, limit: int=5):
    return fake_items_db[skip:limit+skip]

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.ramnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()

    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})

    return item_dict

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result