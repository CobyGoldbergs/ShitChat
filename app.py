from flask import Flask, flash, session, request, url_for
from pymongo import Connection
from utils import create_item, authenticate, create_wall

app = Flask(__name__)

# mongo 
conn = Connection()
db = conn['users']

def auth(page):
    def decorate(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if 'logged_in' not in session:
                flash("You must be logged in to see this page")
                return redirect('/')
            return f(*args, **kwargs)
        return inner
    return decorate

#register a user with username and password. Dict in form {str: username, int: salt, list: ints: private stall wall ids, list: ints: public stall wall ids, list: strings: friends}
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return redirect("register")
    else:
        message = validate(request.form['username'], request.form['password'], db)
        if message == 'Valid':
            register_user(request.form, db):
            flash('Account created')
            return redirect("login")
        else:
            flash(message)
            return redirect("register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect("login")
    else:
        user = authenticate(request.form["username"], request.form["password"], db)
        if user:
            # Loops over dictionary, creates new session element for each key
            for key in user.keys():
                session[key] = user[key]
                session["logged_in"] = True
                flash("Welcome, " + session['username'])
                return redirect("home")
        else:
            flash("Your username or password is incorrect")
            return redirect('login')

#home pages includes: list of trending stall walls, each of which is a link to the wall, list of private walls (also links), list of online friends, button to see inbox of messages
#can later add random wall button
#to access existing walls i thought it'd be a list of links?
@app.route("/home", methods=["GET", "POST"])
@auth("/home")
def home():
    if request.method == "GET":
        return render_template("home.html")
    else:
        if request.form['b'] == "Inbox":
             return redirect("inbox")
        if request.form['b'] == "Create Wall":
            #there needs to be a way for the info to be inserted
            res = create_wall(request.form['name'], request.form['description'])
            if res == "Name required":
                flash(res)
                return redirect('home')
            else:
                flash(res)
                return redirect('home') #or maybe move them to the newly created wall page

#simple inbox to see past conversations
@app.route("/inbox", methods=["GET", "POST"])
@auth("/inbox")
def inbox():



if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
