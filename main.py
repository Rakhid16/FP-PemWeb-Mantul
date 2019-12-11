import re
from joblib import load
import MySQLdb.cursors
from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from os.path import dirname, join
from numpy import expand_dims, argmax
from keras.models import load_model
from keras.preprocessing import image
from keras import backend as K
import pandas as pd

app = Flask(__name__)

# BUAT JAGA-JAGA AJA
app.secret_key = 'TERSERAH'

# KONEKSIKEN KE DATABASE
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_DB'] = 'neurahealth_users'

mysql = MySQL(app)
bantu = "SAKIT"
############################### SUDAH MASUK KE LAMAN-LAMAN WEBSITE ###############################

def load_image(img_path, show=False):
    img = image.load_img(img_path, target_size=(224, 224))
    img_tensor = image.img_to_array(img)
    img_tensor = expand_dims(img_tensor, axis=0)         
    img_tensor /= 255.

    if show:
        plt.imshow(img_tensor[0])                           
        plt.axis('off')
        plt.show()

    return img_tensor

# UNTUK MENAMPILKAN LAMAN UTAMA
@app.route('/', methods=['GET'])
def main_page():
    return render_template('Halaman_Utama.html')

# UNTUK MENAMPILKAN LAMAN ABOUT
@app.route('/about', methods=['GET'])
def about():
    return render_template('Tentang_Kami.html')

# RUTE UNTUK LAMAN LOGIN
@app.route('/login/', methods=['GET', 'POST'])
def login():
    msg = ''   # VARIABEL UNTUK MENAMPUNG PESAN
    
    # CEK APAKAH USERNAME & PASSWORD SESUAI & ADA PADA DATABASE KITA
    if request.method == 'POST' and 'email' in request.form and 'pass_word' in request.form:
        email = request.form['email']
        pass_word = request.form['pass_word']
        
        # PENELUSURAN PADA DATABASE
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = %s AND pass_word = %s', (email, pass_word))
        account = cursor.fetchone()   # AMBIL SATU BARIS DATA
        
        # JIKA USERNAME & PASSWORD BENAR + DATANYA ADA PADA DATABASE KITA
        if account:
            # AGAR VARIABEL DI BAWAH INI DAPAT DIAKSES LEWAT RUTE LAIN
            session['loggedin'] = True
            session['doctor_id'] = account['doctor_id']
            session['doctor_name'] = account['doctor_name']
            
            # LANGSUNG MASUK KE LAMAN home ATAU dashboard
            return redirect(url_for('home'))
        
        # JIKA USERNAME/PASSWORD SALAH DAN/ATAU DATANYA TIDAK ADA PADA DATABASE KITA
        else:
            msg = 'Email/password salah!'
    
    return render_template('Laman_Login.html', msg=msg)

# RUTE UNTUK LAMAN REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = '' # VARIABEL UNTUK MENAMPUNG PESAN

    # CEK APAKAH DATA YANG DIMASUKKAN SUDAH ADA PADA DATABASE
    if request.method == 'POST' and 'doctor_name' in request.form and 'pass_word' in request.form and 'email' in request.form and 'hospital_name' in request.form and 'hospital_code' in request.form:
        doctor_name = request.form['doctor_name']
        pass_word = request.form['pass_word']
        email = request.form['email']
        hospital_name = request.form['hospital_name']
        hospital_code = request.form['hospital_code']

        # PENELUSURAN PADA DATABASE
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM accounts WHERE doctor_name = '{0}'".format(doctor_name))
        account = cursor.fetchone()   # AMBIL SATU DATA

        # TAMPILKAN PESAN ERROR APABILA AKUN SUDAH TERDAFTAR PADA DATABASE KITA
        if account:
            msg = 'Akun itu sudah ada!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Alamat email salah'
        elif not re.match(r'[A-Za-z0-9]+', doctor_name):
            msg = 'Cuma angka dan huruf saja!'
        elif not doctor_name or not pass_word or not email or not hospital_name or not hospital_code:
            msg = 'Masih ada data yang belum dimasukkan!'
        
        # JIKA AKUN TERSEBUT TIDAK ADA PADA DATABASE KITA
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s)', (doctor_name, pass_word, email, hospital_name, hospital_code)) # NULL KARENA KOLOM ID AUTOINCREMENT
            mysql.connection.commit()
            msg = 'Anda sudah terdaftar!'
    
    # JIKA KLIK REGISTER TAPI ADA DATA YANG MASIH BELUM TERISI
    elif request.method == 'POST':
        msg = 'Masih ada data yang belum dimasukkan!'

    return render_template('Laman_Register.html', msg=msg)

# RUTE UNTUK LAMAN BERANDA - SETELAH LOGIN
@app.route('/neurahealth')
def home():
    # CEK APAKAH USER SUDAH LOGIN
    if 'loggedin' in session:
        return render_template('Beranda.html', doctor_name=session['doctor_name'])
    
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

# RUTE UNTUK LAMAN PROFIL - HARUS LOGIN DULU
@app.route('/neurahealth/profile', methods=['GET', 'POST'])
def profile():
    # CEK APAKAH USER SUDAH LOGIN
    if 'loggedin' in session:
        # AKSES DATABASE
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE doctor_id = %s', [session['doctor_id']])
        account = cursor.fetchone()   # AMBIL SATU DATA

        if request.method == 'POST':
            cursor.execute('UPDATE accounts set email = %s, pass_word = %s, hospital_name = %s WHERE doctor_name = %s', (request.form['email'], request.form['password'], request.form['hos_name'], session['doctor_name']))
            mysql.connection.commit()

        return render_template('Laman_Profil.html', account=account)
    
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

# RUTE UNTUK LAMAN DAFTAR PENYAKIT - HARUS LOGIN DULU
@app.route('/neurahealth/diseases', methods=['GET', 'POST'])
def diseases():
    if 'loggedin' in session:
        return render_template('Pilihan_Penyakit.html')
    
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

# RUTE UNTUK LAMAN LOGOUT
@app.route('/logout')
def logout():
    # HAPUS DATA YANG TERSIMPAN SELAMA SESI
    session.pop('loggedin', None)
    session.pop('doctor_id', None)
    session.pop('doctor_name', None)
    
    # BALIK KE LAMAN LOGIN
    return redirect(url_for('main_page'))

############################### KHUSUS PENYAKIT-PENYAKIT ###############################

# PENYAKIT DIABETES
@app.route('/neurahealth/diabetes')
def diabetes_home():
    if 'loggedin' in session:
        return render_template('Beranda_Diabetes.html', doctor_name=session['doctor_name'])

    return redirect(url_for('login'))

