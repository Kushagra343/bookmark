"""File where schema of the application is written."""
import MySQLdb


def schema():
    """Define schema of the application if it dosen't exist."""
    conn = MySQLdb.connect(host="localhost",  # host name
                           user="root",  # database username
                           passwd="homepokl",  # database password
                           )
    c = conn.cursor()  # connection to the databse
    c.execute("CREATE DATABASE IF NOT EXISTS bookmark;")  # creating databse
    c.execute("USE bookmark;")                            # using databse

    # creating tables
    c.execute("CREATE TABLE IF NOT EXISTS users(uid INT NOT NULL AUTO_INCREMENT \
                                               PRIMARY KEY, username \
                                               VARCHAR(100) NOT NULL, \
                                               password \
                                               VARCHAR(500) NOT NULL);")
    c.execute("CREATE TABLE IF NOT EXISTS bookmarks(bid INT NOT NULL AUTO_INCREMENT \
                                               PRIMARY KEY, title \
                                               VARCHAR(100) NOT NULL, \
                                               url \
                                               VARCHAR(500) NOT NULL,\
                                               ts TIMESTAMP DEFAULT \
                                               CURRENT_TIMESTAMP ON UPDATE \
                                               CURRENT_TIMESTAMP,\
                                               uid INT );")
    conn.close()    # closing databse connection
    return
