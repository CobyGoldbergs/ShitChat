from flask import Flask, flash, session, request, url_for, redirect, render_template
from pymongo import Connection
from utils import authenticate, create_wall, add_comment, validate, register_user, update_user, search_wall
from functools import wraps
import pymongo

app = Flask(__name__)

# mongo 
conn = Connection()
db = conn['users']

#walls = db.walls.find()
#for w in walls:
 #   print w

def auth(page):
    def decorate(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if 'logged_in' not in session:
                flash("You must be logged in to see this page")
                return redirect('login')
            return f(*args, **kwargs)
        return inner
    return decorate

#register a user with username and password. Dict in form {str: username, int: salt, list: ints: private stall wall ids, list: ints: public stall wall ids, list: strings: friends}
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        users = db.users.find()
        count = 0
        for u in users:
            if u['logged_in'] == True:
                count += 1
        return render_template("register.html", logged_in = count)
    else:
        if request.form["b"] == "Start Poopin'":
            message = validate(request.form, db)
            if message == 'Valid':
                register_user(request.form, db)
                flash('Account created')
                return redirect("login")
            else:
                return render_template("register.html", message = message)
        elif request.form["b"] == "Log In":
            return redirect("login")
        elif request.form["b"] == "About":
            return redirect("about")
        else:
            return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        users = db.users.find()
        count = 0
        for u in users:
            if u['logged_in'] == True:
                count += 1
        return render_template("login.html", logged_in = count)
    else:
        if request.form["b"] == "Start Poopin'":
            user = authenticate(request.form["email"], request.form["password"], db)
            if user:
                # Loops over dictionary, creates new session element for each key
                for key in user.keys():
                    session[key] = user[key]
                print "Welcome, " + session['first_name']
                return redirect("home")
            else:
                flash("Your username or password is incorrect")
                return redirect('login')
        elif request.form["b"] == "Cancel":
            return redirect("login")
        elif request.form["b"] == "Sign Up":
            return redirect("register")
        elif request.form["b"] == "About":
            return redirect("about")

#home pages includes: list of trending stall walls, each of which is a link to the wall, list of private walls (also links), list of online friends, button to see inbox of messages
#can later add random wall button
#to access existing walls i thought it'd be a list of links?
@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
@auth("/home") #To be readded once login is there
def home():
    if request.method == "GET":
        walls = db.walls.find().sort('up_votes', pymongo.DESCENDING)
        return render_template("home.html", walls=walls)
    else:
        print request.form['b']
        if request.form['b'] == "Inbox":
             return redirect("inbox")
        if request.form['b'] == "Create Wall":
            #there needs to be a way for the info to be inserted, with fields for wall name and description
            res = create_wall(request.form['wall_name'], request.form['description'])
            if res == "Name required":
                flash(res)
                return redirect('home')
            else:
                flash(res)
                return redirect('home') #or maybe move them to the newly created wall page
        if request.form['b'] == "Log Out":
            return logout()
        if request.form['b'] == "search":
            print 'hey'
            x = search_wall(request.form, db)
            return render_template("search_results.html", walls = x)

#simple inbox to see past conversations
#@app.route("/inbox", methods=["GET", "POST"])
#@auth("/inbox")
#def inbox():

@app.route("/create_wall", methods=["GET", "POST"])
def create_w():
    if request.method == "GET":
        return render_template("create_wall.html")
    else:
        if request.form["b"] == "Start Poopin'":
            res = create_wall(request.form["name"], request.form["description"],session, db)
            success = "Wall " + request.form["name"] + " created"
            if res == success:
                print "yay!"
                return redirect('home')
            else:
                return redirect('create_wall')

@app.route("/wall/<wall_id>", methods=["GET", "POST"])
def wall_page(wall_id):
    x = int(wall_id)
    wall = db.walls.find_one( { 'wall_id' : x } ) 
    print wall
    return redirect('home')

#basic log out method
def logout():
    session.pop('logged_in', None)

    user = db.users.find_one( { 'email' : session['email'] } , { "_id" : False } )

    update_user(user['email'], {'logged_in': False}, db)

    flash("You have been logged out")
    return redirect('home')

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
