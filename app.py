from flask import Flask, flash, session, request, url_for, redirect, render_template
from pymongo import Connection
from utils import *
from functools import wraps

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
                return redirect('login')
            return f(*args, **kwargs)
        return inner
    return decorate

#register a user with username and password. Dict in form {str: username, int: salt, list: ints: private stall wall ids, list: ints: public stall wall ids, list: strings: friends}
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
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
        return render_template("login.html")
    else:
        if request.form["b"] == "Start Poopin'":
            user = authenticate(request.form["email"], request.form["password"], db)
            if user:
                # Loops over dictionary, creates new session element for each key
                for key in user.keys():
                    session[key] = user[key]
                    session["logged_in"] = True
                print "Welcome, " + session['first_name']
                return redirect("home")
            else:
                flash("Your username or password is incorrect")
                return render_template("login.html")
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
    test = db.users.find_one( { 'email' : session['email'] } , { "_id" : False } )
    print test
    update_user(session['email'], {'conversations' : {'Niggah': 'Hey'}}, db)
    test = db.users.find_one( { 'email' : session['email'] } , { "_id" : False } )
    print test
    if request.method == "GET":
        return render_template("home.html")
    else:
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

#simple inbox to see past conversations
@app.route("/inbox", methods=["GET", "POST"])
@auth("/inbox")
def inbox():
    if request.method == "GET":
        conversations = []
        
        print "\n", session['conversations'], "\n"
        
        for key in session['conversations']:
            print key
            conversations.append(key)
       
        print conversations
        return render_template("inbox.html", conversations = conversations)
    else:
        if request.form['b'] == "New Message":
            return redirect('messages')


@app.route("/messages", methods=["GET", "POST"])
@app.route("/messages/<usr>", methods=["GET","POST"])
@auth("/messages/<usr>")
def messages(usr = None):
    if request.method == "GET":
        if usr == None:
            return render_template("messages.html", conversation=0)
        else:
            conversation = session['conversations'][usr][1]
            return render_template("messages.html", conversation=conversation, rec=usr)
    else:
        print "Here"
        if request.form['b'] == "send":
            #print "here2"
            #if usr == None:
                #print "setting user"
            usr = request.form['usr']
                #print "starting conversation"
                #print "Recep: " + usr
            x = startConversation(session['email'], usr, db)
            update_user(session['email'], {'conversations' : x['user']}, db)
            update_user(usr, {'conversations' : x['rec']}, db)
            #print "collecting message"
            l = db.users.find_one( { 'email' : session['email'] } , { "_id" : False } )
            print l
            message = request.form['textbox1']
            #print "sending message"
            session['conversations'] = sendMessage(session['email'], usr, message, db)
            conversation = session['conversations'][usr][1]
            return redirect('messages/'+usr)




#basic log out method
def logout():
    session.pop('logged_in', None)
    flash("You have been logged out")
    return redirect('home')

if __name__ == "__main__":
	app.debug = True
	app.secret_key = "shhhhhh"
	app.run()
