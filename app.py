"""Entry point for blog flask app"""
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort


def get_db_connection():
    """Function to create a db connection object and return it."""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    """Functions to retreive and return a post content based on an input id value."""
    conn = get_db_connection()
    post_item = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    if post_item is None:
        abort(404)
    return post_item


app = Flask(__name__)
app.config["SECRET_KEY"] = "your secret key"


@app.route("/")
def index():
    """view function to display all the posts in the database on this app's homepage"""
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts").fetchall()
    conn.close()
    return render_template("index.html", posts=posts)


@app.route("/<int:post_id>")
def post(post_id):
    """Show the post with the given id, the id is an integer"""
    blog_post = get_post(post_id)
    return render_template("post.html", post=blog_post)


@app.route("/create", methods=("GET", "POST"))
def create():
    """view function allowin the user to submit a new post."""
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO posts (title, content) VALUES (?, ?)", (title, content)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))
    return render_template("create.html")


@app.route("/<int:post_id>/edit", methods=("GET", "POST"))
def edit(post_id):
    """View function to edit a blog post."""
    target_post = get_post(post_id)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            conn = get_db_connection()
            conn.execute(
                "UPDATE posts SET title = ?, content = ?" " WHERE id = ?",
                (title, content, post_id),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))

    return render_template("edit.html", post=target_post)


@app.route("/<int:delete_id>/delete", methods=("POST",))
def delete(delete_id):
    """View function to delete a target post based on a passed post.id value."""
    delete_post = get_post(delete_id)
    conn = get_db_connection()
    conn.execute("DELETE FROM posts WHERE id = ?", (delete_id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(delete_post["title"]))
    return redirect(url_for("index"))
