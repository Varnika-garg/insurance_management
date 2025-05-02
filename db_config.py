import pymysql

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='admin123@:',
        database='insurance'
    )
