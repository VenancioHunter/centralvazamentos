from config import db
import datetime
import pytz
from core.lancamento.functions import post_transaction_lancamentos, post_caixa

class Financeiro:

    

    def post_transaction_credito_tecnico(date, amount, description, type, category, especie, destinatario, user, origem, id_origem):

        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
        now_in_sao_paulo = datetime.datetime.now(sao_paulo_tz)
        timestamp = now_in_sao_paulo.timestamp()

        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return "Formato de data inválido."
        
        year = str(date.year)
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"

        transation = {
                    'origem': origem,
                    'id_origem': id_origem,
                    'user': user,
                    'timestamp' : timestamp,
                    'type': type,
                    'category': category,
                    'especie': especie,
                    'destinatario': destinatario,
                    'description': description,
                    'amount': amount
                }

        db.child("financeiro").child('transactions').child(year).child(month).child(day).child('transactions').push(transation)

        post_transaction_lancamentos(year=year, month=month, type=transation['type'], amount=amount)
        post_caixa(amount=amount, type=transation['type'])

    
    def post_programar_lancamento(date, data):

        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return "Formato de data inválido."
        
        year = str(date.year)
        month = f"{date.month:02d}"
        
        db.child("financeiro").child('transactions_programadas').child('pedding').child(year).child(month).push(data)

    def post_confirmar_pagamento_programado(date, data):
    
        try:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
      
        except ValueError:
            return "Formato de data inválido."
        
        year = str(date.year)
        month = f"{date.month:02d}"

        
        db.child("financeiro").child('transactions_programadas').child('paid').child(year).child(month).push(data)
