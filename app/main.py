from typing import Optional
from random import randrange
import time

from fastapi import FastAPI, HTTPException, status
# from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

import utilities


class Post(BaseModel):
    # id: Optional[int] = None
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None


app = FastAPI()

# database connection
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi',
                                user='postgres', password='test123',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('*** Database connection is successful!')
        break
    except Exception as e:
        print('*** Database connection failed! Error occurred :' + str(e))
        time.sleep(2)


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


@app.get("/api/all_posts/")
async def get_all_posts():
    try:
        cursor.execute(""" SELECT * FROM posts""")
        posts = cursor.fetchall()
        if posts:
            result = utilities.prepare_response(True, 'Retrieved all posts successfully.', posts)
        else:
            result = utilities.prepare_response(False, 'Failed to fetch all posts')
        return result
    except Exception as err:
        return utilities.prepare_response(False, 'Error occurred: ' + str(err))


@app.get("/api/post/{id}")
async def get_posts(id: int):
    try:
        cursor.execute(" SELECT * FROM posts WHERE id=(%s) ", (str(id)))
        retrieved_post = cursor.fetchone()
        return utilities.prepare_response(True, 'Successfully fetched a post', retrieved_post)
    except Exception as err:
        return utilities.prepare_response(False, 'Error occurred: ' + str(err))


@app.post("/api/create_post/", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    try:
        cursor.execute(" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ",
                       (post.title, post.content, post.published))
        new_post = cursor.fetchone()
        return utilities.prepare_response(True, 'Successfully created a post', new_post)
    except Exception as err:
        return utilities.prepare_response(False, 'Error occurred: ' + str(err))


# @app.put("/api/update_post/", status_code=status.HTTP_200_OK)
# async def update_post(post: Post):
#     try:
#         post_dict = post.dict()
#         print(post_dict)
#         is_id_passed = "id" in post_dict.keys()
#         if not is_id_passed:
#             return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                                  detail=f'pass id of post in the body of the request!')
#         result = None
#         for i, p in enumerate(my_posts):
#             if p['id'] == int(post_dict["id"]):
#                 my_posts[i] = post_dict
#                 result = True
#         if result:
#             return {"message": "post updated successfully!", "data": post_dict}
#         else:
#             return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id:{id} is not found!')
#     except Exception as e:
#         return HTTPException(status_code=status.HTTP_200_OK, detail=f'Error occurred: {e}')
#
#
# @app.delete("/api/delete_post/{id}", status_code=status.HTTP_200_OK)
# async def delete_post(id: int):
#     try:
#         result = None
#         for i, p in enumerate(my_posts):
#             if p["id"] == int(id):
#                 my_posts.pop(i)
#                 result = True
#         if result:
#             return {"message": f"post with id:{id} deleted successfully!"}
#         else:
#             return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id:{id} is not found!')
#     except Exception as e:
#         return HTTPException(status_code=status.HTTP_200_OK, detail=f'Error occurred: {e}')
