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
    id: Optional[int] = None
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
        cursor.execute(""" SELECT * FROM posts ORDER BY id """)
        posts = cursor.fetchall()
        if posts:
            return utilities.prepare_response(True, 'Retrieved all posts successfully.', posts)
        else:
            return utilities.prepare_response(False, 'Failed to fetch all posts')
    except Exception as err:
        return utilities.prepare_response(False, 'Error occurred: ' + str(err))


@app.get("/api/post/{id}")
async def get_posts(id: int):
    try:
        cursor.execute(" SELECT * FROM posts WHERE id=(%s) ", (str(id)))
        retrieved_post = cursor.fetchone()
        if retrieved_post:
            return utilities.prepare_response(True, 'Successfully fetched a post', retrieved_post)
        else:
            return utilities.prepare_response(False, 'Failed to fetch a post')
    except Exception as err:
        return utilities.prepare_response(False, 'Error occurred: ' + str(err))


@app.post("/api/create_post/", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    try:
        cursor.execute(" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ",
                       (post.title, post.content, post.published))
        new_post = cursor.fetchone()
        conn.commit()
        if new_post:
            return utilities.prepare_response(True, 'Successfully created a post', new_post)
        else:
            return utilities.prepare_response(False, 'Failed to create a post')
    except Exception as err:
        return utilities.prepare_response(False, 'Error occurred: ' + str(err))


@app.put("/api/update_post/", status_code=status.HTTP_200_OK)
async def update_post(post: Post):
    try:
        for item in [post.id, post.title, post.content, post.published]:
            if item is None:
                return utilities.prepare_response(False, 'Please pass valid id, title, '
                                                         'content and published data for a post.')

        cursor.execute(" UPDATE posts SET title=(%s), content=(%s), "
                       "published=(%s) WHERE id=(%s) RETURNING * ",
                       (post.title, post.content, post.published, str(post.id)))
        updated_post = cursor.fetchone()
        conn.commit()
        if updated_post:
            return utilities.prepare_response(True, 'Successfully updated a post', updated_post)
        else:
            return utilities.prepare_response(False, 'Failed to update a post')
    except Exception as err:
        return utilities.prepare_response(False, 'Error occurred: ' + str(err))


@app.delete("/api/delete_post/{id}", status_code=status.HTTP_200_OK)
async def delete_post(id: int):
    try:
        cursor.execute(" DELETE FROM posts WHERE id=(%s) RETURNING * ", (str(id)))
        deleted_post = cursor.fetchone()
        conn.commit()
        if deleted_post:
            return utilities.prepare_response(True, 'Successfully deleted a post', deleted_post)
        else:
            return utilities.prepare_response(False, 'Failed to delete a post')
    except Exception as err:
        return utilities.prepare_response(False, 'Error occurred: ' + str(err))
