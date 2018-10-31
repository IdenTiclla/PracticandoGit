from flask  import Flask,render_template,request,redirect,url_for
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


if __name__ == '__main__':
    app.run(debug=True)