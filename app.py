from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pyrebase
from config import firebase_config
from functools import wraps
from datetime import datetime
import time
import json
from core.attendance.class_attendance import Attendance
from core.wallet.class_wallet_os import Wallet
from core.user.class_user_wallet import User_Wallet
from core.user.class_user import User
import pytz
from config import db, auth
from collections import defaultdict
from core.cities.class_cities import Cities


app = Flask(__name__)
app.secret_key = 'secret'


def datetimeformat(value, format='%d/%m/%Y %H:%M:%S'):
    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
    
    # Converta o timestamp para o horário de São Paulo
    dt_sao_paulo = datetime.fromtimestamp(value, sao_paulo_tz)
    
    # Formate a data e hora no formato desejado
    return dt_sao_paulo.strftime(format)

def datetimeformathour(value, format='%H:%M'):
    return datetime.strptime(value, '%Y-%m-%d %H:%M').strftime(format)

# Registre o filtro no ambiente Jinja2
app.jinja_env.filters['datetimeformat'] = datetimeformat

app.jinja_env.filters['datetimeformathour'] = datetimeformathour

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
                return redirect(url_for('admin'))
            
            elif session['role'] == 'user':
                return redirect(url_for('dashboard'))
            
            elif session['role'] == 'tecnico':
                return redirect(url_for('dashboard_tecnico'))  
        except:
            return "Falha no login"
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user_with_email_and_password(email, password)
            # Defina o nível de acesso padrão e salve o nome do usuário
            db.child("users").child(user['localId']).set({
                "name": name,
                "email": email,
                "password": password,
                "role": "user",  # Define o papel padrão como 'user'
                "cities": []  # Lista de cidades vazia por padrão
            })
            return redirect(url_for('login'))
        except:
            return "Falha no cadastro"
    return render_template('signup.html')


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


@app.route("/", methods=["POST", "GET"])
def homepage():
    if 'user' not in session:
        return redirect(url_for('login'))
    else:
        if session['role'] == 'user':
            return redirect(url_for('dashboard'))
        
        elif session['role'] == 'tecnico':
            return redirect(url_for('dashboard_tecnico'))
        elif session['role'] == 'admin':
            return redirect(url_for('admin'))


@app.route('/dashboard')
@check_roles(['user', 'admin'])
def dashboard():
    user_email = session.get('email', 'Usuário')
    return render_template('dashboard.html', user_email=user_email)

@app.route('/dashboard_tecnico')
@check_roles(['tecnico'])
def dashboard_tecnico():
    user_email = session.get('email', 'Usuário')
    return render_template('dashboard_tecnico.html', user_email=user_email)


@app.route('/admin')
@check_roles('admin')
def admin():
    user_email = session.get('email', 'Admin')
    return render_template('admin.html', user_email=user_email)

@app.route('/attendance')
@check_roles('admin')
def attendance():
    return render_template('attendance.html')


@app.route('/add_city', methods=['GET', 'POST'])
@check_roles(['admin'])
def add_city():
    if request.method == 'POST':
        city_name = request.form['city']

        # Verifique se a cidade já existe
        cities = db.child("cities").get().val() or {}
        if city_name not in cities.values():
            db.child("cities").push(city_name)
            return redirect(url_for('add_city'))
        else:
            return "Cidade já existe"

    return render_template('add_city.html')


@app.route('/list_cities')
@check_roles(['admin'])
def list_cities():
    cities = db.child("cities").get().val() or {}
    return render_template('list_cities.html', cities=cities)


@app.route('/link_user_city', methods=['GET', 'POST'])
@check_roles(['admin'])
def link_user_city():
    if request.method == 'POST':
        user_id = request.form['user_id']
        city = request.form['city']

        # Obtenha as cidades atuais do usuário
        user_cities = db.child("users").child(user_id).child("cities").get().val() or []

        if city not in user_cities:
            user_cities.append(city)
            db.child("users").child(user_id).update({"cities": user_cities})

        return "Usuário vinculado à cidade com sucesso"

    # Obtenha todos os usuários e cidades para o formulário
    users = db.child("users").get().val()

    # Filtrar apenas os usuários com papel "user"
    user_role = 'user'
    users = {user_id: user for user_id, user in users.items() if user.get('role') == user_role}

    cities = db.child("cities").get().val() or {}

    return render_template('link_user_city.html', users=users, cities=cities)


def convert_monetary_value(value_str):
    clean_value = value_str.replace('.', '').replace(',', '.')

    return clean_value


@app.route('/attendance_records', methods=['GET', 'POST'])
@check_roles(['user', 'admin'])
def attendance_records():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']

    if request.method == 'POST':
        # Dados do formulário
        canal = request.form['canal']
        name = request.form['name']
        sexo = request.form['sexo']
        phone = request.form['phone']
        price = request.form['price']
        city = request.form['city']
        service = request.form['service']
        status = "Aguardando"
        details = request.form['details']

        price = convert_monetary_value(price)

        sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

        now_in_sao_paulo = datetime.now(sao_paulo_tz)

        timestamp = now_in_sao_paulo.timestamp()

        # Obter a data atual
        
        now = datetime.now(sao_paulo_tz)
        year = str(now.year)
        month = f"{now.month:02d}"  # Garantir que o mês tenha dois dígitos
        day = f"{now.day:02d}"  # Garantir que o dia tenha dois dígitos

        # Criar um registro de atendimento
        attendance_record = {
            "user_id": user_id,
            "name": name,
            "sexo": sexo,
            "phone": phone,
            "price": price,
            "service": service,
            "status": status,
            "details": details,
            "canal": canal,
            "timestamp": timestamp
        }

        # Salvar o registro de atendimento sob a estrutura desejada
        db.child("attendance_records").child(city).child(year).child(month).child(day).push(attendance_record)
        return redirect(url_for('dashboard'))

    # Carregar as cidades vinculadas ao usuário
    user_data = db.child("users").child(user_id).get().val()
    cities = user_data.get('cities', [])

    # Carregar todos os serviços disponíveis
    services = db.child("services").get().val() or {}

    return render_template('attendance_records.html', cities=cities, services=services)


