from flask  import Flask,render_template,request,redirect,url_for,session,escape
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
# configurando conexion a la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'P@ssw0rd'
app.config['MYSQL_DB'] = 'transito'

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
            session['username'] = user[1]
            return redirect(url_for('home'))
        return "Tus credenciales estan incorrectas"

@app.route("/logout")
def logout():
    session.pop("username",None)
    return "desconectado"



@app.route("/home")
def home():
    if "username" in session:
        return "You are %s" % escape(session["username"])
    return "you must log in first"

app.secret_key = "12345"
if __name__ == '__main__':
    app.run(debug=True)