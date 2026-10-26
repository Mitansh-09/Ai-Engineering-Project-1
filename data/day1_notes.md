# Day 1 — FastAPI Basics

FastAPI is a Python web framework used to build APIs quickly. It is built on top of Starlette and Pydantic, which gives it high performance and automatic data validation.

## Creating an app
```python
from fastapi import FastAPI
app = FastAPI()
```

## Basic route (GET request)
```python
@app.get("/")
def home():
    return {"status": "alive"}
```

## Running the server
```bash
uvicorn main:app --reload
```
The `--reload` flag restarts the server automatically when code changes, useful during development.

## Automatic docs
FastAPI generates interactive API documentation automatically at `/docs` (Swagger UI). This lets you test endpoints directly from the browser without writing separate test code.

## Path parameters
Used to capture values from the URL itself.
```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}
```
FastAPI automatically converts `item_id` to an integer and validates it. If someone passes text instead of a number, FastAPI returns an error automatically.

## Query parameters
Used to pass optional values after a `?` in the URL, like `/items?skip=0&limit=10`.
```python
@app.get("/items/")
def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

## Request body (POST)
Used to send structured data (usually JSON) to the server, like form submissions.
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
def create_item(item: Item):
    return item
```
Pydantic validates incoming data automatically — if `price` is missing or is not a number, FastAPI rejects the request before it reaches your code.

## PUT vs POST vs DELETE
- **POST** creates a new resource
- **PUT** updates/replaces an existing resource completely
- **DELETE** removes a resource

All three can use path or query parameters along with a request body.

## Key takeaway
FastAPI's biggest advantage over plain Flask is automatic validation (via Pydantic) and automatic interactive docs, which saves a lot of manual error-checking code.