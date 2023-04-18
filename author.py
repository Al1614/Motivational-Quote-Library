from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
from flask_app.models import user
import re

DB = "mydb"

class Author:
    
    def __init__(self, author):
        self.id = author["id"]
        self.name = author["name"]
        self.quote = author["quote"]
        self.style = author["style"]
        self.meaning = author["meaning"]
        self.created_at = author["created_at"]
        self.updated_at = author["updated_at"]
        self.user = None

    @classmethod
    def create_valid_author(cls, author_dict):
        if not cls.is_valid(author_dict):
            return False
        
        query = """INSERT INTO authors (name, quote, style, meaning, user_id) VALUES (%(name)s, %(quote)s, %(style)s, %(meaning)s, %(user_id)s);"""
        author_id = connectToMySQL(DB).query_db(query, author_dict)
        author = cls.get_by_id(author_id)

        return author

    @classmethod
    def get_by_id(cls, author_id):
        print(f"get author by id {author_id}")
        data = {"id": author_id}
        query = """SELECT authors.id, authors.created_at, authors.updated_at, quote, style, meaning, name,
                    users.id as user_id, first_name, last_name, email, password, users.created_at as uc, users.updated_at as uu
                    FROM authors
                    JOIN users on users.id = authors.user_id
                    WHERE authors.id = %(id)s;"""
        
        result = connectToMySQL(DB).query_db(query,data)
        
        print("result of query:")
        print(result)
        result = result[0]
        author = cls(result)
        
        author.user = user.User(
                {
                    "id": result["user_id"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "email": result["email"],
                    "password": result["password"],
                    "created_at": result["uc"],
                    "updated_at": result["uu"]
                }
            )

        return author

    @classmethod
    def delete_author_by_id(cls, author_id):

        data = {"id": author_id}
        query = "DELETE from authors WHERE id = %(id)s;"
        connectToMySQL(DB).query_db(query,data)

        return author_id


    @classmethod
    def update_author(cls, author_dict, session_id):

        author = cls.get_by_id(author_dict["id"])
        if author.user.id != session_id:
            flash("You have to be the author poster to update this quote.")
            return False

        if not cls.is_valid(author_dict):
            return False
        
        query = """UPDATE authors
                    SET name = %(name)s, quote = %(quote)s, style = %(style)s, meaning = %(meaning)s
                    WHERE id = %(id)s;"""
        result = connectToMySQL(DB).query_db(query,author_dict)
        author = cls.get_by_id(author_dict["id"])
        
        return author

    @classmethod
    def get_all(cls):
        query = """SELECT 
                    authors.id, authors.created_at, authors.updated_at, quote, style, meaning, name,
                    users.id as user_id, first_name, last_name, email, password, users.created_at as uc, users.updated_at as uu
                    FROM authors
                    JOIN users on users.id = authors.user_id;"""
        author_data = connectToMySQL(DB).query_db(query)
        authors = []

        for author in author_data:
            author_obj = cls(author)
            author_obj.user = user.User(
                {
                    "id": author["user_id"],
                    "first_name": author["first_name"],
                    "last_name": author["last_name"],
                    "email": author["email"],
                    "password": author["password"],
                    "created_at": author["uc"],
                    "updated_at": author["uu"]
                }
            )
            authors.append(author_obj)

        return authors

    @staticmethod
    def is_valid(author_dict):
        valid = True
        flash_string = " field is required and must be at least 3 characters."
        if len(author_dict["name"]) < 3:
            flash("name" + flash_string)
            valid = False
        if len(author_dict["quote"]) <= 2:
            flash("Quote is required.")
            valid = False
        if len(author_dict["style"]) <= 2:
            flash("Style is required.")
            valid = False
        if len(author_dict["meaning"]) <= 2:
            flash("Meaning is required.")
            valid = False

        return valid

        