@app.route('/add_service', methods=['GET', 'POST'])
@check_roles(['admin'])
def add_service():
    if request.method == 'POST':
        service_name = request.form['service']

        # Verifique se o serviço já existe
        services = db.child("services").get().val() or {}
        if service_name not in services.values():
            db.child("services").push(service_name)
            return "Serviço adicionado com sucesso"
        else:
            return "Serviço já existe"

    return render_template('add_service.html')


@app.route('/list_services')
@check_roles(['admin'])
def list_services():
    services = db.child("services").get().val() or {}
    return render_template('list_services.html', services=services)


@app.route('/consulta_atendimentos', methods=['GET', 'POST'])
@check_roles(['user', 'admin'])
def consulta_atendimentos():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']

    # Carregar as cidades vinculadas ao usuário
    user_data = db.child("users").child(user_id).get().val()
    cities = user_data.get('cities', [])

    return render_template('consulta_atendimentos.html', cities=cities)

@app.route('/adm_consulta_atendimentos', methods=['GET', 'POST'])
@check_roles(['user', 'admin'])
def adm_consulta_atendimentos():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']

    # Carregar as cidades vinculadas ao usuário
    cities = db.child("cities").get().val().values()

    return render_template('adm_consulta_atendimentos.html', cities=cities)
    


@app.route('/view_attendance', methods=['GET'])
@check_roles(['user', 'admin'])
def view_attendance():
    city = request.args.get('city')
    date_str = request.args.get('date')

    if not city or not date_str:
        return "Cidade ou data não fornecida."

    # Verifique se o usuário tem permissão para acessar esta cidade
    user_id = session['user']
    user_data = db.child("users").child(user_id).get().val()

    if city not in user_data.get('cities', []):
        return "Você não tem permissão para acessar registros desta cidade."

    # Converter a data fornecida para ano, mês e dia
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return "Formato de data inválido."

    year = str(date.year)
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"

    # Obtenha todos os registros de atendimento para a cidade e data especificadas
    attendance_records = db.child("attendance_records").child(city).child(year).child(month).child(
        day).get().val() or {}

    all_users = db.child("users").get().val() or {}
    tecnicos = {uid: user for uid, user in all_users.items() if
                user['role'] == 'tecnico' and city in user.get('cities', [])}

    return render_template('view_attendance.html', records=attendance_records, city=city, date=f"{day}/{month}/{year}",
                           tecnicos=tecnicos)

@app.route('/adm_view_attendance', methods=['GET'])
@check_roles(['user', 'admin'])
def adm_view_attendance():
    city = request.args.get('city')
    date_str = request.args.get('date')

    if not city or not date_str:
        return "Cidade ou data não fornecida."

    # Verifique se o usuário tem permissão para acessar esta cidade
    user_id = session['user']
    user_data = db.child("users").child(user_id).get().val()

    is_admin = user_data.get('role') == 'admin'
    has_city_permission = city in user_data.get('cities', [])

    if not (is_admin or has_city_permission):
        return "Você não tem permissão para acessar registros desta cidade."

    # Converter a data fornecida para ano, mês e dia
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return "Formato de data inválido."

    year = str(date.year)
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"

    # Obtenha todos os registros de atendimento para a cidade e data especificadas
    attendance_records = db.child("attendance_records").child(city).child(year).child(month).child(
        day).get().val() or {}

    all_users = db.child("users").get().val() or {}
    tecnicos = {uid: user for uid, user in all_users.items() if
                user['role'] == 'tecnico' and city in user.get('cities', [])}

    return render_template('view_attendance.html', records=attendance_records, city=city, date=f"{day}/{month}/{year}",
                           tecnicos=tecnicos)


from collections import defaultdict

@app.route('/view_all_attendances', methods=['GET', 'POST'])
@check_roles(['admin'])
def view_all_attendances():
    if request.method == 'POST':
        selected_date = request.form.get('selected_date')

        if selected_date:
            year, month, day = selected_date.split('-')

            attendance_data = db.child("attendance_records").get().val() or {}

            # Dicionário para agrupar atendimentos por user_id
            grouped_records = defaultdict(list)

            for city, years in attendance_data.items():
                if year in years:
                    months = years[year]
                    if month in months:
                        days = months[month]
                        if day in days:
                            attendances = days[day]
                            for attendance_id, attendance_info in attendances.items():
                                user_id = attendance_info.get('user_id')
                                
                                if user_id:
                                    # Obtém o nome do usuário baseado no user_id
                                    user_name = User.get_name(user_id)

                                    record = {
                                        "city": city,
                                        "date": f"{day}/{month}/{year}",
                                        **attendance_info
                                    }
                                    
                                    # Agrupa pelo nome do usuário
                                    grouped_records[user_name].append(record)
                                else:
                                    # Se user_id não estiver presente, continue ou log um erro
                                    print(f"User ID ausente para o atendimento {attendance_id}")

            return render_template('view_all_attendances.html', grouped_records=grouped_records, selected_date=selected_date)
    else:
        return render_template('view_all_attendances.html', grouped_records={}, selected_date=None)


