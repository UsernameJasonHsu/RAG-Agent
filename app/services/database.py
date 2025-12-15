# 資料庫操作封裝

import os
import time
import mysql.connector

class MySQLConnector:
    def __init__(self, db_config: dict):
        self.conn = mysql.connector.connect(**db_config)
        self.cursor = self.conn.cursor()

    def insert_log(self, question: str, answer: str):
        sql = "INSERT INTO logs (question, answer) VALUES (%s, %s)"
        self.cursor.execute(sql, (question, answer))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()