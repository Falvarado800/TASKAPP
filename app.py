# librerias de flask
from flask import Flask, render_template, request, session, redirect, url_for 
# libreria flask mysql
from flask_mysqldb import MySQL
# importando archivo config para obtener los datos de conexion a mysql
import config
# importando datetime
from datetime import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = config.HEC_SEC_KEY
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB


mysql = MySQL(app)

@app.route('/', methods=['GET'])
def home():
   
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['pass']
    # Conexion con base de datos 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario where email = %s AND password = %s", (email, password))
    user = cur.fetchone()  # Utiliza fetchone() para obtener una coincidencia
    cur.close()
    if user is not None:  # Comprueba si se encontró un usuario
        session['email'] = email
        session['nombre'] = user[1]
        session['apellido'] = user[2]
        session['tipo'] = user[4]

        return redirect(url_for('tasks'))
    else:
        return render_template('index.html', message=' Las credenciales no son correctas ')
    
@app.route('/tasks', methods=['GET'])
def tasks():
    email =  session['email'] 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tarea WHERE email = %s", [email])
    tasks = cur.fetchall()
# recoge la informacion y lo conviert en un diccionario 
    insertObjects = []
    columnNames = [column[0] for column in cur.description]
    for record in tasks:
        insertObjects.append(dict(zip(columnNames, record)))
    cur.close()
    
    
    return render_template('tasks.html', tasks  = insertObjects)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/new-task', methods=['GET', 'POST'])
def newtask():
    titulo= request.form['titulo']
    descripcion= request.form['descripcion']
    email = session['email']
    d = datetime.now()
    date = d.strftime("%y-%m-%d")

    if titulo and descripcion and email:
       cur = mysql.connection.cursor()
       sql = "INSERT INTO tarea (email, titulo, descripcion, date) VALUES (%s, %s, %s, %s)"
       data  = (email, titulo, descripcion, date)
       cur.execute(sql, data)
       mysql.connection.commit()
       return redirect(url_for('tasks'))
   
    
@app.route('/new-user', methods=['GET', 'POST'])
def newuser():
    nombre= request.form['nombre']
    apellido= request.form['apellido']
    email = request.form['email']
    tipo= request.form['tipo']
    password= request.form['password']

    if tipo == 'administrador':
            tipo = 1
    elif tipo == 'basico':
            tipo = 0

    if  session['tipo'] == 1:
        cur = mysql.connection.cursor()
        sql = "INSERT INTO usuario (nombre, apellido, email, tipo, password) VALUES (%s, %s, %s, %s, %s)"
        data  = (nombre, apellido, email, tipo, password)
        cur.execute(sql, data)
        mysql.connection.commit()
        return redirect(url_for('tasks'))
    else:
        return render_template('tasks.html', message='Usuario no autorizado para esta accion.')
    
@app.route('/delete-task', methods=['GET', 'POST'])
def deleteTask():
     cur = mysql.connection.cursor()
     id = request.form['id']
     sql = "delete from tarea where id = %s"
     data = (id,)
     cur.execute(sql, data)
     mysql.connection.commit()
     return redirect(url_for('tasks'))


     
    
       
       


if __name__ == '__main__':
    app.run(debug=True)