@app.route('/vincular_tecnico', methods=['GET', 'POST'])
@check_roles(['admin'])
def vincular_tecnico():
    if request.method == 'POST':
        tecnico_id = request.form['tecnico']
        novas_cidades = set(request.form.getlist('cidades'))  # Recebe lista de cidades selecionadas

        # Recuperar as cidades atualmente vinculadas ao técnico
        tecnico_data = db.child("users").child(tecnico_id).get().val()
        cidades_atuais = set(tecnico_data.get('cities', []))

        # Combinar as cidades atuais com as novas
        cidades_atualizadas = list(cidades_atuais.union(novas_cidades))

        # Atualizar as cidades no banco de dados para o técnico selecionado
        db.child("users").child(tecnico_id).update({"cities": cidades_atualizadas})

        return redirect(url_for('vincular_tecnico'))

    # Carregar todos os técnicos e cidades disponíveis
    all_users = db.child("users").get().val() or {}
    tecnicos = {uid: user for uid, user in all_users.items() if user['role'] == 'tecnico'}
    all_cities = db.child("cities").get().val() or {}

    return render_template('vincular_tecnico.html', tecnicos=tecnicos, all_cities=all_cities)


@app.route('/verifica_agenda', methods=['POST', 'GET'])
def verifica_agenda():
    data = request.json
    date = data.get('date')
    start_time = data.get('startTime')
    end_time = data.get('endTime')
    tecnico_id = data.get('technician')

    date_str = date
    date_firebase = datetime.strptime(date_str, '%Y-%m-%d')

    year = str(date_firebase.year)
    month = f"{date_firebase.month:02d}"  # Garantir que o mês tenha dois dígitos
    day = f"{date_firebase.day:02d}"  # Garantir que o dia tenha dois dígitos

    # Combine date and time to create datetime objects
    start_datetime = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
    end_datetime = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M')

    cities = db.child('users').child(tecnico_id).child('cities').get().val()

    for city in cities:

        #os_existentes = db.child("ordens_servico").order_by_child("tecnico_id").equal_to(tecnico_id).get().val() or {}
        os_existentes = db.child("ordens_servico").child(city).child(year).child(month).child(
            day).order_by_child("tecnico_id").equal_to(tecnico_id).get().val() or {}

        for os_id, os_data in os_existentes.items():
            os_start = datetime.strptime(os_data['start_datetime'], '%Y-%m-%d %H:%M')
            os_end = datetime.strptime(os_data['end_datetime'], '%Y-%m-%d %H:%M')

            # Check for overlapping times
            if not (end_datetime <= os_start or start_datetime >= os_end):
                print(f"O técnico já possui uma OS agendada nesse horário.")
                return jsonify({'status': 'conflict', 'message': 'O técnico já possui uma OS agendada nesse horário.'}), 400
            

    return jsonify({'status': 'success', 'message': 'Horário livre'}), 200

@app.route('/gerar_os', methods=['POST'])
def gerar_os():
    city = request.form.get('city')
    date_filter = request.form.get('date')
    id_attendance = request.form.get('idRecord')

    date = request.form.get('dateos')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    tecnico_id = request.form.get('tecnico')

    # Combine date and time to create datetime objects
    start_datetime = datetime.strptime(f"{date} {start_time}", '%Y-%m-%d %H:%M')
    end_datetime = datetime.strptime(f"{date} {end_time}", '%Y-%m-%d %H:%M')

    data_datetime = datetime.strptime(date_filter, '%d/%m/%Y')
    # Formatar o objeto datetime no formato desejado aaaa-mm-dd
    data_formatada = data_datetime.strftime('%Y-%m-%d')
    # Check availability for each selected technician

    # Save the new OS to the database

    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')

    now_in_sao_paulo = datetime.now(sao_paulo_tz)

    timestamp = now_in_sao_paulo.timestamp()

    newprice = request.form.get('priceservice')
    if not newprice:
        newprice = "0.00"
    else:
        newprice = convert_monetary_value(newprice)
    
    nova_os = {
        "city": request.form.get('city'),
        "name": request.form.get('name'),
        "phone": request.form.get('phone'),
        "service": request.form.get('service'),
        "oldprice": request.form.get('price'),
        "newprice": newprice,
        "start_datetime": start_datetime.strftime('%Y-%m-%d %H:%M'),
        "end_datetime": end_datetime.strftime('%Y-%m-%d %H:%M'),
        "tecnico_id": tecnico_id,
        "timestamp": timestamp,
        "user_id": session['user'],
        "address": {
            "numero": request.form.get('numerocasa'),
            "rua":request.form.get('rua'),
            "bairro": request.form.get('bairro'),
            "complemento": request.form.get('enderecocomplemento'),
            "localizacao": request.form.get('localizacao')
        }
    }

    date_str = request.form.get('dateos')
    date = datetime.strptime(date_str, '%Y-%m-%d')

    year = str(date.year)
    month = f"{date.month:02d}"  # Garantir que o mês tenha dois dígitos
    day = f"{date.day:02d}"  # Garantir que o dia tenha dois dígitos

    #db.child("ordens_servico").push(nova_os)
    Attendance.update_status(id=id_attendance, city=city, date=data_formatada)

    db.child("ordens_servico").child(city).child(year).child(month).child(day).push(nova_os)

    return redirect(url_for('dashboard'))

