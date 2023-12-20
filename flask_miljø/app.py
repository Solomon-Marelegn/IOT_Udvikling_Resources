from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pymysql
from datetime import timedelta
from ssh_conn import exec_cmd_on_vm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iot_project_eaaa_2023_Group_4'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=15)

def connect(database):
    try:
        conn = pymysql.connect(
            user='user1',
            password = 'test',
            host = '192.168.2.21',
            port=3306,
            database = database)
        print("connected to database")
        return conn
        
    except pymysql.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return None    
    
def generate_chart(data_dict, chart_type):
    labels = list(data_dict.keys())
    data = list(data_dict.values())
    colors = ['#4CAF50', '#FFC107', '#F44336']
    _, ax = plt.subplots()

    if chart_type == 'pie':
        wedges, _ = ax.pie(data, labels=None, colors=colors, startangle=90)
        legend_labels = [f'{label}: {data_dict[label]}' for label in labels]
        ax.legend(wedges, legend_labels, title='Labels', loc='upper left', bbox_to_anchor=(1, 1))
        ax.axis('equal')

    elif chart_type == 'bar':
        ax.bar(labels, data, color=colors)

    image_stream = BytesIO()
    plt.savefig(image_stream, format='png', bbox_inches='tight')
    image_stream.seek(0)
    plt.close()
    encoded_image = base64.b64encode(image_stream.read()).decode('utf-8')

    return f"data:image/png;base64, {encoded_image}"

def get_statistic(conn, location = None):
    cur = conn.cursor()
    
    data = {'pleased': 0, 'neutral': 0, 'displeased': 0}
    for label in data.keys():
        if location:
            query = f"""SELECT COUNT(*) FROM ratings where feedback = '{label}' and location = '{location}';"""
        else:
            query = f"SELECT COUNT(*) FROM ratings where feedback = '{label}';"

        cur.execute(query)
        amount = cur.fetchone()[0]
        data[label] = amount
    return data


def get_raw_data(conn, amount, location = None):
    cur = conn.cursor()
    
    if location:
        query = f"""SELECT feedback, time, date, location from ratings 
        WHERE location = '{location}' order by date desc,  
            time desc limit {amount};"""
    else:
        query = f"""SELECT feedback, 
            time, date, location from ratings order by date desc,  
            time desc limit {amount};"""
        
    cur.execute(query)
    data = cur.fetchall()
    result = []
    for tup in data:
        temp_dict = {"feedback": tup[0],"time": tup[1],
                     "date": tup[2], "region": tup[3], }
        result.append(temp_dict)
    return result

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/total')
def total():
    conn = connect('customer_satisfaction')
    data = get_statistic(conn)
    latest_data = get_raw_data(conn, 5)

    if sum(data.values()) == 0:
        pie_chart_data = "No data available"
        bar_chart_data = "No data available"
    else:
        pie_chart_data = generate_chart(data, 'pie')
        bar_chart_data = generate_chart(data, 'bar')
    
    conn.commit()
    conn.close()

    return render_template('total.html', 
                           pie_chart_data=pie_chart_data, 
                           bar_chart_data=bar_chart_data, 
                           data=data, 
                           latest_data=latest_data)

@app.route('/per_region')
def per_region():
    conn = connect('customer_satisfaction')
    locations = ['Aarhus', 'København']
    data_1 = get_statistic(conn, locations[0])
    data_2 = get_statistic(conn, locations[1])
    latest_data_1 = get_raw_data(conn, 5, locations[0])
    latest_data_2 = get_raw_data(conn, 5, locations[1])
    

    if sum(data_1.values()) == 0:
        pie_chart_data_1 = "No data available"
        bar_chart_data_1 = "No data available"
    else:
        pie_chart_data_1 = generate_chart(data_1,'pie')
        bar_chart_data_1 = generate_chart(data_1, 'bar')
        


    if sum(data_2.values()) == 0:
        pie_chart_data_2 = "No data available"
        bar_chart_data_2 = "No data available"
    else:
        pie_chart_data_2 = generate_chart(data_2, 'pie')
        bar_chart_data_2 = generate_chart(data_2, 'bar')
    
    conn.commit()
    conn.close()

    return render_template('per_region.html', 
                           pie_chart_data_1=pie_chart_data_1, 
                           bar_chart_data_1=bar_chart_data_1,
                           pie_chart_data_2 = pie_chart_data_2,
                           bar_chart_data_2 = bar_chart_data_2,
                           data_1 = data_1,
                           data_2 = data_2,
                           latest_data_1 = latest_data_1,
                           latest_data_2 = latest_data_2)

@app.route('/raw_data', methods=['GET', 'POST'])
def raw_data():
    conn = connect('customer_satisfaction')
    row_count = 1000
    if request.method == 'POST':
        row_count = int(request.form.get('row_count', 1000))

    data = get_raw_data(conn, row_count)

    conn.commit()
    conn.close()
    return render_template('raw_data.html', data=data, row_count=row_count)

def check_credentials(username, password):
    conn = connect('users')
    cursor = conn.cursor()
    query = f"SELECT * FROM users.admins WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)

    result = cursor.fetchone()
    

    conn.commit()
    conn.close()
    return result

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'username' in session:
        return render_template('admin.html', device_status=get_device_status())

    elif request.method == 'POST':
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']

        if check_credentials(admin_username, admin_password):
            session['username'] = admin_username
            return render_template('admin.html', device_status=get_device_status())

    else:
        return render_template('login.html')

def get_device_status():
    global device_status
    device_status = {
        'Mqtt_Broker': exec_cmd_on_vm('Mqtt_Broker'),
        'Mqtt_Sub': exec_cmd_on_vm('Mqtt_Sub'),
        'Database': exec_cmd_on_vm('Database'),
    }
    return device_status


@app.route('/admin/refresh', methods=['POST'])
def refresh_page():
    session['username'] = session.get('username', None)
    return redirect(url_for('admin'))

@app.route('/admin/toggle', methods=['POST'])
def toggle_device():
    device = request.form.get('device')
    current_status = device_status[device]

    if current_status == 'Off':
        exec_cmd_on_vm(f'start_{device}')
    else:
        exec_cmd_on_vm(f'stop_{device}')
    
    new_status = exec_cmd_on_vm(device)
    device_status[device] = new_status
    
    return render_template('admin.html', device_status=device_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)