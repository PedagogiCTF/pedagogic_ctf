#!/usr/bin/python3
import sqlite3, sys
import bcrypt, time

## Usage :
# ex : ./race_condition.py register admin password123
# ex : ./race_condition.py login admin password123

start_time = time.time()

## check params
if len(sys.argv) != 4 or not sys.argv[1] or not sys.argv[2] or not sys.argv[3]:
    print("Please send me an 'action' (register or login) with your credentials (login, then password)")
    sys.exit(0)
action = sys.argv[1]
login = sys.argv[2]
passwd = sys.argv[3]
hashed_passwd = bcrypt.hashpw(passwd.encode("utf-8"), bcrypt.gensalt(8)).decode('utf-8')
## end check params

try:
    conn = sqlite3.connect('/tmp/race_condition/race_condition.db', isolation_level=None)
    cur = conn.cursor()
except Exception as e:
    print('Error connecting to db: {}'.format(e))
    sys.exit(0)


def get_user_id():
    cur.execute("SELECT id, password FROM users WHERE login=?", [login])
    user = cur.fetchone()
    if user:
        if bcrypt.hashpw(passwd.encode("utf-8"), user[1].encode('utf-8')) == user[1].encode('utf-8'):
            return user[0]
    return -1


def do_register():
    cur.execute("INSERT INTO users(login, password) VALUES(?, ?)", [login, hashed_passwd])
    user_id = get_user_id()
    time.sleep(0.5)  # simulate more db access / calculus
    elapsed = time.time() - start_time
    print("It's been " + str(elapsed) + "s since you started register.\n")
    cur.execute("INSERT INTO forbidden_ids(user_id) VALUES(?)", [user_id])


def do_login():
    user_id = get_user_id()
    if user_id < 0:
        return "We failed to log you in :/"
    elapsed = time.time() - start_time
    print("It's been " + str(elapsed) + "s since you started log in.\n")
    cur.execute("SELECT count(*) FROM forbidden_ids WHERE user_id=?", [user_id])
    if cur.fetchone()[0] > 0:
        return "You are logged in. But sorry you are not allowed to see the secret."
    with open('secret') as s:
        return "You are logged in. And congratz ! Here is the secret : " + s.read()


if action == 'register':
    try:
        do_register()
        print("You are registered !")
    except Exception as e:
        print("An error occurred : " + str(e))
elif action == 'login':
    try:
        print(do_login())
    except Exception as e:
        print("An error occurred : " + str(e))
else:
    print("Error, action param not valid.")

conn.close()
