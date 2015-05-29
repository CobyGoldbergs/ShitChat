from flask import Flask, flash, session, request, url_for, redirect, render_template
from pymongo import MongoClient
from utils import *
from functools import wraps
import pymongo
import operator
import string
import json

app = Flask(__name__)

# mongo 
#conn = Connection()
db = MongoClient()['users']


#walls = db.walls.find()
#for w in walls:
 #   print w

#db.walls.remove()


#db.messages.remove()



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
    users = db.users.find()
    count = 0
    for u in users:
        if u['logged_in'] == True:
            count += 1
    if request.method == "GET":
        return render_template("login.html", logged_in = count)
    else:
        if request.form["b"] == "Start Poopin'":
            user = authenticate(request.form["email"], request.form["password"], db)
            if user:
                # Loops over dictionary, creates new session element for each key
                for key in user.keys():
                    session[key] = user[key]
                return redirect("home")
            else:
                return render_template("login.html", message = "Username or password is incorrect", logged_in = count)
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
    test = db.users.find_one( { 'email' : session['email'] } , { "_id" : False } )
    print test
    update_user(session['email'], {'conversations' : {'Niggah': 'Hey'}}, db)
    test = db.users.find_one( { 'email' : session['email'] } , { "_id" : False } )
    print test
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
@app.route("/inbox", methods=["GET", "POST"])
@auth("/inbox")
def inbox():
    if request.method == "GET":
        messages = db.messages.find()
        conversations = []
        for conversation in messages:
            for user in conversation['tag']:
                if user == session['email']:
                    conversations.append(conversation)
        return render_template("inbox.html", conversations = conversations, sender = session['email'])
    else:
        if request.form['b'] == "New Message":
            return redirect('messages')
        if request.form["b"] == "Log Out":
            return logout()
        if request.form['b'] == "Create a Wall!":
            return redirect("create_wall")
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


@app.route("/messages", methods=["GET", "POST"])
@app.route("/messages/<usr>", methods=["GET","POST"])
@auth("/messages/<usr>")
def messages(usr = None):
    if request.method == "GET":
        if usr == None:
            messages = db.messages.find()
            for message in messages:
                print message
            return render_template("messages.html", conversation=0)
        else:
            usr = usr.split("_")
            usr.sort()
            print usr
            while "" in usr:
                usr.remove("")
            print "\n", usr, "\n"
            conversation = db.messages.find_one({'tag' : usr}, {"_id" : False})
            print conversation
            if conversation == None:
                startConversation(usr, db)
                conversation = db.messages.find_one({'tag' : usr}, {"_id" : False})
            return render_template("messages.html", conversation=conversation)
    if request.method == "POST":
        if request.form["b"] == "Log Out":
            return logout()
        if request.form['b'] == "Create a Wall!":
            return redirect("create_wall")
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
        else:
            print "hit send\n"
            message = request.form["textbox1"]
            if usr == None:
                print "getting usr...\n"
                print request.form["usr"]
                usr = request.form["usr"].replace(" ", "").split(",")
                usr.append(session['email'])
                usr.sort()
                print usr
                startConversation(usr, db)
            else:
                usr = usr.split("_")
                usr.sort()
                while "" in usr:                    
                    usr.remove("")
                print usr
                sendMessage(session['email'], usr, message, db)
            s = ""
            for email in usr:
                s+= "_" + email
            return redirect('messages/'+s)




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
    #print wall
    upped = False
    if wall_id in session['walls_upped']:
        upped = True
    if request.method == "GET":
        if wall['type'] == "writing":
            return render_template("stall.html", wall=wall, upped=upped)
        else:
            return redirect(url_for('canvas', wall_id=wall_id))
    if request.method == "POST":
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
        if request.form['b'] == "Search Wall":
            x = search_wall(request.form, db)
            if x == []:
                flash('invalid search')
                return redirect('home')
            return render_template("search_results.html", walls = x)
    else:
        canvas(wall_id, db)


