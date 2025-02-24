from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from config import db, auth
from functools import wraps
from operator import itemgetter
from collections import defaultdict
from datetime import datetime
from core.lancamento.class_financeiro import Financeiro
app = Flask(__name__)
app.secret_key = 'secret'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['localId']
            session['email'] = email

            user_data = db.child("users").child(user['localId']).get().val()
            session['role'] = user_data.get('role', 'user')
            session['name'] = user_data.get('name')
            
            if session['role'] == 'admin':
                return redirect(url_for('homepage'))
        except:
            return "Falha no login"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('email', None)
    return redirect(url_for('login'))

def check_roles(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            user_role = db.child("users").child(session['user']).get().val().get('role')  # type: ignore
            if user_role not in allowed_roles:
                return "Acesso negado"
            return f(*args, **kwargs)

        return decorated_function

    return decorator

@app.route('/')
@check_roles(['admin'])
def homepage():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_email = session.get('email', 'Usuário')
    return render_template('index.html', user_email=user_email)

def convert_monetary_value(value_str):
    clean_value = value_str.replace('.', '').replace(',', '.')

    return clean_value

@app.route('/lancamentos', methods=['GET'])
@check_roles(['admin'])
def lancamentos():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Captura o mês e o ano selecionados no formulário
    mes = request.args.get('mes', default=2, type=int)
    ano = request.args.get('ano', default=2025, type=int)

    # Supondo que você já tenha a função que busca as transações do Firebase
    transactions_list = get_transactions_by_month(ano, mes)  # Retorna as transações do mês selecionado

    caixa = db.child("financeiro").child('caixa').get().val()

    saldo = {}
    receita = 0
    despesas = 0

    destinatarios = db.child("financeiro").child('destinarios').get().val()

    for day in transactions_list:
        for id in transactions_list[day]['transactions']:
            amount = float(transactions_list[day]['transactions'][id]['amount'])  # Converter para float
            if transactions_list[day]['transactions'][id]['type'] == 'c':
                saldo[day] = saldo.get(day, 0) + amount
                receita += amount
            else:
                saldo[day] = saldo.get(day, 0) - amount
                despesas += amount
    
    dias_ordenados = sorted(saldo.keys())  # Ordena os dias em ordem crescente

    for i in range(1, len(dias_ordenados)):
        dia_anterior = dias_ordenados[i - 1]
        dia_atual = dias_ordenados[i]
        saldo[dia_atual] += (saldo[dia_anterior])      

    resultado = "{:.2f}".format(receita - despesas)


    # Passar lista de meses e anos para o template para popular o select
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    anos = [2024, 2025]  # Pode expandir essa lista conforme necessário

    return render_template('lancamentos.html', transactions=transactions_list, ano=ano, mes=mes, saldo=saldo, receita="{:.2f}".format(receita), despesas="{:.2f}".format(despesas), resultado=resultado, meses=meses, anos=anos, destinatarios=destinatarios, caixa=caixa)

def get_transactions_by_month(year, month):
    transactions_path = f"financeiro/transactions/{year}/{int(month):02}"
    month_transactions_data = db.child(transactions_path).get().val() or {}
    return month_transactions_data

# Função para exibir transações formatadas (por exemplo, em HTML)
def display_transactions(transactions):
    for transaction in transactions:
        day = transaction['day']
        description = transaction['description']
        amount = float(transaction['amount'])
        trans_type = transaction['type']  # 'c' para crédito, 'd' para débito
        
        # Formatação de débito/crédito
        if trans_type == 'c':
            amount_display = f"<span style='color: green;'>{amount:.2f}</span>"
        else:
            amount_display = f"<span style='color: red;'>-{amount:.2f}</span>"
        
        # Exibir os dados
        print(f"Dia: {day} - {description} - {amount_display}")


@app.route('/post_lancamento', methods=['POST', 'GET'])
def post_lancamento():

    user = session['name']
    id_origem = session['user']
    
    origem = request.form.get('origem')
    type = request.form.get('typeTransaction')
    date = request.form.get('date')
    amount = convert_monetary_value(request.form.get('amount'))
    category = request.form.get('categoria').title()
    especie = request.form.get('especie').title()
    destinatario = request.form.get('destinatario')
    description = request.form.get('descricao')

    Financeiro.post_transaction_credito_tecnico(date=date, type=type, amount=amount, category=category, description=description, especie=especie, destinatario=destinatario, user=user, origem=origem, id_origem=id_origem)

    return redirect(url_for('lancamentos'))

@app.route('/cadastrar_destinatario', methods=['POST', 'GET'])
def cadastrar_destinatario():
    name = request.form.get('namedestinatario').title()

    db.child("financeiro").child('destinarios').push(name)

    return redirect(url_for('lancamentos'))

@app.route('/delete_transaction', methods=['POST', 'GET'])
def delete_transaction():
    date = request.form.get('deleteDate')
    id_transaction = request.form.get('deleteTransactionId')

    try:
        
        date = datetime.strptime(date, '%Y-%m-%d')

        year = str(date.year)
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"
    
    except ValueError:
            return "Formato de data inválido."
        
    

    transaction =  dict(db.child("financeiro").child('transactions').child(year).child(month).child(day).child('transactions').child(id_transaction).get().val())

    get_caixa = db.child("financeiro").child('caixa').get().val()


    if transaction['type'] == 'c':

        get_credito = db.child("financeiro").child('lancamentos').child(year).child(month).child('receita').get().val() or 0
        valor_atualizado = "{:.2f}".format(float(get_credito) - float(transaction['amount']))
        
        db.child("financeiro").child('lancamentos').child(year).child(month).child('receita').set(valor_atualizado)

        caixa = "{:.2f}".format(float(get_caixa) - float(transaction['amount']))

    else:
        get_credito = db.child("financeiro").child('lancamentos').child(year).child(month).child('despesas').get().val() or 0
        valor_atualizado = "{:.2f}".format(float(get_credito) + float(transaction['amount']))
        
        db.child("financeiro").child('lancamentos').child(year).child(month).child('despesas').set(valor_atualizado)

        caixa = "{:.2f}".format(float(get_caixa) + float(transaction['amount']))
    
    db.child("financeiro").child('caixa').set(caixa)

    db.child("financeiro").child('transactions').child(year).child(month).child(day).child('transactions').child(id_transaction).remove()

    return redirect(url_for('lancamentos'))


@app.route('/novo_lancamento', methods=['GET'])
@check_roles(['admin'])
def novo_lancamento():
    if 'user' not in session:
        return redirect(url_for('login'))

    destinatarios = db.child("financeiro").child('destinarios').get().val()


    return render_template('novo_lancamento.html', destinatarios=destinatarios)

@app.route('/profile_user/<id>', methods=['GET', 'POST'])
@check_roles(['admin'])
def profile_user(id):
    if 'user' not in session:
        return redirect(url_for('login'))

    name = db.child("users").child(id).child('name').get().val()

    cities = db.child('users').child(id).child('cities').get().val() or 0
    print(cities)


    return render_template('profile_user.html', name=name, cities=cities)

@app.route('/lancamento_programado', methods=['GET', 'POST'])
@check_roles(['admin'])
def lancamento_programado():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    destinatarios = db.child("financeiro").child('destinarios').get().val()

    return render_template('lancamento_programado.html', destinatarios=destinatarios)

@app.route('/post_novo_lancamento_programado', methods=['POST'])
def receber_lancamento():
    # Captura os dados do formulário
    type = request.form.get('typeTransaction')
    origem = request.form.get('origem')
    amount = request.form.get('amount')
    date = request.form.get('date')
    category = request.form.get('categoria')
    especie = request.form.get('especie')
    destinatario = request.form.get('destinatario')
    description = request.form.get('descricao')
    
    data = {
        'origem': origem,
        'type': type,
        'category': category.title(),
        'especie': especie.title(),
        'destinatario': destinatario,
        'description': description,
        'vencimento': date,
        'amount': convert_monetary_value(amount)    
    }
    
    Financeiro.post_programar_lancamento(date=date, data=data)
    
    # Retorne uma resposta JSON para indicar sucesso
    return jsonify({"message": "Lançamento recebido com sucesso!"}), 200


@app.route('/get_transactions_pendding/<ano>/<mes>')
def get_transactions_pendding(ano, mes):
    # Pega as transações do Firebase usando o ano e o mês
    transactions = db.child("financeiro").child('transactions_programadas').child('pedding').child(ano).child(mes).get().val()
    
    # Converte OrderedDict para lista de dicionários
    transactions_list = []
    if transactions:
        for key, value in transactions.items():
            transaction = value
            transaction['id'] = key
            transactions_list.append(transaction)
        
        # Ordena a lista de transações pela data de vencimento em ordem crescente
        transactions_list = sorted(
            transactions_list,
            key=lambda x: datetime.strptime(x['vencimento'], '%Y-%m-%d') if 'vencimento' in x and x['vencimento'] else datetime.min
        )

    # Retorna em formato JSON
    return jsonify(transactions_list)


@app.route('/post_confirmar_pagamento_programado', methods=['POST'])
def post_confirmar_pagamento_programado():
    # Captura os dados do formulário
    id = request.form.get('confirmarPagamentId')
    data_vencimento = request.form.get('dataVencimento')
    tipo_pagamento = request.form.get('pagamentototalparcial')
    amount = convert_monetary_value(request.form.get('newamount'))
    date_paymment = request.form.get('newdate')

    try:
        date = datetime.strptime(data_vencimento, '%Y-%m-%d')
    except ValueError:
            return "Formato de data inválido."
            
    year = str(date.year)
    month = f"{date.month:02d}"

    transaction = db.child("financeiro").child('transactions_programadas').child('pedding').child(year).child(month).child(id).get().val()
    
    transaction['datapagamento'] = date_paymment
    transaction['valorpago'] = amount
    if tipo_pagamento == 'total':
        
        Financeiro.post_transaction_credito_tecnico(date=date_paymment, type=transaction['type'], amount=amount, category=transaction['category'], description=transaction['description'], especie=transaction['especie'], destinatario=transaction['destinatario'], user=session['name'], origem=transaction['origem'], id_origem='')
        
        Financeiro.post_confirmar_pagamento_programado(date=date_paymment, data=transaction)

        transaction = db.child("financeiro").child('transactions_programadas').child('pedding').child(year).child(month).child(id).remove()
    
    else:
        amount_parcial = "{:.2f}".format(float(transaction['amount']) - float(amount))
        

        db.child("financeiro").child('transactions_programadas').child('pedding').child(year).child(month).child(id).child('amount').set(amount_parcial)

        db.child("financeiro").child('transactions_programadas').child('pedding').child(year).child(month).child(id).child('parcial').set(True)

        Financeiro.post_confirmar_pagamento_programado(date=date_paymment, data=transaction)
    
    # Retorne uma resposta JSON para indicar sucesso
    return jsonify({"message": "Lançamento recebido com sucesso!"}), 200


@app.route('/get_transactions_paid/<ano>/<mes>')
def get_transactions_paid(ano, mes):
    # Pega as transações do Firebase usando o ano e o mês
    transactions = db.child("financeiro").child('transactions_programadas').child('paid').child(ano).child(mes).get().val()
    
    # Converte OrderedDict para lista de dicionários
    transactions_list = []
    if transactions:
        for key, value in transactions.items():
            transaction = value
            transaction['id'] = key
            transactions_list.append(transaction)
        
        # Ordena a lista de transações pela data de vencimento em ordem crescente
        transactions_list = sorted(
            transactions_list,
            key=lambda x: datetime.strptime(x['vencimento'], '%Y-%m-%d') if 'vencimento' in x and x['vencimento'] else datetime.min
        )

    # Retorna em formato JSON
    return jsonify(transactions_list)


@app.route('/delete_transaction_programada/<id>', methods=['DELETE'])
def delete_transaction_programada(id):
    # Captura `year` e `month` dos parâmetros de consulta

    date = request.args.get('date')
    
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
            return "Formato de data inválido."
            
    year = str(date.year)
    month = f"{date.month:02d}"
    
    try:

        db.child("financeiro").child('transactions_programadas').child('pedding').child(year).child(month).child(id).remove()

        return jsonify({'success': True, 'message': 'Transação cancelada com sucesso'}), 200
    except Exception as e:
        print(f"Erro ao deletar transação: {e}")
        return jsonify({'error': 'Erro ao cancelar a transação'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5039)
