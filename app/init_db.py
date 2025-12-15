from services.database import MySQLConnector

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "yourpassword",
    "database": "nlp_db"
}

db = MySQLConnector(**db_config)
db.execute_sql_file("sql/init_db.sql")
db.close()