import random
from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel
from typing import Annotated, Any, Literal
from fastapi import FastAPI, Query, Path, Body
from pydantic import AfterValidator, Field, HttpUrl
from uuid import UUID
from datetime import datetime, time, timedelta

app = FastAPI()

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}

# declare your data model as a class that inherits from BaseModel

class Image(BaseModel):
    name: str
    url: HttpUrl

class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None,
        description="The description of the item",
        max_length=200,
        examples=["A very nice Item"] # can declare example in field
    )
    price: float = Field(gt=0, description="The price must be greater than 0")
    tax: float | None = None
    tags: set[str] = set()
    image: list[Image] | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"} # doesnt allow to keep any other query except for these filterParams class

    limit: int = Field(100, gt=0, le=100) #field(default, aru)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at" # While a regular type hint like str allows any text string, Literal["read", "write"] forces the value to be "literally" either "read" or "write".
    tags: list[str] = []

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

# @app.get("/items/{item_id}")
# async def read_user_item(item_id: str, needy: str):
#     item = {"item_id": item_id, "needy": needy}
#     return item

fake_items_db = [{"key1": "value1"}, {"key2":"value2"},{"key3": "value3"}, {"key4":"value4"}]

# @app.get("/items/")
# async def read_items(skip: int=0, limit: int=5):
#     return fake_items_db[skip:limit+skip]

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

# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item,  q: Annotated[str | None, Query(min_length=3, max_length=20, pattern="fixedquery$")]= None):
#     result = {"item_id": item_id, **item.model_dump()}
#     if q:
#         result.update({"q": q})
#     return result

# query parameter q that can appear multiple times in the URL
# @app.get("/items/")
# async def read_items(q: Annotated[list[str] | None, Query()] = None):
#     query_items = {"q": q}
#     return query_items

# @app.get("/items/")
# async def read_items(q: Annotated[list[str] | None, Query()] = ["hello", "shamir"]):
#     query_items = {"q": q}
#     return query_items


# 
# @app.get("/items/")
# async def read_items(
#     q: Annotated[
#         str | None,
#         Query(
#             alias="item-query",
#             title="Query string",
#             description="Query string for the items to search in the database that have a good match",
#             min_length=3,
#             max_length=50,
#             pattern="^fixedquery$",
#             deprecated=True,
#         ),
#     ] = None,
# ):
#     results: dict[str, Any] = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results["q"] = q
#     return results

def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id

# @app.get("/items/{item_id}")
# async def read_items(
#     item_id: Annotated[
#         int,
#         Path(
#             title="id of an item",
#             description="this should be a id of an item as item_id path paramter",
#         ),
#     ],
#     id: Annotated[str | None, AfterValidator(check_valid_id)] = None
# ):
#     if id:
#         item = data.get(id)
#     else:
#         id, item = random.choice(list(data.items()))
#     return {"id": id, "name": item}

# with ge=1, item_id will need to be an integer number "greater than or equal" to 1
# @app.get("/items/{item_id}")
# async def read_items(
#     item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)], q: str
# ):
#     results: dict[str, Any]  = {"item_id": item_id}
#     if q:
#         results.update({"q": q})
#     return results

# @app.get("/items/")
# async def read_items(filter_query: Annotated[FilterParams, Query()]):
#     return filter_query

class User(BaseModel):
    username: str 
    full_name: str | None = None

# @app.put("/items/{item_id}")
# async def update_item(
#     item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
#     q: str | None = None,
#     item: Item | None = None,
# ):
#     results: dict[str, Any] = {"item_id": item_id}
#     if q:
#         results.update({"q": q})
#     if item:
#         results.update({"item": item})
#     return results

# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item, user: User, importance: Annotated[str, Body()], q: str | None):
#     results = {"item_id": item_id, "item": item, "user": user, "importance": importance, "q": q}
#     return results

# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
#     results = {"item_id": item_id, "item": item}
#     return results

# @app.put("/items/{item_id}")
# async def update_item(
#     item_id: int,
#     item: Annotated[
#         Item,
#         Body(
#             examples=[
#                 {
#                     "name": "Foo",
#                     "description": "A very nice Item",
#                     "price": 35.4,
#                     "tax": 3.2,
#                 }
#             ],
#         ),
#     ],
# ):
#     results = {"item_id": item_id, "item": item}
#     return results

@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }