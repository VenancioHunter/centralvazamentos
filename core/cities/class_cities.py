from config import db
from datetime import datetime

class Cities:
    def get_cities():
        
        data = db.child("cities").get().val()

        return data
