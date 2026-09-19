import random
from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel
from typing import Annotated, Any, Literal
from fastapi import FastAPI, Query, Path, Body, Cookie, Header, Response, status, Form, File, UploadFile
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import AfterValidator, Field, HttpUrl
from uuid import UUID
from datetime import datetime, time, timedelta

app = FastAPI()

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


class BaseUser(BaseModel):
    email: str
    username: str

class UserIn(BaseUser):
    password: str

# class UserIn(BaseModel):
#     email: str
#     password: str
#     username: str

# class UserOut(BaseModel):
#     email: str
#     username: str

class Cookies(BaseModel):
    model_config = {"extra": "forbid"}
    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None

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


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
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

# @app.post("/items/")
# async def create_item(item: Item):
#     item_dict = item.model_dump()

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

# @app.put("/items/{item_id}")
# async def read_items(
#     item_id: UUID,
#     start_datetime: Annotated[datetime, Body()],
#     end_datetime: Annotated[datetime, Body()],
#     process_after: Annotated[timedelta, Body()],
#     repeat_at: Annotated[time | None, Body()] = None,
# ):
#     start_process = start_datetime + process_after
#     duration = end_datetime - start_process
#     return {
#         "item_id": item_id,
#         "start_datetime": start_datetime,
#         "end_datetime": end_datetime,
#         "process_after": process_after,
#         "repeat_at": repeat_at,
#         "start_process": start_process,
#         "duration": duration,
#     }

# @app.get("/items/")
# async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
#     return {"ads_id": ads_id}

# @app.get("/items/")
# async def read_items(
#     strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
# ):
#     return {"strange_header": strange_header}

# @app.get("/items/")
# async def read_items(cookies: Annotated[Cookies, Cookie()]):
#     return cookies

# @app.post("/items/")
# async def create_item(item: Item) -> Item:
#     return item

# @app.get("/items/")
# async def read_items() -> list[Item]:
#     return [
#         Item(name="Portal Gun", price=42.0),
#         Item(name="Plumbus", price=32.0),
#     ]

# not convienient in most cases
# @app.post("/user/", response_model=UserOut )
# async def add_user(user: UserIn) -> Any:
#     return user 

# @app.post("/user/")
# async def create_user(user: UserIn) -> BaseUser:
#     return user

# @app.get("/portal")
# async def get_portal(teleport: bool = False) -> Response:
#     if teleport:
#         return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
#     return JSONResponse(content={"message": "Here's your interdimensional portal."})

# The same would happen if you had something like a union between different types where one or more of them are not valid Pydantic types
# this fails because the type annotation is not a Pydantic type and is not just a single Response class or subclass, 
# it's a union (any of the two) between a Response and a dict.
@app.get("/portal", response_model=None) # it will casue error in response model is removed 
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return {"message": "Here's your interdimensional portal."}

# remove the value which as unset and have default value none
# @app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
# async def read_item(item_id: str):
#     return items[item_id]

class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type: str = "car"


class PlaneItem(BaseItem):
    type: str = "plane"
    size: int


items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}

@app.get("/keyword-weights/", response_model=dict[str, float])
async def read_keyword_weights():
    return {"foo": 2.3, "bar": 3.4}

@app.get("/items/{item_id}", response_model=PlaneItem | CarItem)
async def read_item(item_id: str):
    return items[item_id]

# HTTP status code
# 100 - 199 = Information, response cannot have body
# 200 - 299 = Successful
# 300 - 399 = Redirection
# 400 - 499 = Client error
# 500 - 599 = Server error

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}

# @app.post("/login/")
# async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
#     return {"username": username}

class FormData(BaseModel):
    model_config = {"extra": "forbid"} # If a client tries to send some extra data, they will receive an error response.
    username: str
    password: str

@app.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data

# @app.post("/files/")
# async def create_file(file: Annotated[bytes | None, File()] = None):
#     if not file:
#         return {"message": "No file sent"}
#     else:
#         return {"file_size": len(file)}


# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile | None = None):
#     if not file:
#         return {"message": "No upload file sent"}
#     else:
#         return {"filename": file.filename}

# multiple file upload with Additional metadata

@app.post("/files/")
async def create_files(
    files: Annotated[list[bytes], File(description="Multiple files as bytes")],
):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
):
    return {"filenames": [file.filename for file in files]}