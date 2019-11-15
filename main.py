import webapp2
import MySQLdb
import passwords
import random
import cgi

def recordSession(sessionid):
    conn = setConn()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO sessions (id) VALUES (%s);", (sessionid,))
    
    cursor.close()
    conn.commit()
    conn.close()
    
def checkUser(cookie):
    conn = setConn()
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM sessions WHERE id=%s;", (cookie,))
    username = cursor.fetchall()
    if len(username) != 0:
        username = username[0][0]
    else:
        username = None
    cursor.close()
    conn.commit()
    conn.close()

    return username

def updateUser(cookie, username):
    conn = setConn()
    cursor = conn.cursor()

    cursor.execute("UPDATE sessions SET username=%s WHERE id=%s", (username, cookie))
    
    cursor.close()
    conn.commit()
    conn.close()


def setConn():
    conn = MySQLdb.connect(unix_socket = passwords.UNIX_SOCKET,
                       user = passwords.SQL_USER,
                       passwd = passwords.SQL_PASSWD,
                       db = "zhiyulong")
    return conn

def userForm(self):
    self.response.write('''
            <br>
            <form action="https://csc346-lab7.appspot.com/" method="get">            
                Please enter your name: <br>
                <input type="text" name = "username"><br>
                <input type='submit'>
            </form>
    ''')


def getForm():
    form = cgi.FieldStorage()
    if form.getvalue("username"):
        return form.getvalue("username")
    else:
        return None

def checkIncrement():
    form = cgi.FieldStorage()
    if form.getvalue("increment"):
        return form.getvalue("increment")
    else:
        return None

def displayButton(self, username, value):
    
    self.response.write('<br><br>Your current entry count: {}'.format(value))
    self.response.write('''
        <br>
        <form action="https://csc346-lab7.appspot.com/" method = "get">
            <button type="submit" name="increment" value='{}'>INCREMENT</button>
        </form>
    '''.format(username))


def checkEntry(user):
    conn = setConn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM entry WHERE username=%s;",(user,))
    record = cursor.fetchall()
    
    if len(record)==0:
        cursor.close()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO entry (username, times) VALUES (%s, 0);", (user,))
        value = 0
    else:
        value = record[0][2]
    
    cursor.close()
    
    if checkIncrement() == user:
        cursor = conn.cursor()
        cursor.execute('UPDATE entry SET times=times+1 WHERE username=%s',(user,))
        cursor.close()
        value += 1
        
    conn.commit()
    conn.close()

    return value


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/html"
        
        cookie = self.request.cookies.get("cookie_name")
        
        if cookie == None:
            sessionid = "%032x" % random.getrandbits(128)
            self.response.set_cookie("cookie_name",sessionid, max_age=1800)
            
            recordSession(sessionid)
            cookie = sessionid

        user = checkUser(cookie)
        form = getForm()
        if user == None and form == None:
            self.response.write("User field of this session is NULL!<br>")
            userForm(self)
        
        elif user == None and form != None:
            updateUser(cookie, form)
            self.response.write('<br>Updated the session with user: ' + form)
            self.response.write('<br>Check <a href="https://csc346-lab7.appspot.com/">value</a>') 
        else:
            value =  checkEntry(user)
            
            self.response.write("<br>Hi! "+user)
            displayButton(self, user, value)
    
        
        
app = webapp2.WSGIApplication ([
    ("/", MainPage),
], debug=True)