@app.route('/consulta_agenda', methods=['GET', 'POST'])
@check_roles(['tecnico'])
def consulta_agenda():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template('consulta_agenda.html')

@app.route('/view_schedule', methods=['GET'])
@check_roles(['tecnico'])
def view_schedule():
    date_str = request.args.get('date')
    # Converter a data fornecida para ano, mês e dia
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return "Formato de data inválido."

    
    year = str(date.year)
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"
    
    # Obtenha o ID do técnico logado
    tecnico_id = session['user']
    
    cities = db.child('users').child(session['user']).child('cities').get().val()

    all_ordens_servico = {}
    
    # Buscar ordens de serviço para cada cidade
    for city in cities:
        ordens_servico_path = f"ordens_servico/{city}/{year}/{month}/{day}"
        os_agendadas = db.child(ordens_servico_path).get().val() or {}
        all_ordens_servico.update(os_agendadas)
    
    # Filtrar as ordens de serviço para o técnico logado
    ordens_servico_tecnico = {os_id: os for os_id, os in all_ordens_servico.items() if os.get('tecnico_id') == tecnico_id}
    
    ordens_servico_ordenadas = dict(sorted(
        ordens_servico_tecnico.items(),
        key=lambda item: datetime.strptime(item[1]['start_datetime'], '%Y-%m-%d %H:%M')
    ))

    costs_day = User_Wallet.verify_costs(id=tecnico_id, date=date)

    return render_template('view_schedule.html', ordens_servico=ordens_servico_ordenadas, cities=cities, date=date_str, costs_day=costs_day)

@app.route('/consulta_os_atendente', methods=['GET', 'POST'])
@check_roles(['user', 'admin'])
def consulta_os_atendente():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']

    # Carregar as cidades vinculadas ao usuário
    user_data = db.child("users").child(user_id).get().val()
    cities = user_data.get('cities', [])

    return render_template('consulta_os_atendente.html', cities=cities)

@app.route('/view_schedule_atendente', methods=['GET'])
@check_roles(['user'])
def view_schedule_atendente():
    city = request.args.get('city')
    date_str = request.args.get('date')

    if not city or not date_str:
        return "Cidade ou data não fornecida."

    # Verifique se o usuário tem permissão para acessar esta cidade
    user_id = session['user']
    user_data = db.child("users").child(user_id).get().val()

    if city not in user_data.get('cities', []):
        return "Você não tem permissão para acessar registros desta cidade."

    # Converter a data fornecida para ano, mês e dia
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return "Formato de data inválido."

    
    year = str(date.year)
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"
    
    # Obtenha o ID do técnico logado
    tecnico_id = session['user']
    
    
    ordens_servico_path = f"ordens_servico/{city}/{year}/{month}/{day}"
    os_agendadas = db.child(ordens_servico_path).get().val() or {}
    
    all_users = db.child("users").get().val() or {}
    tecnicos = {uid: user for uid, user in all_users.items() if
                user['role'] == 'tecnico' and city in user.get('cities', [])}
    
    ordens_servico_ordenadas = dict(sorted(
        os_agendadas.items(),
        key=lambda item: datetime.strptime(item[1]['start_datetime'], '%Y-%m-%d %H:%M')
    ))



    return render_template('view_schedule_atendente.html', ordens_servico=ordens_servico_ordenadas, city=city, date=date_str, tecnicos=tecnicos)

@app.route('/reagendar_os', methods=['GET', 'POST'])
@check_roles(['user', 'admin'])
def reagendar_os():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_id = session['user']

    city = request.form.get('city')
    old_id = request.form.get("idRecord")
    old_date = request.form.get("osOldDate")
    new_date = request.form.get("dateos")
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    tecnico_id = request.form.get('tecnico')

    # Converte as datas e horas para objetos datetime
    start_datetime = datetime.strptime(f"{new_date} {start_time}", '%Y-%m-%d %H:%M')
    end_datetime = datetime.strptime(f"{new_date} {end_time}", '%Y-%m-%d %H:%M')

    # Define o fuso horário de São Paulo
    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
    now_in_sao_paulo = datetime.now(sao_paulo_tz)

    # Obtém o timestamp atual
    timestamp = now_in_sao_paulo.timestamp()

    # Tenta converter a data antiga para objetos ano, mês e dia
    try:
        date = datetime.strptime(old_date, '%Y-%m-%d')
    except ValueError:
        return "Formato de data inválido."

    year = str(date.year)
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"

    # Obter o registro antigo
    path_old_os = f"ordens_servico/{city}/{year}/{month}/{day}"
    get_os = db.child(path_old_os).child(old_id).get().val() or {}

    if get_os:
        # Converte start_datetime e end_datetime para strings formatadas
        get_os["start_datetime"] = start_datetime.strftime('%Y-%m-%d %H:%M')
        get_os["end_datetime"] = end_datetime.strftime('%Y-%m-%d %H:%M')
        get_os["timestamp"] = timestamp
        get_os["tecnico_id"] = tecnico_id

        # Tenta converter a nova data para ano, mês e dia
        try:
            date = datetime.strptime(new_date, '%Y-%m-%d')
        except ValueError:
            return "Formato de data inválido."

        year = str(date.year)
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"

        # Salva os dados no Firebase com o novo ID gerado automaticamente
        db.child("ordens_servico").child(city).child(year).child(month).child(day).push(get_os)

        db.child(path_old_os).child(old_id).remove()
        

    return redirect(url_for('consulta_os_atendente'))

@app.route('/finalizar_os', methods=['POST'])
def finalizar_os():
    # Recebe os dados enviados pelo formulário
    data = request.json
   
    # Inicializa as variáveis de categorização
    status_pagamento = None
    detalhes_pagamento = {}

    os_id = data.get('os_id')
    os_city = data.get('os_city')
    os_date = data.get('os_date')

    create_paymment = {}

    # Tenta converter a nova data para ano, mês e dia
    try:
            date_firebase = datetime.strptime(os_date, '%Y-%m-%d')
    except ValueError:
            return "Formato de data inválido."

    year = str(date_firebase.year)
    month = f"{date_firebase.month:02d}"
    day = f"{date_firebase.day:02d}"

    if data.get('statusPaymment') == 'received':
        
        # Filtra os dados e categoriza
        if data.get("method") in ["pix", "dinheiro"]:
            # Pagamentos recebidos
            status_pagamento = "recebido"
            detalhes_pagamento["valor"] = data.get("amount")
            detalhes_pagamento["metodo"] = data.get("method")

            create_paymment ={
                'os_id': os_id,
                'os_date': os_date,
                'tecnico_id': session['user'],
                'method': data.get('method'),
                'amount': convert_monetary_value(data.get('amount')),
            }

            try: 
                Wallet.create_paymment_success(data=create_paymment, date=os_date, city=os_city)

                Wallet.update_status_os(id=os_id, city=os_city, date=os_date, status_paymment=status_pagamento)

                User_Wallet.create_transaction_success(data=create_paymment, date=os_date, city=os_city, id_tecnico=session['user'])

                
            
            except:
                return jsonify({'status': 'conflict', 'message': 'Erro.'}), 400

        
        elif data.get("method") == "cartao":
            status_pagamento = "recebido"
            detalhes_pagamento["valor"] = data.get("cardValor")
            detalhes_pagamento["parcelas"] = data.get("installments")

            create_paymment ={
                'os_id': os_id,
                'os_date': os_date,
                'tecnico_id': session['user'],
                'method': data.get('method'),
                'amount': convert_monetary_value(data.get('cardValor')),
                'installments': data.get('installments')
            }

            try:
                Wallet.create_paymment_success(data=create_paymment, date=os_date, city=os_city)

                Wallet.update_status_os(id=os_id, city=os_city, date=os_date, status_paymment=status_pagamento)

                User_Wallet.create_transaction_success(data=create_paymment, date=os_date, city=os_city, id_tecnico=session['user'])

            except:
                return jsonify({'status': 'conflict', 'message': 'Erro.'}), 400

    if data.get('statusPaymment') == 'notreceived' or data.get("method") == "boleto":
       
        if data.get("method") == "boleto":
            # Pagamentos a receber
            status_pagamento = "pendente"
            
            create_paymment = {
                'os_id': os_id,
                'os_city': os_city,
                'os_date': os_date,
                'tecnico_id': session['user'],
                'method': data.get('method'),
                'amount': convert_monetary_value(data.get('boletoValor')),
                'vencimento': data.get('vencimento')
            }

            try:
                Wallet.create_paymment_pendding(data=create_paymment, date=os_date, city=os_city)
                Wallet.update_status_os(id=os_id, city=os_city, date=os_date, status_paymment=status_pagamento)
            
            except:
                return jsonify({'status': 'conflict', 'message': 'Erro.'}), 400
            
        elif data.get("method") in ["pix", "dinheiro"]:
            # Pagamentos recebidos
            status_pagamento = "pendente"
            detalhes_pagamento["valor"] = data.get("amount")
            detalhes_pagamento["metodo"] = data.get("method")

            create_paymment ={
                'os_id': os_id,
                'os_date': os_date,
                'os_city': os_city,
                'tecnico_id': session['user'],
                'method': data.get('method'),
                'amount': convert_monetary_value(data.get('amount')),
                'vencimento': os_date
            }

            try: 
                Wallet.create_paymment_pendding(data=create_paymment, date=os_date, city=os_city)
                Wallet.update_status_os(id=os_id, city=os_city, date=os_date, status_paymment=status_pagamento)
                
            
            except:
                return jsonify({'status': 'conflict', 'message': 'Erro.'}), 400

        
        elif data.get("method") == "cartao":
            status_pagamento = "pendente"
            detalhes_pagamento["valor"] = data.get("cardValor")
            detalhes_pagamento["parcelas"] = data.get("installments")

            create_paymment ={
                'os_id': os_id,
                'os_date': os_date,
                'os_city': os_city,
                'tecnico_id': session['user'],
                'method': data.get('method'),
                'amount': convert_monetary_value(data.get('cardValor')),
                'installments': data.get('installments'),
                'vencimento': os_date
            }

            try:
                Wallet.create_paymment_pendding(data=create_paymment, date=os_date, city=os_city)
                Wallet.update_status_os(id=os_id, city=os_city, date=os_date, status_paymment=status_pagamento)


            except:
                return jsonify({'status': 'conflict', 'message': 'Erro.'}), 400


