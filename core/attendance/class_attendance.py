from config import db_link
import requests
import json
from datetime import datetime

class Attendance():

    def update_status(id ,city, date):

        date = datetime.strptime(date, '%Y-%m-%d')
        year = str(date.year)
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"

        data = {
            'status': 'Agendado'
        }
        response = requests.patch(f'{db_link}/attendance_records/{city}/{year}/{month}/{day}/{id}.json', data=json.dumps(data))