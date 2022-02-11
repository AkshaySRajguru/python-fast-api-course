from typing import Optional

from fastapi import FastAPI
# from fastapi.params import Body
from pydantic import BaseModel


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Hello World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    """
    Receives HTTP requests in the paths / and /items/{item_id}.
    Both paths take GET operations (also known as HTTP methods)

    :param int item_id: item_id
    :param str q: optional string query
    :return dict: {"item_id", "query"}
    """
    return {"item_id": item_id, "q": q}


@app.get("/api/posts/")
async def get_posts():
    return {"post": "this is the post 1"}


# @app.post("/api/create/posts")
# async def create_post(body: dict = Body(...)):
#     return {"title": body["title"], "content": body["content"]}

@app.post("/api/create/posts")
async def create_post(post: Post):
    return post.dict()
