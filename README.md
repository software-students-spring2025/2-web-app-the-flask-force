# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

Our Task Tracker allows users to efficiently manage their daily tasks and habits, helping them stay organized, track progress, and build consistency within their own individual portals that have a user-friendly design.

## User stories

[User Stories](https://github.com/software-students-spring2025/2-web-app-the-flask-force/issues/11)

## Steps necessary to run the software

### Cloning the Repo

Open your terminal (Mac/Linux) or PowerShell(Windows)
Navigate to the directory where you want to clone the project, and clone it using:

`git clone https://github.com/software-students-spring2025/2-web-app-the-flask-force.git`

Now navigate into the newly created project directory

### Virtual Enviornment

Create a virtual enviornment for this project:

`python3 -m venv .venv`

And activate it:

`source .venv/bin/activate`

### Dependencies

Now, with the virtual enviornment created and active, install all necessesay python dependencies to it:

`pip install -r requirements.txt`

### Enviornment Variables

Copy the variables inside the example.env file into a file called .env:

`cp example.env .env`

Update all of the values to values you will use, you can choose the name of the database and the secret key!
If you are using MongoDB Atlas to host your database online, the URL should be assigned to the CONNECTION_STRING variable.

### MongoDB

Start MongoDB, it should be installed and running locally:

`brew services start mongodb-community@6.0`

### Initialize the DB

Initialize the databse by running:

`python init_db.py`

### Run the App

Start the app by using:

`python app.py`

Or if you are using an IDE like VS Code with a run button, you can run it by pressing that.
If it is sucessful you should see an output such as:

` * Running on http://127.0.0.1:5000`

### Open the App in a Browser

We reccomend using google chrome, however any browser will do. Input the http://127.0.0.1:5000 in a browser, and you should see the Log In screen of the app. 

### Start Using the App

Register an account and start using and enjoy the task manager app!


## Task boards

[Task Board - Sprint 1](https://github.com/orgs/software-students-spring2025/projects/71)

[Task Board - Sprint 2](https://github.com/orgs/software-students-spring2025/projects/114)
