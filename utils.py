import hashlib, uuid #for password security
from time import ctime

##########################     LOGIN/ REGISTER        ##########################

#Creates new user in database.
#user: {string:username, int:password, int:salt, list:int:private_walls, list:int:public_walls, list:string:friends, dict:conversations, int:count_unread}
#conversations can be structured :  {person_talked_to: {int:unread_count, messages:[{'sender':who_sent_this_message, string:'message_text', string:'time':'12:04:50', 'date':Jan-20-2015}, more messages....], more people:{}....}
def register_user(form, db):
    user = {}

    user['username'] = form['username']

    #security
    pword = form['password']
    salt = uuid.uuid4().hex #creates salt, randomized string attached to end of password
    hash_pass = hashlib.sha512(salt + pword).hexdigest() #prepend the salt to the password, hash using sha512 algorithm, use hexdigest to store as string
    user['password'] = hash_pass
    user['salt'] = salt

    user['private_walls'] = [] #will be list of ids
    user['public_walls'] = [] #ditto
    user['friends'] = [] #list of other users usernames
    user['conversations'] = {}
    user['count_unread'] = 0 #number of total unread messages
    
    return db.users.insert(user)
    

#ensures a valid username and password
def validate(username, password, db):
    taken_name = db.tutees.find_one({'username': username})
    if taken_name:
        if len(username) == 0:
            return 'No username entered'
        elif len(password) > 5:
            return 'Invalid password. Must be at least five characters.'
        else:
            return 'Valid'
    else:
        return 'Username taken'

#checks that login info is valid, returns the full user info associated with the username if it is
def authenticate(username, password, db):
    #finds user with the listed username
    user = db.users.find_one( { 'username' : username } , { "_id" : False } )
    if user == None:
        return None

    #security check on password
    salt = user["salt"]
    hash_pass = user["password"]
    hash_confirm = hashlib.sha512(salt + password).hexdigest()
    if hash_pass == hash_confirm:
        return user
    else:
        return None
        
# update_dict must be in the form {field_to_update : new_val}
def update_user(username, update_dict, db):
    db.users.update({'username' : username}, {'$set' : update_dict}, upsert=True)
    return True


##########################     WALLS        ##########################

wall_count = 0

#creates a dict wall: {string:name, string:description, int:wall_id, int:num_comments, list:dict:comments{string:comment,  string:'time':'12:04:50', 'date':Jan-20-2015, int:up_votes, int:comment_id}} 
def create_wall(name, description, db):
    wall = {}
    if len(name) == 0:
        return "Name required"
    else:
        wall['name'] = name
        repeated = db.walls.find_one( { 'name' : name } , { "_id" : False } )
        if repeated != None:
            return "Name taken"
        wall['description'] = description
        global wall_count #to access the global variable
        wall_count += 1
        wall['wall_id'] = wall_count
        wall['comments'] = []
        wall['num_comments'] = 0
        db.walls.insert(wall)
        return "Wall" + name + "created"

#adds a comment, must be given form with the comment, name of the current wall, session and db
#if user is not yet liste as having that wall connected, adds the wall's id
def add_comment(form, current_wall, session, db):
    walls = db.walls.find_one( {'name':current_wall} )
    
    comment = {}
    comment['comment'] = form['comment']

    if form['comment'] == None:
        return 'Comment field left blank'

    comment['up_votes'] = 0
    
    #for time stamp
    time_total = str(ctime())
    comment['date'] = time_total[4:10] + ", " + time_total[20:25]
    comment['time'] = time_total[11:19]
    
    for w in walls:
        wall = w
    old_comments = wall['comments']
    old_comments.append(comment)
    num_comments = wall['num_comments'] + 1
    update_wall(wall['name'], {'comments':comment, num_comments:num_comments}, db)
    return "comment added"
    
    
    
def search_wall(form, db):
    name = form['name']
    wall = db.walls.find_one( { 'name' : name } , { "_id" : False } )
    if wall == None:
        return "Invalid search name"
    for w in wall:
        return w #Since name repeats aren't allowed, only one will be returned

# update_dict must be in the form {field_to_update : new_val}
def update_wall(name, update_dict, db):
    db.wall.update({'name' : name}, {'$set' : update_dict}, upsert=True)
    return True    
        
################################################# MESSAGES ##########################################################

#sends message by updating the "conversations" key for each user. Conversations' value is a dictionary, each key being the username of the other side of a given conversation. The value of each such key is a list of dictionaries, each dictionary containing a given message's content, sender, and time of sending. Example:
# 'conversations': {person_talked_to: {unread_count: #, messages:[{'sender':person_talked_to/me, 'message_text':'sup', 'time':'12:04:50', 'date':Jan-20-2015}, more messages....], more people....}
#form must have a recipient listed, a message content
def send_message(form, session, db):
        recipient_username = form['recipient']
        message = form['message']
        sender_user_type = session['type']
        recipient_cursor = db.users.find({'username':recipient_username})
        recipient = {}
        for t in recipient_cursor:
                recipient = t
        if recipient == {}:
                return "invalid recipient"
        conversations = recipient['conversations'] #list of dictionaries, each dictionary being a message that this recipient has already recieved
        time_total = str(ctime())
        date = time_total[4:10] + ", " + time_total[20:25]
        time = time_total[11:19]

        #first update the dictionary of the recipient of the message
        new_message = [{'sender':session['username'], 'message_text':message, 'time':time, 'date':date}]
        unread_count = 1
        #check if this conversation already exists. If so incorporate rest of conversation
        if conversations.has_key(session['username']): #if they've already talked
                add_message = conversations[session['username']]['messages']
                for x in add_message:
                        new_message.append(x) #so that new message is at the begginning
                unread_count = conversations[session['username']]['unread_count'] + 1 #unread count in this specific conversation

        conversations[session['username']] = {'unread_count':unread_count, 'messages':new_message} #insert as the new value in dict
        count = recipient['count_unread'] + 1 #increment user's count of unread messages
        update_user(recipient['username'], {'conversations':conversations, 'count_unread':count}, db)
        
        #update dictionary of the sender
        conversations = session['conversations'] #list of dictionaries, each dictionary being a message that this recipient has already recieved
        new_message = [{'sender':session['username'], 'message_text':message, 'time':time, 'date':date}]
        if conversations.has_key(recipient['username']):
                add_message = conversations[recipient['username']]['messages']
                for x in add_message:
                        new_message.append(x)
        conversations[recipient['username']] = {'unread_count':0, 'messages':new_message}
        update_user(session['username'], {'conversations':conversations}, db)
        return message + " sent on " + date + " by " + session['username']
