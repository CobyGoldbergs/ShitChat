from flask import Flask, flash, session, request, url_for, redirect, render_template
from pymongo import Connection
from utils import authenticate, create_wall, add_comment, validate, register_user, update_user, search_wall, update_wall, up_vote, add_friend
from functools import wraps
import pymongo
import operator

app = Flask(__name__)

# mongo 
conn = Connection()
db = conn['users']

#walls = db.walls.find()
#for w in walls:
 #   print w

#db.users.remove()

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

@app.route("/about", methods=["GET", "POST"])
def about():
    if request.method == "GET":
        users = db.users.find()
        count = 0
        for u in users:
            if u['logged_in'] == True:
                count += 1
        return render_template("about.html", logged_in = count)
    else:
        if request.form["b"] == "Log In":
            return redirect("login")
        elif request.form["b"] == "Sign Up":
            return redirect("register")
    

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
        if request.form['b'] == "Create a Wall!":
            return redirect("create_wall")
        if request.form['b'] == "Log Out":
            return logout()
        if request.form['b'] == "Search Wall":
            x = search_wall(request.form, db)
            if x == []:
                flash('invalid search')
                return redirect('home')
            return render_template("search_results.html", walls = x)
        if request.form['b'] == "Search User":
            add_friend(request.form, session, db)
            user = db.users.find_one( { 'email' : session['email'] } , { "_id" : False })
            session['friends'] = user['friends']
            return redirect('home')
            
            

#simple inbox to see past conversations
#@app.route("/inbox", methods=["GET", "POST"])
#@auth("/inbox")
#def inbox():

@app.route("/create_wall", methods=["GET", "POST"])
def create_w():
    if request.method == "GET":
        return render_template("create.html")
    else:
        if request.form['b'] == "Create a Wall!":
            return redirect("create_wall")
        if request.form["b"] == "Start Poopin'":
            res = create_wall(request.form, session, db)
            success = "Wall " + request.form["name"] + " created"
            if res == success:
                return redirect('home')
            else:
                return redirect('create_wall')
        if request.form['b'] == "search":
            x = search_wall(request.form, db)
            if x == []:
                flash('invalid search')
                return redirect('home')
            return render_template("search_results.html", walls = x)

@app.route("/wall/<wall_id>", methods=["GET", "POST"])
def wall_page(wall_id):
    wall = db.walls.find_one( { 'wall_id' : wall_id } )
    upped = False
    if wall_id in session['walls_upped']:
        upped = True
    if request.method == "GET":
        return render_template("stall.html", wall=wall, upped=upped)
    else:
        if request.form["b"] == "Log Out":
            return logout()
        if request.form['b'] == "Create a Wall!":
            return redirect("create_wall")
        if request.form["b"] == "Post":
            resp = add_comment(request.form, wall_id, session, db)
            if resp == "Comment field left blank":
                return redirect(url_for('wall_page', wall_id=wall_id))
            else:
                return redirect(url_for('wall_page', wall_id=wall_id))
        if request.form["b"] == "up_vote":
            new_ses = up_vote(wall_id, session, db)
            session['walls_upped'] = new_ses
            return redirect(url_for('wall_page', wall_id=wall_id))
        if request.form['b'] == "search":
            x = search_wall(request.form, db)
            if x == []:
                flash('invalid search')
                return redirect('home')
            return render_template("search_results.html", walls = x)

@app.route("/canvas", methods=["GET", "POST"])
def canvas():
    if request.method == "GET":
        return render_template("canvas.html")


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
