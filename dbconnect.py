"""Configuration file for database settings."""
import MySQLdb  # database name


def connection():
    """Function used for establishing connection with the database."""
    conn = MySQLdb.connect(host="localhost",  # host name
                           user="root",  # database username
                           passwd="homepokl",  # database password
                           db="bookmark")  # name of the data base
    c = conn.cursor()  # used for executind queries

    return c, conn
