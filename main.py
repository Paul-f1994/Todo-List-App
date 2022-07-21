import os
from flask import Flask, render_template, request, redirect, url_for
from google.cloud import ndb

client = ndb.Client()
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

colors = ["#EBF6FA", "#FAE8E8", "#D3E3D6", "#FBEFE3", "#D9E6EC", "#ECDCDC", "#E3E2E1"]

class TodoList(ndb.Model):
    id = ndb.IntegerProperty()
    title = ndb.StringProperty()
    complete = ndb.BooleanProperty()
    due = ndb.StringProperty()
    category = ndb.StringProperty()
    priority = ndb.IntegerProperty()

@app.route("/")
def index():
    with client.context():
        todo_lists = {}
        todos = TodoList.query().order(TodoList.id)
        for todo in todos:
            if todo.category not in todo_lists:
                todo_lists[todo.category] = []
            todo_lists[todo.category].append(todo)
            todo_lists[todo.category].sort(key=lambda x: x.priority, reverse=False)
        return render_template("index.html", todo_lists=todo_lists, colors=colors)


@app.route("/clear")
def init():
    with client.context():
        ndb.delete_multi(
            TodoList.query().fetch(keys_only=True)
        )
    return redirect(url_for("index"))

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    due = request.form.get("due")
    category = request.form.get("category")
    priority = int(request.form.get("priority") if request.form.get("priority").isnumeric() else 3)
    with client.context():
        todo = TodoList.query().order(-TodoList.id).get()
        if todo != None:
            new_todo = TodoList(id = todo.id + 1, title = title, complete = False, due = due, category = category, priority = priority)
        else:
            new_todo = TodoList(id = 0, title = title, complete = False, due = due, category = category, priority = priority)
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


@app.route("/updateAll/<string:todo_id>", methods=["POST"])
def updateDueAndCategory(todo_id):
    todo_id =  int(todo_id)
    title = request.form.get("updateTitle")
    due = request.form.get("updateDue")
    category = request.form.get("updateCategory")
    priority = int(request.form.get("updatePriority") if request.form.get("updatePriority").isnumeric() else 3)
    with client.context():
        todo = TodoList.query().filter(TodoList.id == todo_id).get()
        todo.title = title
        todo.due = due
        todo.category = category
        todo.priority = priority
        todo.put()
    return redirect(url_for("index"))


@app.route("/delete/<string:todo_id>")
def delete(todo_id):
    todo_id = int(todo_id)
    with client.context():
        todo = TodoList.query().filter(TodoList.id == todo_id).get()
        todo.key.delete()
    return redirect(url_for("index"))

if __name__ == "__main__":
    client
    app.run(debug=True)