@app.route('/listar_pendentes_tecnico', methods=['GET', 'POST'])
@check_roles(['tecnico'])
def listar_pendentes_tecnico():
    if 'user' not in session:
        return redirect(url_for('login'))

    tecnico_id = session['user']  # ID do técnico logado
    now = datetime.now()
    ano_atual = now.strftime("%Y")
    mes_atual = now.strftime("%m")

    # Receber ano e mês do formulário ou usar os valores padrão (ano e mês atuais)
    if request.method == 'POST':
        ano = request.form.get('ano', ano_atual)
        mes = request.form.get('mes', mes_atual)
    else:
        ano = ano_atual  # Ano atual
        mes = mes_atual  # Mês atual

    # Obter as cidades associadas ao técnico
    cities = db.child('users').child(session['user']).child('cities').get().val()

    all_pendding_transactions = {}

    # Buscar ordens de serviço pendentes para cada cidade
    for city in cities:
        pendding_transactions_path = f"wallet/{city}/{ano}/{mes}"
        paymments_pendding = db.child(pendding_transactions_path).get().val() or {}

        # Agora, em vez de usar `update`, fazemos uma combinação manual para não sobrescrever
        for day, day_data in paymments_pendding.items():
            if day not in all_pendding_transactions:
                all_pendding_transactions[day] = day_data
            else:
                # Verifique se 'transactions' existe em day_data
                if 'transactions' in day_data and 'pendding' in day_data['transactions']:
                    # Mesclar as transações do dia
                    all_pendding_transactions[day]['transactions']['pendding'].update(day_data['transactions']['pendding'])

    pendding_transactions = {}

    # Percorrer os dias e filtrar as transações pendentes do técnico logado
    for day, day_data in all_pendding_transactions.items():
        pendding = day_data.get('transactions', {}).get('pendding', {})
        for trans_id, trans_data in pendding.items():
            if trans_data.get('tecnico_id') == tecnico_id:
                pendding_transactions[trans_id] = trans_data

    # Renderizar as transações filtradas
    return render_template('paymments_pendding_tecnico.html', transactions=pendding_transactions, ano=ano, mes=mes)


@app.route('/extrato_tecnico', methods=['GET', 'POST'])
@check_roles(['tecnico'])
def extrato_tecnico():
    if 'user' not in session:
        return redirect(url_for('login'))

    tecnico_id = session['user']  # ID do técnico logado
    now = datetime.now()
    ano_atual = now.strftime("%Y")
    mes_atual = now.strftime("%m")

    # Receber ano e mês do formulário ou usar os valores padrão (ano e mês atuais)
    if request.method == 'POST':
        ano = request.form.get('ano', ano_atual)
        mes = request.form.get('mes', mes_atual)
    else:
        ano = ano_atual  # Ano atual
        mes = mes_atual  # Mês atual

    participation = User_Wallet.get_participation(id=tecnico_id)
    participation_empresa = 100 - participation
    
    # Obter as cidades associadas ao técnico
    cities = db.child('users').child(session['user']).child('cities').get().val()

    grouped_transactions = {}

    # Buscar ordens de serviço para cada cidade
    for city in cities:
        success_transactions_path = f"wallet/{city}/{ano}/{mes}"
        paymments_success = db.child(success_transactions_path).get().val() or {}

        # Agrupar as transações por dia
        for day, day_data in paymments_success.items():
            success = day_data.get('transactions', {}).get('success', {})
            if day not in grouped_transactions:
                grouped_transactions[day] = {
                    'transactions': [], 
                    'total_amount': 0.0, 
                    'costs': {'combustivel': 0.0, 'manutencao': 0.0, 'pedagio': 0.0, 'reparo': 0.0, 'outros': 0.0}, 
                    'balance': 0.0,
                    'city':city
                }
            for trans_id, trans_data in success.items():
                if trans_data.get('tecnico_id') == tecnico_id:
                    amount = float(trans_data.get('amount', 0))  # Pega o valor da transação
                    grouped_transactions[day]['transactions'].append({
                        'trans_id': trans_id,
                        'data': trans_data,
                        'city': city
                    })
                    grouped_transactions[day]['total_amount'] += amount  # Soma o valor ao total do dia


    # Obter os custos (combustível, manutenção, pedágio) do mês
    costs_path = f"users/{session['user']}/wallet/costs/{ano}/{mes}"
    month_costs_data = db.child(costs_path).get().val() or {}

    # Somar os custos de todos os dias do mês
    for day, costs_data in month_costs_data.items():
        total_costs = 0.0
        
        # Inicializar variáveis para custos individuais
        combustivel = 0.0
        manutencao = 0.0
        pedagio = 0.0
        reparo = 0.0
        outros = 0.0
        
        # Percorrer os dados de custo para o dia específico
        for cost_id, cost_items in costs_data.items():
            if isinstance(cost_items, dict):
                combustivel = float(cost_items.get('combustivel', '0.0'))
                manutencao = float(cost_items.get('manutencao', '0.0'))
                pedagio = float(cost_items.get('pedagio', '0.0'))
                reparo = float(cost_items.get('reparo', '0.0'))
                outros = float(cost_items.get('outros', '0.0'))
              
                # Somar ao total de custos do dia
                total_costs += combustivel + manutencao + pedagio + reparo + outros

               
        # Se houver transações agrupadas para esse dia, atualizar com os custos


        if day in grouped_transactions:

  
            grouped_transactions[day]['combustivel'] = combustivel
            grouped_transactions[day]['manutencao'] = manutencao
            grouped_transactions[day]['pedagio'] = pedagio
            grouped_transactions[day]['reparo'] = reparo
            grouped_transactions[day]['outros'] = outros
            grouped_transactions[day]['total_costs'] = total_costs
            grouped_transactions[day]['balance'] = grouped_transactions[day]['total_amount'] - total_costs  # Calcula o saldo restante
            grouped_transactions[day]['tecnico'] = (grouped_transactions[day]['balance'] /100) * participation
            grouped_transactions[day]['tecnico_total'] = grouped_transactions[day]['tecnico']
            grouped_transactions[day]['empresa'] = ((grouped_transactions[day]['balance'] /100) * participation_empresa)


    # Renderizar as transações agrupadas por dia, incluindo os custos e o saldo restante
    return render_template('extrato_tecnico.html', grouped_transactions=grouped_transactions, ano=ano, mes=mes)


