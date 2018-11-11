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
app.config['MYSQL_PASSWORD'] = 'P@ssw0rd'
app.config['MYSQL_DB'] = 'transito'
# clave secreta para sesiones
app.secret_key = "12345"

mysql = MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

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
                cur.execute('INSERT INTO users (nombre,hash,f_nac) VALUES (%s,%s,%s)',(nombre,hash,date))
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
        query = "SELECT * FROM users WHERE nombre = '{0}'".format(nombre)
        cur.execute(query)
        user = cur.fetchall()
        user = user[0]
        password = request.form['password']
        print(user)
        if user and check_password_hash(user[2],password):
            session['user_id'] = user[0]
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
    #olvidar cualquier usuario
    session.clear()
    return redirect(url_for('login'))



@app.route("/home")
@login_required
def home():
    id = escape(session["user_id"])
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = '{0}'".format(id))
    user = cur.fetchall()
    nombre = user[0][1]
    return render_template("home.html",nombre = nombre,dado=dado[0],dados=diccionario["dados"][int(id)-1])


@app.route("/lanzarDado")
def lanzarDado():
    id = escape(session["user_id"])
    dado[0] = randint(1, 6)

    if len(diccionario["dados"][int(id)-1]) != 6:
        if  dado[0] not in diccionario["dados"][int(id)-1]:
            diccionario["dados"][int(id)-1].append(dado[0])
            diccionario["puntajeRonda"][int(id)-1] += dado[0]
        else:
            print('Dado repetido tu puntaje baja a cero')
            diccionario["cantidadRepetidos"][int(id)-1] +=1
            if diccionario["cantidadRepetidos"][int(id)-1] == 3:
                print("PERDISTE CHOQUITO")
            diccionario["puntajeRonda"][int(id)-1] = 0
            diccionario["dados"][int(id)-1] = []
    else:
        diccionario["puntajeRonda"][int(id)-1] = 100
        print("GANASTE CHOQUITO")

    print(diccionario)
    print(diccionario["dados"][int(id)-1])#
    return redirect(url_for('home'))

@app.route("/anotar")
def anotar():
    id = escape(session["user_id"])
    diccionario["puntajePartida"][int(id)-1] +=diccionario["puntajeRonda"][int(id)-1]
    diccionario["puntajeRonda"][int(id)-1] = 0
    diccionario["dados"][int(id)-1] = []
    print(diccionario)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)