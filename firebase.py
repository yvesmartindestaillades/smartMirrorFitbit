import firebase_admin
from firebase_admin import credentials, db
from os.path import join, dirname
import datetime


class Firebase:
    
    def __init__(self) -> None:
        cred = credentials.Certificate("invu-41101-firebase-adminsdk-h3w93-7a2ae7baff.json")
        firebase_admin.initialize_app(cred, options={'projectId': 'invu-41101', 'databaseURL': 'https://invu-41101-default-rtdb.firebaseio.com/'})
        self.ref = db.reference("/")
        self.user = 'yves_martin'
        
    def set_user(self, user: str) -> None:
        self.user = user
    
    def push(self, data: dict, name:str, date=None, user=None) -> None:
        if data is None:
            return
        path = self.set_path(name, user, date)
        print("Pushing data at path", path)
        return self.ref.child(path).push(data)
    
    def set(self, data: dict, name:str, date=None, user=None) -> None:
        if data is None:
            return
        path = self.set_path(name, user, date)
        print("Setting data at path", path)
        return self.ref.child(path).set(data)

    def read(self, name:str, date=None, user=None) -> None:
        path = self.set_path(name, user, date)
        print("Reading data at path", path)
        return self.ref.child(path).get()
    
    def delete(self, name:str, date=None, user=None) -> None:
        path = self.set_path(name, user, date)
        return self.ref.child(path).delete()
    
    def set_path(self, item, user='yves_martin', date=None):
        user = self.user if user is None else user
        date = datetime.date.today().isoformat() if date is None else str(date).split(' ')[0]
        return join(user, date, item)
    
    def exists(self, name:str, date=None, user=None) -> bool:
        path = self.set_path(name, user, date)
        return self.ref.child(path).get() is not None
    
firebase = Firebase()