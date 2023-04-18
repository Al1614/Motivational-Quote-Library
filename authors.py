from flask import Flask, render_template, session, redirect, request
from flask_app import app
from flask_app.models.user import User
from flask_app.models.author import Author
from flask import flash

@app.route("/authors/home")
def authors_home():
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.")
        return redirect("/")
    
    user = User.get_by_id(session["user_id"])
    authors = Author.get_all()

    return render_template("home.html", user=user, authors=authors)

@app.route("/authors/<int:author_id>")
def show_detail(author_id):
    user = User.get_by_id(session["user_id"])
    author = Author.get_by_id(author_id)
    return render_template("author_detail.html", user=user, author=author)

@app.route("/authors/create")
def author_create_page():
    user = User.get_by_id(session["user_id"])
    return render_template("create_author.html", user = user)

@app.route("/authors/edit/<int:author_id>")
def author_edit_page(author_id):
    user = User.get_by_id(session["user_id"])
    author = Author.get_by_id(author_id)
    return render_template("edit_author.html",  user = user, author = author)

@app.route("/authors", methods=["POST"])
def create_authors():
    valid_author = Author.create_valid_author(request.form)
    if valid_author:
        return redirect(f'/authors/{valid_author.id}')
    return redirect('/authors/create')

@app.route("/authors/<int:author_id>", methods=["POST"])
def update_author(author_id):

    valid_author = Author.update_author(request.form, session["user_id"])

    if not valid_author:
        return redirect(f"/authors/edit/{author_id}")
        
    return redirect(f"/authors/{author_id}")

@app.route("/authors/delete/<int:author_id>")
def delete_by_id(author_id):
    Author.delete_author_by_id(author_id)
    return redirect("/authors/home")