import time

from fastapi import FastAPI, Path, HTTPException
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///app.db")
Session = sessionmaker(bind=engine)
my_session = Session()

Base = declarative_base()

app = FastAPI()

class Blog(Base):
    __tablename__ = "blogs"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    author = sqlalchemy.Column(sqlalchemy.String)
    page_number = sqlalchemy.Column(sqlalchemy.String)


    def __str__(self):
        return f'{self.name} by {self.author}'


Base.metadata.create_all(engine)


class BlogSchemaIn(BaseModel):
    name: str = None
    author: str = None
    page_number: int = None

class BlogSchemaOut(BaseModel):
    id: int
    name: str = None
    author: str = None
    page_number: int = None


@app.get("/")
def home_page():
    return {"Hello": "World"}

@app.get("/blogs/", tags=["Blog"])
def get_all_blogs():
    blogs = my_session.query(Blog).all()
    blog_object_list = []

    for blog in blogs:
        blog_dict = BlogSchemaOut(**blog.__dict__)
        blog_object_list.append(blog_dict)

    return blog_object_list

@app.post("/blogs/", tags=["Blog"])
def create_new_blog(blog: BlogSchemaIn):
    blog = Blog(**blog.__dict__)
    my_session.add(blog)
    my_session.commit()
    print(blog, "saved") # don't remove this line
    blog = BlogSchemaOut(**blog.__dict__)
    return blog


@app.get("/blogs/{pk}", tags=["Blog"])
def get_specific_blog(pk: int = Path(default=None)):
    if not pk:
        raise HTTPException(
            status_code = 400,
            detail = "Enter valid blog id"
        )

    
    blog = my_session.query(Blog).get(pk)
    
    if not blog:
        raise HTTPException(
            status_code = 404,
            detail = f"Blog with id {pk} not found"
        )

    blog = BlogSchemaOut(**blog.__dict__)
    return blog


@app.put("/blogs/{pk}",tags=["Blog"])
def edit_speicfic_blog(*, pk: int = Path(default=None), blog: BlogSchemaIn):
    if not pk:
        raise HTTPException(400, "please specify a valid blog id")

    blog_instance = my_session.query(Blog).get(pk)

    if not blog_instance:
        raise HTTPException(404, f"blog with id {pk} not found")

    if blog.name:
        blog_instance.name = blog.name
    
    if blog.author:
        blog_instance.author = blog.author

    if blog.page_number:
        blog_instance.page_number = blog.page_number

    my_session.commit()
    print(blog_instance, "Updated")
    blog = BlogSchemaOut(**blog_instance.__dict__)
    return blog
    

@app.delete("/blogs/{pk}", tags=["Blog"])
def delete_specific_blog(pk: int = Path(default=None)):
    if not pk:
        raise HTTPException(404, "Please enter a valid blog id")

    blog = my_session.query(Blog).get(pk)
    my_session.delete(blog)
    my_session.commit()

    return {
        "message": f"blog of id {pk} has been deleted"
    }



    
