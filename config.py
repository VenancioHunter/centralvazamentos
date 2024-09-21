import pyrebase



db_link = "https://central-942b3-default-rtdb.firebaseio.com"

firebase_config = {
    "apiKey": "AIzaSyBsB3mCu1ud2OXaOzVo4637h0a27QL2yuY",
    "authDomain": "central-942b3.firebaseapp.com",
    "databaseURL": "https://central-942b3-default-rtdb.firebaseio.com",
    "projectId": "central-942b3",
    "storageBucket": "central-942b3.appspot.com",
    "messagingSenderId": "514561357213",
    "appId": "1:514561357213:web:bfac9ab5de5081a6b36b74",
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()