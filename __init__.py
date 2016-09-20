"""Web App for managing bookmarks."""
# these are local functions imported from within the app.
from dbconnect import connection
from helper import login_required, is_username_exist  # helper functions
from schema import schema

# these are functions imported from flask library.
from flask.ext import excel   # used for handling csv file
from flask import Flask, render_template, redirect, \
    request, session, url_for  # various flask utilities

# these are functions imported from other applications.
from MySQLdb import escape_string   # used as safeguard for injection attack.
from passlib.hash import sha256_crypt  # used for encryption

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])  # url address and methods allowed for this function
def login_page():
    """Home page of the application where the user can log in."""
    if 'logged_in' and 'username' in session:    # redirect user if already logged in
        return redirect(url_for('logged_in'))

    try:
        message = None
        c, conn = connection()
        if request.method == 'POST':
            data = c.execute("SELECT * FROM users WHERE username = (%s)",
                             escape_string(request.form['username']))  # extracting user
            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):  # verifying hash password
                session['logged_in'] = True       # setting session values helps keep logged in
                session['username'] = request.form['username']
                return redirect(url_for('logged_in', message=message))

            else:
                message = 'Invalid credentials. Try again'

        return render_template('UserAccount/login.html', message=message)  # for get method

    except Exception:        # catching any errors that occured in above code
        message = 'Invalid credentials. Try again'
        return redirect(url_for('/', message=message))


@app.route('/logout/')
@login_required  # wrapper ensuring that only logged in user can access this page
def logout():
    """Logout function used for clearing session values and ejecting user out of server."""
    session.pop('logged_in', None)    # clearing session values
    session.clear()
    return render_template('UserAccount/login.html', message='logged out')


@app.route('/logged_in/', methods=["GET", "POST"])
@login_required
def logged_in():
    """Logged in page that appears afte succesful authentication and shows bookmarks."""
    try:
        c, conn = connection()

        if request.method == 'POST':
            title = request.form['name']   # taking input for storing bookmark
            url = request.form['url']

            c.execute("SELECT uid FROM users WHERE username = (%s)",
                      session['username'])   # storing bookmark under the user who created it
            c.execute("INSERT INTO bookmarks (title, url, uid) VALUES \
                (%s, %s, %s)", (escape_string(title), escape_string
                                (url), c.fetchone()[0]))
            conn.commit()   # database commiting changes and closing of the connection
            c.close()
            conn.close()
            return redirect(url_for('logged_in', message="message"))

        else:
            c.execute("SELECT * FROM users WHERE username = (%s)",
                      session['username'])
            c.execute("SELECT * FROM bookmarks WHERE uid = (%s)",
                      c.fetchone()[0])
            a = list(c.fetchall())  # if get request then query the list of bookmarks and display them

            return render_template('UserAccount/logged_in.html',
                                   data=a)
    except Exception, e:
        return render_template('UserAccount/login.html', message=e)


@app.route('/register/', methods=["GET", "POST"])
def registration_page():
    """Page where new user accounts are made."""
    try:
        message = None

        if request.method == 'POST':
            username = request.form['username']

            password = sha256_crypt.encrypt(
                (str(request.form['password'])))   # taking password and hashing it for protection
            c, conn = connection()

            if is_username_exist(escape_string(username)) > 0:   # checking if user exists
                message = 'That username is already taken, please choose anot\
                her'
                return render_template('UserAccount/register.html',
                                       message=message)

            else:
                c.execute("INSERT INTO users (username, password) VALUES \
                (%s, %s)", (escape_string(username), escape_string
                            (password)))    # creating new user
                conn.commit()
                c.close()
                conn.close()
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('logged_in'))
        return render_template('UserAccount/register.html')

    except Exception as e:
        return(str(e))


@app.route('/download', methods=["POST"])
@login_required
def download():
    """Function which helps to export the bookmarks list."""
    if request.method == 'POST':
        c, conn = connection()
        c.execute("SELECT uid FROM users WHERE username = (%s)",
                  session['username'])

        data = c.execute("SELECT * FROM bookmarks WHERE uid = (%s)",
                         c.fetchone()[0])   # fetching bookmarks for logged in user
        data = (tuple(a[1:-1] for a in c.fetchall()))  # truncating data from list

        heading = ((('Title', 'URL', 'Timestamp'),))  # adding heading for excel file
        output = excel.make_response_from_array(heading + data, 'csv')  # converting list into csv
        output.headers["Content-Disposition"] = "attachment; \
                      filename=export.csv"
        output.headers["Content-type"] = "text/csv"  # setting header to download the file
    return output


if __name__ == "__main__":
    schema()  # function for checking databse schema
    app.secret_key = '12345'  # secret key used for hashing
    app.run()  # running the instance of the app
