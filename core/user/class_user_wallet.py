from config import db
from datetime import datetime

class User_Wallet:

    def create_transaction_success(data, city, date, id_tecnico):
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return "Formato de data inválido."

        year = str(date.year)
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"

        transation ={
            'os_id': data['os_id'],
            'os_date': data['os_date'],
            'method': data['method'],
            'amount': data['amount'],
        }

        # Salva os dados no Firebase com o novo ID gerado automaticamente
        db.child("users").child(id_tecnico).child('wallet').child('cities').child(city).child(year).child(month).child(day).child('transactions').child('success').push(transation)

    def create_costs(id, date, data):
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return "Formato de data inválido."

        year = str(date.year)
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"

        db.child("users").child(id).child('wallet').child('costs').child(year).child(month).child(day).push(data)

    def verify_costs(id, date):

        year = str(date.year)
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"

        data = db.child("users").child(id).child('wallet').child('costs').child(year).child(month).child(day).get().val()

        if data is not None:
            return True
        else:
            return False
        
    def get_participation(id):
        data = db.child("users").child(id).child("porcentagem").get().val()

        return data