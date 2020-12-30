import mysql.connector
import dotenv
import os

dotenv.load_dotenv()
HOST = os.getenv("HOST")
USER = os.getenv('USER')
PASSWD = os.getenv('PASSWD')
DB = os.getenv('DB')

class InformationDataBase:
    def __init__(self):
        self.db = mysql.connector.connect(
            host=HOST,
            user=USER,
            passwd=PASSWD,
            database=DB
        )

        self.mycursor = self.db.cursor()


    def add_bd(self,post_id, title, name_photo, address):
        self.mycursor.execute("INSERT INTO Informations (post_id, title, name_photo, address) VALUES (%s,%s,%s,%s)", (post_id, title, name_photo, address))
        self.db.commit()
        print(f"""
        {post_id} has been added to the db!
        {title} has been added to the db!
        { name_photo} has been added to the db! 
        {address} has been added to the db!
    """)

    def get_image_title(self, name):
        self.mycursor.execute(f"SELECT title, address FROM Informations WHERE name_photo='{name}'")
        info = self.mycursor.fetchone()
        print(info)
        return info

    def clear_db(self):
        self.mycursor.execute("DELETE FROM informations;")
        self.db.commit()
        print("DB Cleared!")
        return




if __name__ == "__main__":
    inst = InformationDataBase()
