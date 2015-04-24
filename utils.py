import hashlib, uuid #for password security

##########################     LOGIN/ REGISTER        ##########################

#Creates new user in database.
#user: {string:username, int:password, int:salt, list:int:private_walls, list:int:public_walls, list:string:friends, dict:conversations}
#conversations can be structured :  {person_talked_to: {int:unread_count, messages:[{'sender':who_sent_this_message, string:'message_text', string:'time':'12:04:50', 'date':Jan-20-2015}, more messages....], more people....}
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


##########################     WALLS        ##########################

wall_count = 0

#creates a dict wall: {string:name, string:description, int:wall_id, int:num_comments, list:dict:comments{string:comment,  string:'time':'12:04:50', 'date':Jan-20-2015, int:up_votes, int:comment_id}} 
def create_wall(name, description):
    wall = {}
    if len(name) == 0:
        return "Name required"
    else:
        wall['name'] = name
        wall['description'] = description
        global wall_count
        wall_count += 1
        wall['wall_id'] = wall_count
        wall['comments'] = []
        wall['num_comments'] = 0
        return "Wall" + name + "created"
