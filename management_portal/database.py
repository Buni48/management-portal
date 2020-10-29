import mariadb
import sys

def connect():
    """
    Connects django to the mariadb database 'management_portal'.
    It creates the database if it doesn't exist.

    Returns:
    sql connection
    """
    user        = 'root'
    password    = 'test'
    host        = '127.0.0.1'
    port        = 3306
    database    = 'management_portal'

    try:
        # try connect to database
        __connectDatabase(user, password, host, port, database)
    except mariadb.Error as e:
        # try connect to mysql in general instead
        try:
            __createDatabase(user, password, host, port, database)
            __connectDatabase(user, password, host, port, database)
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

def __connectDatabase(user, password, host, port, database):
    """
    Connect to database 'management_portal'

    Returns:
    sql connection
    """
    return mariadb.connect(
        user     = user,
        password = password,
        host     = host,
        port     = port,
        database = database
    )

def __createDatabase(user, password, host, port, database):
    """
    Connect to mariadb in general and create database
    """
    conn =  mariadb.connect(
        user     = user,
        password = password,
        host     = host,
        port     = port
    )
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE `' + database + '`')
