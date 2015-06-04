from flask import Flask, flash, session, request, url_for, redirect, render_template, jsonify
from pymongo import MongoClient
from utils import *
from functools import wraps
import pymongo
import operator
import string
import json
import re

app = Flask(__name__)

# mongo 
#conn = Connection()
db = MongoClient()['users']



#db.hot_walls.ensure_index( { "createdAt": 1 }, { 'expireAfterSeconds': 60 } )



#Tue May 26 22:16:53 2015

#db.walls.remove()

#print "hey"
#users = db.users.find()
#for u in users:
    #print u
    #print "SPACE"

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
    update_user(session['email'], {'conversations' : {'Niggah': 'Hey'}}, db)
    test = db.users.find_one( { 'email' : session['email'] } , { "_id" : False } )
    if request.method == "GET":
        walls = db.new_walls.find().sort('up_votes', pymongo.DESCENDING)
        return render_template("home.html", walls=walls)
    else:
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
        print session['friends']
        print session['email']
        if usr == None:
            messages = db.messages.find()
            return render_template("messages.html", conversation=0)
        else:
            print session['friends']
            usr = usr.split("_")
            usr.sort()
            while "" in usr:
                usr.remove("")
            conversation = db.messages.find_one({'tag' : usr}, {"_id" : False})
            if conversation == None:
                startConversation(usr, db)
                conversation = db.messages.find_one({'tag' : usr}, {"_id" : False})
                friends = session['friends']
                user = db.users.find_one({'email': usr[0]})
                print "HERE"
                print user

                friend_dict = {}
                friend_dict['email'] = user['email']
                friend_dict['first_name'] = user['first_name']
                friend_dict['last_name'] = user['last_name']
                friends.append(friend_dict)
                session['friends'] = friends
                update_user(session['email'], {'friends': friends}, db)

                friends_other = user['friends']
                user_dict = {}
                user_dict['email'] = session['email']
                user_dict['first_name'] = session['first_name']
                user_dict['last_name'] = session['last_name']
                friends_other.append(user_dict)
                update_user(usr[0], {'friends': user_dict}, db)
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
    #red = json.loads(json.dumps(request.args.get("red")))
    #white = json.loads(json.dumps(request.args.get("white")))
    all_edits = json.loads(json.dumps(request.args.get("edits")))

    #REQUEST HANDLING
    #red_request_string = request.query_string
    request_string = request.query_string

    request_data = ""
    if(len(request_string) > 0):
        x = 0
        while(x < len(request_string) - 2):
            if(request_string[x-1] == "="):
                j = 0;
                if(request_string[x] == "r" or request_string[x] == "b" or request_string[x] == "g" or request_string[x] == "w"):
                    request_data = request_data + request_string[x] + ","
                else:
                    while(len(request_string) > j+x and request_string[j+x].isdigit()):
                        request_data = request_data + request_string[j+x]
                        if(j+x+1 >= len(request_string)):
                            request_data = request_data + ","
                        elif(not(request_string[j+x+1].isdigit())):
                            request_data = request_data + ","
                        j = j + 1
            x = x + 1
    request_data = request_data + "0,0,w"
    print request_data + "\n"

    if(len(request_string) > 0):
        request_array = []
        b = 0
        number = ""
        coord_array = []
        while (b < len(request_data)):
            if(request_data[b] == ","):
                if(len(coord_array) < 2):
                    coord_array.append(int(float(number)))
                elif(len(coord_array) == 2):
                    if(request_data[b-1] == "r"):
                        coord_array.append(0)
                    if(request_data[b-1] == "b"):
                        coord_array.append(1)
                    if(request_data[b-1] == "g"):
                        coord_array.append(2)
                    if(request_data[b-1] == "w"):
                        coord_array.append(3)
                    #coord_array.append(request_data[b-1])
                    request_array.append(coord_array)
                    coord_array = []
                number = ""
            elif(request_data[b].isdigit()):
                number = number + request_data[b]
            b = b + 1
        thing = wall['edits']
        thing.append(request_array)
        update_wall(wall_id, {'edits': thing}, db)
        print wall['edits']
        print request_array
        thing = wall['edits']
        thing.append(request_array)
        update_wall(wall_id, {'edits': thing}, db)

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
@app.route("/walls/<sort>", methods=["GET", "POST"])
def walls(sort = "new"):
    if request.method == "GET":
        if sort == "new":
            wall_curs = db.walls.find()
            walls = []
            for wall in wall_curs:
                walls.append(wall)
            return render_template("walls.html", walls=walls[::-1])
        if sort == "pop":
            walls = db.walls.find().sort('up_votes', pymongo.DESCENDING)
        if sort == "mypop":
            wall_ids = session['walls_upped']
            walls = []
            for wall_id in wall_ids:
                walls.append(db.walls.find_one( { 'wall_id' : wall_id } , { "_id" : False } ))
        if sort == "mywalls":
            wall_ids = session['public_walls']
            walls = []
            for wall_id in wall_ids:
                walls.append(db.walls.find_one( { 'wall_id' : wall_id } , { "_id" : False } ))
        return render_template("walls.html", walls=walls)
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

@app.route('/_search_wall_update')
def wall_search_update():
    name = request.args.get('name', 0, type=str)
    if name == '':
        return jsonify(result=['','',''])
    regx = re.compile("^%s" % name, re.IGNORECASE)
    w = db.walls.find( {'name': regx }).sort('up_votes', pymongo.DESCENDING)
    ret = []
    for wall in w:
        new_dict = {}
        new_dict['name'] = wall['name']
        new_dict['wall_id'] = wall['wall_id']
        ret.append(new_dict)
    blank = {}
    blank['name'] = ''
    blank['wall_id'] = ''
    if len(ret) == 0:
        ret.append(blank)
    if len(ret) == 1:
        ret.append(blank)
    if len(ret) == 2:
        ret.append(blank)
    return jsonify(result=ret)

@app.route('/_email_search')
def email_search():
    print "something"
    name = request.args.get('name', 0, type=str)
    if name == '':
        return jsonify(result=['','',''])
    regx = re.compile("^%s" % name, re.IGNORECASE)
    u = db.users.find( {'email': regx })
    ret = []
    for user in u:
        print user
        new_dict = {}
        new_dict['email'] = user['email']
        new_dict['id'] = "_" + user['email'] + "_" + session['email']
        ret.append(new_dict)
    blank = {}
    blank['email'] = ''
    blank['id'] = ''
    if len(ret) == 0:
        ret.append(blank)
    if len(ret) == 1:
        ret.append(blank)
    if len(ret) == 2:
        ret.append(blank)
    return jsonify(result=ret)


if __name__ == "__main__":
    app.debug = True
    app.secret_key = "shhhhhh"
    app.run(port=8000)
