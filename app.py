from flask import Flask, render_template, request, redirect, abort, url_for, make_response
from dotenv import load_dotenv
import os
import pymongo
from bson.objectid import ObjectId
import datetime
import flask_login
import flask
from flask_pymongo import PyMongo

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

users_collection = db["users"]
users_collection.create_index("email", unique = True)

db.tasks.insert_one({
    "name": "Test Task",
    "completed": False,
    "deleted": False,
    "due_date": "2025-01-01",
    "description": "This is a test task",
    "owner": "test@example.com",
    "created_time": datetime.datetime.now()
})

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
#app.config["MONGO_URI"] = os.getenv("CONNECTION_STRING")
#mongo = pymongo(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#users = {'foo@bar.tld': {'password': 'secret'}}

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    user_data = users_collection.find_one({"email": email})
    if not user_data:
        return None

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    user_data = users_collection.find_one({"email": email})
    if not user_data:
        return None

    user = User()
    user.id = email
    return user

#Currently just prints "Home" to show app working, needs to acces task collection of DB and display tasks on template (HTML)
@app.route('/')
def show_home():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    user_email = flask_login.current_user.id
    tasks = tasks_collection.find({"completed": False, "owner": user_email})
    return render_template('index.html', tasks=tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    password = request.form['password']
    user_data = users_collection.find_one({"email": email, "password": password})

    if user_data:
        user = User()
        user.id = email
        flask_login.login_user(user)

        next_page = request.args.get("next")  
        return redirect(next_page or url_for('show_home'))

    return 'Bad login'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    email = request.form['email']
    password = request.form['password']

    if users_collection.find_one({"email": email}):
        return 'User already exists'

    users_collection.insert_one({"email": email, "password": password})
    return redirect(url_for('login'))

@app.route('/protected')
@flask_login.login_required
def protected():
    return render_template('protected.html', email=flask_login.current_user.id)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))


@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form.get('task')
    due = request.form.get("due")
    description = request.form.get("description")
    user_email = flask_login.current_user.id
    if task_name and due:
        task = {
            "name": task_name,
            "completed": False,
            "deleted": False,
            "due_date": due,
            "description": description,
            "owner": user_email,
            "created_time": datetime.datetime.now()
        }
        tasks_collection.insert_one(task)
    return redirect(url_for('show_home'))

#Possible TODO: Implement a collection in the DB to store deleted tasks so they can be reinstated (or some other way to do it)
@app.route('/delete/<task_id>', methods = ['POST'])
def delete_task(task_id):
    tasks_collection.delete_one({"_id": ObjectId(task_id)})
    return redirect(url_for('show_home'))

#Code Added to change False to True,
#Possible TODO: Delete it after completed or something else visually up to you
@app.route('/complete/<task_id>')
def complete_task(task_id):
    user_email = flask_login.current_user.id
    task = tasks_collection.find_one({"_id": ObjectId(task_id), "owner": user_email})
    
    if task:
        tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"completed": True}})
    
    return redirect(url_for('show_home'))

@app.route('/completed')
def show_completed():
    user_email = flask_login.current_user.id
    completed_tasks = tasks_collection.find({"completed": True, "owner": user_email})
    return render_template('completed.html', tasks=completed_tasks)

@app.route('/readd/<task_id>')
def readd_task(task_id):
    user_email = flask_login.current_user.id
    task = tasks_collection.find_one({"_id": ObjectId(task_id), "owner": user_email, "completed": True})
    
    if task:
        tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"completed": False}})
    
    return redirect(url_for('show_home'))

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

# new page for search
@app.route('/search', methods=['GET'])
def search_tasks():
    search_term = request.args.get('search', '').strip()  # get search term
    if not search_term:
        return render_template('search.html', tasks=[], search_term="")  # empty page
    
    user_email = flask_login.current_user.id 

    # search for tasks based on input
    search_results = list(tasks_collection.find({
        "owner": user_email,
        "$or": [
            {"name": {"$regex": search_term, "$options": "i"}}, 
            {"description": {"$regex": search_term, "$options": "i"}}
        ]
    }))

    return render_template('search.html', tasks=search_results, search_term=search_term)

if __name__ == '__main__':
    app.run(debug=True)