@app.route('/fechar_dia_tecnico', methods=['POST'])
def fechar_dia_tecnico():

    date = request.form.get('date')

    data = {
    'manutencao': convert_monetary_value(request.form.get('manutencao') if request.form.get('manutencao') != "" else "0.00"),
    'combustivel': convert_monetary_value(request.form.get('combustivel') if request.form.get('combustivel') != "" else "0.00"),
    'pedagio': convert_monetary_value(request.form.get('pedagio') if request.form.get('pedagio') != "" else "0.00"),
    'reparo': convert_monetary_value(request.form.get('reparo') if request.form.get('reparo') != "" else "0.00"),
    'outros': convert_monetary_value(request.form.get('outros') if request.form.get('outros') != "" else "0.00"),
}

    
    User_Wallet.create_costs(id=session['user'], date=date, data=data)



    return redirect(url_for('dashboard_tecnico'))

@app.route('/adm_relatorios', methods=['GET', 'POST'])
@check_roles(['admin'])
def adm_relatorios():

    return render_template('adm_relatorios.html')


@app.route('/adm_consulta_extrato', methods=['GET', 'POST'])
@check_roles(['admin'])
def adm_consulta_extrato():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('adm_consulta_extrato.html')

@app.route('/adm_extrato_tecnico', methods=['GET', 'POST'])
@check_roles(['admin'])
def adm_extrato_tecnico():
    date_str = request.args.get('date')

    # Converter a data fornecida para ano, mês e dia
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return "Formato de data inválido."
    
    year = str(date.year)
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"

    # Obter todos os dados de wallet do Firebase
    wallet_data = db.child("wallet").get().val() or {}

    # Dicionário para agrupar transações, somar os amounts e os custos por técnico
    tecnico_transactions = defaultdict(lambda: {'transactions': [], 'total_amount': 0.0, 'costs': {'combustivel': 0.0, 'manutencao': 0.0, 'pedagio': 0.0, 'reparo': 0.0, 'outros': 0.0}, 'valor_final': 0.0})

    # Iterar sobre as cidades na estrutura do Firebase
    for city, years in wallet_data.items():
        if year in years:
            months = years[year]
            if month in months:
                days = months[month]
                if day in days:
                    # Obter as transações do dia específico
                    transactions = days[day].get("transactions", {}).get("success", {})

                    # Agrupar transações pelo nome do técnico e somar os amounts
                    for transaction_id, transaction_info in transactions.items():
                        tecnico_id = transaction_info.get('tecnico_id')
                        if tecnico_id:
                            name_tecnico = User.get_name(tecnico_id)  # Obter o nome do técnico
                        
                            # Buscar os custos do técnico (apenas uma vez por técnico)
                            if 'costs_retrieved' not in tecnico_transactions[name_tecnico]:
                                costs_path = f"users/{tecnico_id}/wallet/costs/{year}/{month}/{day}"
                                day_costs_data = db.child(costs_path).get().val() or {}
                                participation = User_Wallet.get_participation(id=tecnico_id)
                                participation_empresa = 100 - participation

                                # Somar os custos se eles existirem
                                for cost_id, cost_info in day_costs_data.items():
                                    
                                    tecnico_transactions[name_tecnico]['costs']['combustivel'] += float(cost_info.get('combustivel', 0))
                                    tecnico_transactions[name_tecnico]['costs']['manutencao'] += float(cost_info.get('manutencao', 0))
                                    tecnico_transactions[name_tecnico]['costs']['pedagio'] += float(cost_info.get('pedagio', 0))
                                    tecnico_transactions[name_tecnico]['costs']['reparo'] += float(cost_info.get('reparo', 0))
                                    tecnico_transactions[name_tecnico]['costs']['outros'] += float(cost_info.get('outros', 0))
                                    
                                    
                                # Marcar que os custos foram buscados
                                tecnico_transactions[name_tecnico]['costs_retrieved'] = True
                        
                            # Somar o valor da transação ao total do técnico
                            amount = float(transaction_info.get('amount', 0))
                            tecnico_transactions[name_tecnico]['transactions'].append(transaction_info)
                            tecnico_transactions[name_tecnico]['total_amount'] += amount
                        transaction_info['city'] = city

    # Calcular o valor final para cada técnico (total_amount - custos)
    for name_tecnico, data in tecnico_transactions.items():
        total_costs = data['costs']['combustivel'] + data['costs']['manutencao'] + data['costs']['pedagio'] + data['costs']['reparo'] + data['costs']['outros']
        data['valor_final'] = data['total_amount'] - total_costs
        data['tecnico'] = (data['valor_final'] /100) * participation
        data['empresa'] = (data['valor_final'] /100) * participation_empresa

    # Renderizar o template com os dados agrupados e a soma total
    return render_template('adm_extrato_tecnico.html', tecnico_transactions=tecnico_transactions, date=date_str, year=year, month=month, day=day)

