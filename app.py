from flask  import Flask,render_template,request,redirect,url_for,session,escape
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash,check_password_hash
from helpers import *
from random import randint

diccionario = {"id":[],"dados":[],"cantidadRepetidos":[],"puntajeRonda":[],"puntajePartida":[]}
dado = [0]

# instanciando nuestra aplicacion
app = Flask(__name__)
# configurando conexion a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'game'
# clave secreta para sesiones
app.secret_key = "12345"

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/help')
def help():
   return render_template("help.html")
@app.route('/score_table')
def score_table():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM users"
    cur.execute(query)
    users = cur.fetchall()
    print(users)
    for user in users:
        print(user[1])
    return render_template("score_table.html",users=users)
    
@app.route("/signUp",methods=['GET','POST'])
def signUp():
    if  request.method == 'GET':
        return render_template("signUp.html")
    else:
        nombre = request.form['nombre']
        password = request.form['password']
        password_again = request.form['password_again']
        date = request.form['fecha_nac']
        checkbox = request.form.getlist('checkbox')

        hash = generate_password_hash(password,method='sha256')
        if not nombre or not password or not password_again or not date or not checkbox:
            return "Debes ingresar los datos"
        else:
            if password == password_again:
                cur = mysql.connection.cursor()
                cur.execute(f"INSERT INTO users (nombre,hash,f_nac) VALUES ('{nombre}','{hash}','{date}')")
                mysql.connection.commit()
                return redirect(url_for('signUp'))
            else:
                return "Debes repetir la misma contrasenia"

@app.route("/login",methods=["GET","POST"])
def login():
    # olvidar cualquier sesion activa
    session.clear()
    if request.method =="GET":
        return render_template("login.html")
    else:
        nombre = request.form['nombre']
        # buscar en la base de datos ese usuario con ese nombre
        cur = mysql.connection.cursor()
        query = f"SELECT * FROM users WHERE nombre = '{nombre}'"
        cur.execute(query)
        user = cur.fetchall()
        user = user[0]
        password = request.form['password']
        print(user)
        if user and check_password_hash(user[2],password):
            session['user_id'] = user[0]
            print("ENTRAMOS CABORRRRRON")
            if  int(session["user_id"]) not in diccionario["id"]:
                diccionario["id"].append(int(session["user_id"]))
                diccionario["dados"].append([])
                diccionario["cantidadRepetidos"].append(0)
                diccionario["puntajeRonda"].append(0)
                diccionario["puntajePartida"].append(0)
            return redirect(url_for('home'))
        return "Tus credenciales estan incorrectas"

@app.route("/logout")
@login_required
def logout():
    #forget any user
    session.clear()
    return redirect(url_for('login'))



@app.route("/home")
@login_required
def home():
    id = escape(session["user_id"])
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM users WHERE id = '{id}'")
    user = cur.fetchall()
    nombre = user[0][1]
    return render_template("home.html",nombre = nombre,dado=dado[0],dados=diccionario["dados"][int(id)-1])


@app.route("/lanzarDado")
def lanzarDado():
    id = escape(session["user_id"])
    dado[0] = randint(1, 6)
    # si el usuario no saco los 6 dados
    if len(diccionario["dados"][int(id)-1]) != 6:
        # si el dado no esta en los dados que saco
        if  dado[0] not in diccionario["dados"][int(id)-1]:
            diccionario["dados"][int(id)-1].append(dado[0])
            diccionario["puntajeRonda"][int(id)-1] += dado[0]
            
        else:
            print('Dado repetido tu puntaje baja a cero')
            diccionario["cantidadRepetidos"][int(id)-1] += 1
            # si la cantidad de dados repetidos es 3
            if diccionario["cantidadRepetidos"][int(id)-1] >= 3:
                return render_template('lose.html')
            diccionario["puntajeRonda"][int(id)-1] = 0
            diccionario["dados"][int(id)-1] = []
    else:
        diccionario["puntajeRonda"][int(id)-1] = 100
        #agregar puntaje a la db
        return render_template('win.html')

    print(diccionario)
    print(diccionario["dados"][int(id)-1])#
    return redirect(url_for('home'))

@app.route("/anotar")
def anotar():
    id = escape(session["user_id"])
    diccionario["puntajePartida"][int(id)-1] += diccionario["puntajeRonda"][int(id)-1]
    if diccionario["puntajePartida"][int(id)-1] >= 100:
                return render_template('win.html')
    diccionario["puntajeRonda"][int(id)-1] = 0
    diccionario["dados"][int(id)-1] = []
    print(diccionario)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)