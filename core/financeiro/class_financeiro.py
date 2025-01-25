from config import db
import datetime
import pytz
from core.financeiro.functions import post_transaction_lancamentos, post_caixa

class Financeiro:

    

    def post_transaction_credito_tecnico(user, date, amount, description, destinatario, method_payment, origem, id_origem):

        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        now_in_sao_paulo = datetime.datetime.now(sao_paulo_tz)
        timestamp = now_in_sao_paulo.timestamp()

        transation = {
                    'user': user,
                    'origem': origem,
                    'id_origem': id_origem,
                    'timestamp' : timestamp,
                    'type': 'c',
                    'description': f"",
                    'amount': amount,
                    'category': 'Serviço',
                    'especie': f'Remessa {method_payment}',
                    'destinatario': 'Central Vazamentos' 
                }

        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return "Formato de data inválido."
        
        year = str(date.year)
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"

        db.child("financeiro").child('transactions').child(year).child(month).child(day).child('transactions').push(transation)

        post_transaction_lancamentos(month=month, year=year, type=transation['type'], amount=amount)
        post_caixa(amount=amount, type=transation['type'])


     
    def post_transaction_debito(user, date, amount, description, category, especie, destinatario, origem, id_origem):

        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        now_in_sao_paulo = datetime.datetime.now(sao_paulo_tz)
        timestamp = now_in_sao_paulo.timestamp()

        transation = {
                    'user': user,
                    'origem': origem,
                    'id_origem': id_origem,
                    'timestamp' : timestamp,
                    'type': 'd',
                    'description': description,
                    'category': category,
                    'especie': especie,
                    'destinatario': destinatario,
                    'amount': amount
                }
        
        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return "Formato de data inválido."
        
        year = str(date.year)
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"

        db.child("financeiro").child('transactions').child(year).child(month).child(day).child('transactions').push(transation)

        post_transaction_lancamentos(month=month, year=year, type=transation['amount'], amount=amount)
        post_caixa(amount=amount, type=transation['type'])

    



