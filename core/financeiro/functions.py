
from config import db

def post_transaction_lancamentos(month, year, type, amount):

        if type == 'c':
            get_credito = db.child("financeiro").child('lancamentos').child(year).child(month).child('receita').get().val() or 0
          
            valor_atualizado = "{:.2f}".format(float(get_credito) + float(amount))
            
            db.child("financeiro").child('lancamentos').child(year).child(month).child('receita').set(valor_atualizado)

        else: 
            get_despesas = db.child("financeiro").child('lancamentos').child(year).child(month).child('despesas').get().val() or 0

            valor_atualizado = "{:.2f}".format(float(get_despesas) - float(amount))
            
            db.child("financeiro").child('lancamentos').child(year).child(month).child('despesas').set(valor_atualizado)

def post_caixa(amount, type):
        
        get_caixa = db.child("financeiro").child('caixa').get().val() or 0

        if type == 'c':
            caixa = "{:.2f}".format(float(get_caixa) + float(amount))
        else:
            caixa = "{:.2f}".format(float(get_caixa) - float(amount))

        db.child("financeiro").child('caixa').set(caixa)