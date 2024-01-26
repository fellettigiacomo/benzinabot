import mysql.connector

class ch:
    def __init__(self, host, user, pw, dbname):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=pw,
            database=dbname
        )
        
    def execute(self, query):
        try:
            if self.db.is_connected():
                cursor = self.db.cursor()
                cursor.execute(query)
                self.db.commit()
            else:
                print("errore mysql: non connesso al database")
        except mysql.connector.Error as e:
            print("errore mysql: ", e)

    def checkUser(self, userid):
        try:
            if self.db.is_connected():
                cursor = self.db.cursor()
                cursor.execute(f"SELECT * FROM utenti WHERE idUtente = {userid}")
                result = cursor.fetchall()
                self.db.commit()
                if len(result) > 0:
                    return True
                else:
                    return False
            else:
                print("errore mysql: non connesso al database")
                return None
        except mysql.connector.Error as e:
            print("errore mysql: ", e)
            return None

    def fetch(self, query):
        try:
            if self.db.is_connected():
                cursor = self.db.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                self.db.commit()
                return result
            else:
                print("errore mysql: non connesso al database")
                return None
        except mysql.connector.Error as e:
            print("errore mysql: ", e)
            return None
        
    def truncate(self, tableName):
        try:
            if self.db.is_connected():
                cursor = self.db.cursor()
                cursor.execute(f"TRUNCATE TABLE {tableName}")
                self.db.commit()
            else:
                print("errore mysql: non connesso al database")
        except mysql.connector.Error as e:
            print("errore mysql: ", e)

    def close(self):
        self.db.close()