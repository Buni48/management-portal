import mariadb
import sys

def connect():
    user        = 'root'
    password    = 'test'
    host        = '127.0.0.1'
    port        = 3306
    database    = 'management_portal'

    try:
        # try connect to database
        return mariadb.connect(
            user     = user,
            password = password,
            host     = host,
            port     = port,
            database = database
        )
    except mariadb.Error as e:
        # try connect to mysql in general instead
        try:
            conn =  mariadb.connect(
                user     = user,
                password = password,
                host     = host,
                port     = port
            )
            cursor = conn.cursor()
            # create database
            cursor.execute('CREATE DATABASE `management_portal`')
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
