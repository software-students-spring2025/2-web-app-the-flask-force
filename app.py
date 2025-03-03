from flask import Flask, render_template, request, redirect, abort, url_for, make_response
from dotenv import load_dotenv
import os
import pymongo
from bson.objectid import ObjectId
import datetime

load_dotenv(override=True)

CONNECTION_STRING = os.environ.get("CONNECTION_STRING")
print(CONNECTION_STRING)
assert CONNECTION_STRING
DATABASE_NAME = os.environ.get("DATABASE_NAME")
print(DATABASE_NAME)
assert DATABASE_NAME

connection = pymongo.MongoClient(CONNECTION_STRING)
#print(connection)

db = connection[DATABASE_NAME]
#print(db)

tasks_collection = db["tasks"]
tasks_collection.create_index("completed")

app = Flask(__name__)

#Currently just prints "Home" to show app working, needs to acces task collection of DB and display tasks on template (HTML)
@app.route('/')
def show_home():
    tasks = tasks_collection.find({"completed": False})
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form.get('task')
    due = request.form.get("due")
    description = request.form.get("description")
    if task_name and due:
        task = {
            "name": task_name,
            "completed": False,
            "deleted": False,
            "due_date": due,
            "description": description,
            "created_time": datetime.datetime.now()
        }
        tasks_collection.insert_one(task)
    return redirect(url_for('show_home'))

#Possible TODO: Implement a collection in the DB to store deleted tasks so they can be reinstated (or some other way to do it)
@app.route('/delete/<task_id>')
def delete_task(task_id):
    tasks_collection.delete_one({"_id": ObjectId(task_id)})
    return redirect(url_for('show_home'))

#Code Added to change False to True,
#Possible TODO: Delete it after completed or something else visually up to you
@app.route('/complete/<task_id>')
def complete_task(task_id):
    task = tasks_collection.find_one({"_id": ObjectId(task_id)})
    
    if task:
        task["completed"] = True
        db["completed"].insert_one(task)
        tasks_collection.delete_one({"_id": ObjectId(task_id)})
    
    return redirect(url_for('show_home'))

@app.route('/completed')
def show_completed():
    completed_tasks = db["completed"].find({"completed": True})
    return render_template('completed.html', tasks=completed_tasks)

#forms that will allow user to edit the name, description and due date.
@app.route('/edit/<task_id>', methods=['POST'])
def edit_task(task_id):
    new_name = request.form.get('new_name')
    new_description = request.form.get('new_description')
    new_due = request.form.get('new_due')
    print(request.form)
    
    #structure i found to only update fields that the user chooses to edit, not all at once
    update_fields = {}
    
    if new_name:
        update_fields["name"] = new_name
    if new_description:
        update_fields["description"] = new_description
    if new_due:
        update_fields["due_date"] = new_due
    print(update_fields)
    if update_fields:
        tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": update_fields})
    
    return redirect(url_for('show_home'))
    
if __name__ == '__main__':
    app.run(debug=True)
