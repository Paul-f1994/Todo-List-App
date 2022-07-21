import os
from unicodedata import category
from flask import Flask, render_template, request, redirect, url_for
from google.cloud import ndb

client = ndb.Client()
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

class TodoList(ndb.Model):
    id = ndb.IntegerProperty()
    title = ndb.StringProperty()
    complete = ndb.BooleanProperty()
    due = ndb.StringProperty()
    category = ndb.StringProperty()

@app.route("/")
def index():
    with client.context():
        todo_list = TodoList.query().order(TodoList.id)
        return render_template("index.html", todo_list=todo_list)


@app.route("/init")
def init():
    with client.context():
        todoItem0 = TodoList(id = 0,
                        title = "buy shoes",
                        complete = False)
        todoItem0.put()
        todoItem1 = TodoList(id = 1,
                        title = "study",
                        complete = False)
        todoItem1.put()
        # ndb.delete_multi(
        #     TodoList.query().fetch(keys_only=True)
        # )
        return redirect(url_for("index"))

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    due = request.form.get("due")
    category = request.form.get("category")
    with client.context():
        todo = TodoList.query().order(-TodoList.id).get()
        if todo != None:
            new_todo = TodoList(id = todo.id + 1, title = title, complete = False, due = due, category = category)
        else:
            new_todo = TodoList(id = 0, title = title, complete = False, due = due, category = category)
        new_todo.put()
        return redirect(url_for("index"))


@app.route("/complete/<string:todo_id>")
def complete(todo_id):
    todo_id =  int(todo_id)
    with client.context():
        todo = TodoList.query().filter(TodoList.id == todo_id).get()
        todo.complete = not todo.complete
        todo.put()
        return redirect(url_for("index"))


@app.route("/delete/<string:todo_id>")
def delete(todo_id):
    todo_id =  int(todo_id)
    with client.context():
        todo = TodoList.query().filter(TodoList.id == todo_id).get()
        todo.key.delete()
        return redirect(url_for("index"))

if __name__ == "__main__":
    client
    app.run(debug=True)