@app.route("/canvas/<wall_id>", methods=["GET", "POST"])
def canvas(wall_id):

    wall = db.walls.find_one( {'wall_id':wall_id} )
    red = json.loads(json.dumps(request.args.get("red")))
    white = json.loads(json.dumps(request.args.get("white")))
    #print red
    #print request.query_string

    print "red one"
    print red

    #red_request_string = request.query_string
    red_request_string = ""
    white_request_string = ""
    stop_red = False
    for x in range(0, len(request.query_string)):
        if(request.query_string[x] == "w"):
            stop_red = True
        elif(not(stop_red)):
            red_request_string = red_request_string + request.query_string[x]
        elif(stop_red):
            white_request_string = white_request_string + request.query_string[x]

    red_request_data = ""
    if(len(red_request_string) > 0):
        x = 0
        while(x < len(red_request_string) - 2):
            #print red_request_string[x]
            if(red_request_string[x-1] == "="):
                j = 0;
                while(len(red_request_string) > j+x and red_request_string[j+x].isdigit()):
                    red_request_data = red_request_data + red_request_string[j+x]
                    if(j+x+1 >= len(red_request_string)):
                        red_request_data = red_request_data + ","
                    elif(not(red_request_string[j+x+1].isdigit())):
                        red_request_data = red_request_data + ","
                    j = j + 1
            x = x + 1
    #print red_request_data
    #print "please"
    red_request_data = red_request_data + "0,0,"
    if(len(red_request_string) > 0):
        request_array = []
        b = 0
        number = ""
        coord_array = []
        while (b < len(red_request_data)):
            if(red_request_data[b] == ","):
                if(len(coord_array) < 2):
                    coord_array.append(int(float(number)))
                elif(len(coord_array) == 2):
                    request_array.append(coord_array)
                    coord_array = []
                    coord_array.append(int(float(number)))
                number = ""
            else:
                number = number + red_request_data[b]
            b = b + 1
        #print request_array
        red_thing = wall['red']
        red_thing.append(request_array)
        #print "red"
        #print red_thing
        update_wall(wall_id, {'red': red_thing}, db)

    white_request_data = ""
    if(len(white_request_string) > 0):
        x = 0
        while(x < len(white_request_string) - 2):
            #print white_request_string[x]
            if(white_request_string[x-1] == "="):
                j = 0;
                while(len(white_request_string) > j+x and white_request_string[j+x].isdigit()):
                    white_request_data = white_request_data + white_request_string[j+x]
                    if(j+x+1 >= len(white_request_string)):
                        white_request_data = white_request_data + ","
                    elif(not(white_request_string[j+x+1].isdigit())):
                        white_request_data = white_request_data + ","
                    j = j + 1
            x = x + 1
    #print white_request_data

    white_request_data = white_request_data + "0,0,"
    if(len(white_request_string) > 0):
        request_array = []
        b = 0
        number = ""
        coord_array = []
        while (b < len(white_request_data)):
            if(white_request_data[b] == ","):
                if(len(coord_array) < 2):
                    coord_array.append(int(float(number)))
                elif(len(coord_array) == 2):
                    request_array.append(coord_array)
                    coord_array = []
                    coord_array.append(int(float(number)))
                number = ""
            else:
                number = number + white_request_data[b]
            b = b + 1
        #print request_array
        white_thing = wall['white']
        white_thing.append(request_array)
        update_wall(wall_id, {'white': white_thing}, db)

    #print wall
    if request.method == "POST":
        if request.form["b"] == "up_vote":
            new_ses = up_vote(wall_id, session, db)
            session['walls_upped'] = new_ses
            return redirect(url_for('wall_page', wall_id=wall_id))
        if request.form["b"] == "Log Out":
            return logout()
        if request.form['b'] == "Create a Wall!":
            return redirect("create_wall")
        if request.form['b'] == "Search Wall":
            x = search_wall(request.form, db)
            if x == []:
                flash('invalid search')
                return redirect('home')
            return render_template("search_results.html", walls = x)
        
    if request.method == "GET":
        wall = db.walls.find_one( {'wall_id':wall_id} )
        
        upped = False
        if wall_id in session['walls_upped']:
            upped = True
        
        return render_template("canvas.html", wall=wall, upped=upped)

@app.route("/walls", methods=["GET", "POST"])
def walls():
    if request.method == "GET":
        walls = db.walls.find().sort('name', pymongo.ASCENDING)
        wall_dict = {}
        counter = 0
        wall_dict[string.uppercase[counter]] = []
        l = []
        for w in walls:
            #create lists of all walls with each letter first
            print w['name'][0]
            if w['name'][0] == string.uppercase[counter]:
                l.append(w)
            else:
                while w['name'][0] != string.uppercase[counter]:
                    wall_dict[string.uppercase[counter]] = l
                    counter += 1
                    if counter > 26:
                        break
                    wall_dict[string.uppercase[counter]] = []
                    l = []
                l.append(w)
        wall_dict[string.uppercase[counter]] = l
        for key in wall_dict:
            print key
            print wall_dict[key]
        return render_template("walls.html", walls=wall_dict)
    else:
        if request.form["b"] == "Log Out":
            return logout()
        if request.form['b'] == "Create a Wall!":
            return redirect("create_wall")
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
    app.run(port=8000)