@app.route('/neurahealth/diabetes/diagnose', methods=['GET','POST'])
def diabetes_input():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        msg = ''
        if request.method == 'POST':
            AI_diabetes = load('models/diabetes.pkl')
            data1 = [[request.form['jum_kel'], request.form['ka_glu'], request.form['tek_dar'], request.form['ket_kul'], request.form['insulin'], request.form['bmi'], request.form['ri_kel'], request.form['umur']]]

            hasil = AI_diabetes.predict_proba(data1)
            iya = hasil[0][0]*100
            tidak = hasil[0][1]*100

            if iya > tidak:
                cursor.execute('INSERT INTO neurahealth_patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['name'], request.form['birthPlace'], request.form['birthDate'], request.form['noKtp'], request.form['address'], request.form['gender'], "Y", session['doctor_name'], "Diabetes")) # NULL KARENA KOLOM ID AUTOINCREMENT
                mysql.connection.commit()
                return render_template('hasil_diabetes.html', msg="Kena penyakit diabetes")
            else:
                cursor.execute('INSERT INTO neurahealth_patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['name'], request.form['birthPlace'], request.form['birthDate'], request.form['noKtp'], request.form['address'], request.form['gender'], "T", session['doctor_name'], "Diabetes")) # NULL KARENA KOLOM ID AUTOINCREMENT
                mysql.connection.commit()
                return render_template('hasil_diabetes.html', msg="Tidak kena penyakit diabetes")
            
    return render_template('inputan_diabetes.html')

@app.route('/neurahealth/diabetes/data')
def diabetes_data():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT name, birth_plc, birth_date, ktp, alamat, gender, result FROM neurahealth_patients WHERE byuser = %s and diseases = %s', [session['doctor_name'], "Diabetes"])
        rv = cursor.fetchall()

        #data_ekspor = pd.DataFrame()

        return render_template('Data_Pasien_Diabetes.html', value=rv)
    
    return redirect(url_for('login'))

# PENYAKIT JANTUNG
@app.route('/neurahealth/jantung')
def jantung_home():
    if 'loggedin' in session:
        return render_template('Beranda_Jantung.html', doctor_name=session['doctor_name'])

    return redirect(url_for('login'))

@app.route('/neurahealth/jantung/diagnose', methods=['GET','POST'])
def jantung_input():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            AI_jantung = load('models/jantung.pkl')
            data1 = [[request.form['je_ka'], request.form['cp'], request.form['blood_pres'], request.form['chol'], request.form['fbs'], request.form['heart_rate'], request.form['thal'], request.form['umur']]]

            hasil = AI_jantung.predict_proba(data1)
            iya = hasil[0][0]*100
            tidak = hasil[0][1]*100

            if iya > tidak:
                cursor.execute('INSERT INTO neurahealth_patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['name'], request.form['birthPlace'], request.form['birthDate'], request.form['noKtp'], request.form['address'], request.form['gender'], "Y", session['doctor_name'], "Jantung")) # NULL KARENA KOLOM ID AUTOINCREMENT
                mysql.connection.commit()
                return render_template('hasil_jantung.html', msg="Kena penyakit jantung")
            else:
                cursor.execute('INSERT INTO neurahealth_patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['name'], request.form['birthPlace'], request.form['birthDate'], request.form['noKtp'], request.form['address'], request.form['gender'], "T", session['doctor_name'], "Jantung")) # NULL KARENA KOLOM ID AUTOINCREMENT
                mysql.connection.commit()
                return render_template('hasil_jantung.html', msg="Tidak kena penyakit jantung")

    return render_template('inputan_jantung.html')

@app.route('/neurahealth/jantung/data')
def jantung_data():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT name, birth_plc, birth_date, ktp, alamat, gender, result FROM neurahealth_patients WHERE byuser = %s and diseases = %s', [session['doctor_name'], "Jantung"])
        rv = cursor.fetchall()

        return render_template('Data_Pasien_Jantung.html', value=rv)

    return redirect(url_for('login'))

############################################################################################## IMAGE ##############################################################################################

@app.route('/neurahealth/malaria')
def malaria_home():
    if 'loggedin' in session:
        return render_template('Beranda_Malaria.html')
    return redirect(url_for('login'))

@app.route('/neurahealth/malaria/diagnose', methods=['GET','POST'])
def malaria_input():
    if 'loggedin' in session:
        return render_template('index.html')

    return redirect(url_for('login'))

@app.route('/neurahealth/malaria/data', methods=['GET','POST'])
def malaria_data():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name, birth_plc, birth_date, ktp, alamat, gender, result FROM neurahealth_patients WHERE byuser = %s and diseases = %s", [session['doctor_name'], "Malaria"])
        rv = cursor.fetchall()

        return render_template("Data_Pasien_Malaria.html", value=rv)

    return redirect(url_for('login'))

# TUMOR OTAK
@app.route('/neurahealth/tumor')
def tumor_home():
    if 'loggedin' in session:
        return render_template('Beranda_Tumor.html')
    return redirect(url_for('login'))

@app.route('/neurahealth/tumor/diagnose', methods=['GET','POST'])
def tumor_input():
    if 'loggedin' in session:
        return render_template('index1.html')
    return redirect(url_for('login'))

@app.route('/neurahealth/tumor/data', methods=['GET','POST'])
def tumor_data():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name, birth_plc, birth_date, ktp, alamat, gender, result FROM neurahealth_patients WHERE byuser = %s and diseases = %s", [session['doctor_name'], "Tumor"])
        rv = cursor.fetchall()
        return render_template('Data_Pasien_Tumor.html', value=rv)

    return redirect(url_for('login'))

# PARKINSON
@app.route('/neurahealth/parkinson')
def parkinson_home():
    if 'loggedin' in session:
        return render_template('Beranda_Parkinson.html', doctor_name=session['doctor_name'])
    
    return redirect(url_for('login'))

@app.route('/neurahealth/parkinson/diagnose', methods=['GET','POST'])
def parkinson_input():
    if 'loggedin' in session:
        return render_template('index2.html')
    
    return redirect(url_for('login'))

@app.route('/neurahealth/parkinson/data', methods=['GET','POST'])
def parkinson_data():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name, birth_plc, birth_date, ktp, alamat, gender, result FROM neurahealth_patients WHERE byuser = %s and diseases = %s", [session['doctor_name'], "Parkinson"])
        rv = cursor.fetchall()
        return render_template('Data_Pasien_Parkinson.html', value=rv)
    
    return redirect(url_for('login'))

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    global bantu

    if request.method == 'POST':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        model = load_model("models/GAMBAR_KABEH.h5")
        model._make_predict_function()
        
        f = request.files['image']
        
        basepath = dirname(__file__)
        file_path = join(basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        new_image = load_image(file_path)
        
        pred = model.predict(new_image)
        K.clear_session()

        if argmax(pred) == 0:
            bantu = "Y"
            cursor.execute('INSERT INTO neurahealth_patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['name'], request.form['birthPlace'], request.form['birthDate'], request.form['noKtp'], request.form['address'], request.form['gender'], bantu, session['doctor_name'], "Malaria")) # NULL KARENA KOLOM ID AUTOINCREMENT
            mysql.connection.commit()
            msg = "Data Sudah Tersimpan!"
            return str("Kena penyakit malaria")
        
        elif argmax(pred) == 1:
            bantu = "T"
            cursor.execute('INSERT INTO neurahealth_patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['name'], request.form['birthPlace'], request.form['birthDate'], request.form['noKtp'], request.form['address'], request.form['gender'], bantu, session['doctor_name'], "Malaria")) # NULL KARENA KOLOM ID AUTOINCREMENT
            mysql.connection.commit()
            msg = "Data Sudah Tersimpan!"
            return str("Ndak kena ada malaria")
        
        elif argmax(pred) == 2:
            bantu = "Y"
            cursor.execute('INSERT INTO neurahealth_patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['name'], request.form['birthPlace'], request.form['birthDate'], request.form['noKtp'], request.form['address'], request.form['gender'], bantu, session['doctor_name'], "Parkinson")) # NULL KARENA KOLOM ID AUTOINCREMENT
            mysql.connection.commit()
            msg = "Data Sudah Tersimpan!"
            return str("Kena penyakit parkinson")
        
        elif argmax(pred) == 3:
            bantu = "T"
            cursor.execute('INSERT INTO neurahealth_patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['name'], request.form['birthPlace'], request.form['birthDate'], request.form['noKtp'], request.form['address'], request.form['gender'], bantu, session['doctor_name'], "Parkinson")) # NULL KARENA KOLOM ID AUTOINCREMENT
            mysql.connection.commit()
            msg = "Data Sudah Tersimpan!"
            return str("Ndak kena penyakit parkinson")
        
        elif argmax(pred) == 4:
            bantu = "Y"
            cursor.execute('INSERT INTO neurahealth_patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['name'], request.form['birthPlace'], request.form['birthDate'], request.form['noKtp'], request.form['address'], request.form['gender'], bantu, session['doctor_name'], "Tumor")) # NULL KARENA KOLOM ID AUTOINCREMENT
            mysql.connection.commit()
            msg = "Data Sudah Tersimpan!"
            return str("Kena penyakit Tumor")
        
        else:
            bantu = "T"
            cursor.execute('INSERT INTO neurahealth_patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (request.form['name'], request.form['birthPlace'], request.form['birthDate'], request.form['noKtp'], request.form['address'], request.form['gender'], bantu, session['doctor_name'], "Tumor")) # NULL KARENA KOLOM ID AUTOINCREMENT
            mysql.connection.commit()
            msg = "Data Sudah Tersimpan!"
            return str("Ndak kena penyakit Tumor")

    return None