@app.route('/os/<city>/<year>/<month>/<day>/<id>', methods=['GET', 'POST'])
@check_roles(['admin', 'tecnico'])
def os(city, year, month, day, id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    get_os = db.child("ordens_servico").child(city).child(year).child(month).child(day).child(id).get().val()


    return render_template('os.html', os=get_os)

@app.route('/users', methods=['GET', 'POST'])
@check_roles(['admin'])
def users():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    users_data = User.get_users()

    users_list = []
    for user_id, user_info in users_data.items():
        name = user_info.get('name')
        email = user_info.get('email')
        role = user_info.get('role')
        users_list.append({'name': name, 'email': email, 'role': role})

    return render_template('users.html', users=users_list)

@app.route('/deletar_os', methods=['GET', 'POST'])
@check_roles(['user'])
def deletar_os():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Obtendo os dados do formulário
    city = request.form.get('city')
    old_id = request.form.get("idRecord")
    motivo = request.form.get("deleteOsMotivo")
    date = request.form.get("deletaOsdate")
    tecnico_id = request.form.get('tecnico')

    # Verificando o formato da data
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return "Formato de data inválido."
    
    year = str(date.year)
    month = f"{date.month:02d}"
    day = f"{date.day:02d}"

    # Obtendo dados da OS do Firebase
    data = db.child("ordens_servico").child(city).child(year).child(month).child(day).child(old_id).get().val()

    if not data:
        return "Dados da OS não encontrados."

    # Obter a data e hora atual com o fuso horário de São Paulo
    fuso_horario_sp = pytz.timezone('America/Sao_Paulo')
    data_atual_sp = datetime.now(fuso_horario_sp)
    date_str = data_atual_sp.strftime('%Y-%m-%d')

    # Verificando o formato da data atual
    try:
        date_canceled = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return "Formato de data inválido."
    
    ano = str(date_canceled.year)
    mes = f"{date_canceled.month:02d}"
    dia = f"{date_canceled.day:02d}"

    # Atualizando o dicionário com o motivo do cancelamento
    data['motivo_cancelamento'] = motivo

    # Salvando os dados atualizados em canceled_services no Firebase
    db.child("canceled_services").child(city).child(ano).child(mes).child(dia).push(data)

    db.child("ordens_servico").child(city).child(year).child(month).child(day).child(old_id).remove()

    return redirect(url_for('dashboard'))

@app.route('/adm_lista_paymments_pendentes', methods=['GET', 'POST'])
@check_roles(['admin'])
def adm_lista_paymments_pendentes():
    if 'user' not in session:
        return redirect(url_for('login'))

    now = datetime.now()
    ano_atual = now.strftime("%Y")
    mes_atual = now.strftime("%m")

    # Receber ano e mês do formulário ou usar os valores padrão (ano e mês atuais)
    if request.method == 'POST':
        ano = request.form.get('ano', ano_atual)
        mes = request.form.get('mes', mes_atual)
    else:
        ano = ano_atual  # Ano atual
        mes = mes_atual  # Mês atual

    all_pendding_transactions = []

    cities = Cities.get_cities()

    # Buscar ordens de serviço pendentes para cada cidade
    for city in cities.values():
        pendding_transactions_path = f"wallet/{city}/{ano}/{mes}"
        paymments_pendding = db.child(pendding_transactions_path).get().val() or {}

        # Iterar sobre cada dia
        for day_data in paymments_pendding.values():
            # Verificar se há transações pendentes no dia
            if 'transactions' in day_data and 'pendding' in day_data['transactions']:
                for transaction_id, transaction_data in day_data['transactions']['pendding'].items():
                    # Adicionar o ID da transação ao dicionário
                    name = User.get_name(id=transaction_data['tecnico_id'])
                    transaction_data['transaction_id'] = transaction_id
                    transaction_data['name_tecnico'] = name
                    all_pendding_transactions.append(transaction_data)

    # Renderizar as transações pendentes
    return render_template('adm_lista_pendentes.html', transactions=all_pendding_transactions, ano=ano, mes=mes)

@app.route('/update_pendding', methods=['POST', 'GET'])
def update_pendding():

    os_id = request.form.get('paymmentIdOs')
    os_city = request.form.get('paymmentCity')
    os_date = request.form.get('osDate')
    transaction_id = request.form.get('transactionId')
   
    date_paymment = request.form.get('datePaymment')

    # Tenta converter a nova data para ano, mês e dia
    try:
        date_firebase = datetime.strptime(os_date, '%Y-%m-%d')
    except ValueError:
        return "Formato de data inválido."

    year = str(date_firebase.year)
    month = f"{date_firebase.month:02d}"
    day = f"{date_firebase.day:02d}"

    paymment_pendding = dict(db.child("wallet").child(os_city).child(year).child(month).child(day).child('transactions').child('pendding').child(transaction_id).get().val())
   
    status_pagamento = "recebido"    
    
    try:

        Wallet.create_paymment_success(data=paymment_pendding, date=date_paymment, city=os_city)

        Wallet.update_status_os(id=os_id, city=os_city, date=os_date, status_paymment=status_pagamento)

        User_Wallet.create_transaction_success(data=paymment_pendding, date=date_paymment, city=os_city, id_tecnico=paymment_pendding['tecnico_id'])

        db.child("wallet").child(os_city).child(year).child(month).child(day).child('transactions').child('pendding').child(transaction_id).remove()
        

    except:
        return jsonify({'status': 'conflict', 'message': 'Erro.'}), 400
    return redirect(url_for('adm_lista_paymments_pendentes'))

if __name__ == '__main__':
    app.run(debug=True, port=5036)