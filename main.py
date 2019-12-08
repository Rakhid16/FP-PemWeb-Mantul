import re
from joblib import load
import MySQLdb.cursors
from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for, session

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

############################### SUDAH MASUK KE LAMAN-LAMAN WEBSITE ###############################

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
@app.route('/neurahealth/profile')
def profile():
    # CEK APAKAH USER SUDAH LOGIN
    if 'loggedin' in session:
        # AKSES DATABASE
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE doctor_id = %s', [session['doctor_id']])
        account = cursor.fetchone()   # AMBIL SATU DATA
        
        return render_template('Laman_Profil.html', account=account)
    
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

# RUTE UNTUK LAMAN DAFTAR PENYAKIT - HARUS LOGIN DULU
@app.route('/neurahealth/diseases', methods=['GET', 'POST'])
def diseases():
    # CEK APAKAH USER SUDAH LOGIN
    if 'loggedin' in session:

        if request.method == 'POST':
            return redirect(url_for('malaria_home'))
        elif request.method == 'POST' and request.form['msk'] == 2:
            return redirect(url_for('jantung_home'))
        elif request.method == 'POST' and request.form['msk'] == 3:
            return redirect(url_for('tumor_home'))
        elif request.method == 'POST' and request.form['msk'] == 4:
            return redirect(url_for('diabetes_home'))
        elif request.method == 'POST' and request.form['msk'] == 5:
            return redirect(url_for('parkinson_home'))

        return render_template('Pilihan_Penyakit.html', doctor_name=session['doctor_name'])
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
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

@app.route('/neurahealth/diabetes/diagnose', methods=['GET','POST'])
def diabetes_input():
    AI_diabetes = load('models/diabetes.pkl')
    data1 = [[request.form['n_hamil'], request.form['glukosa'], request.form['tekanan_darah'], request.form['ketebalan_kulit'], request.form['kadar_insulin'], request.form['bmi'], request.form['riwayat'], request.form['umur']]]
    
    hasil = AI_diabetes.predict_proba(data1)
    iya = hasil[0][0]*100
    tidak = hasil[0][1]*100
    
    hasil = "Pasien terdiagnosa " + str(tidak) +"% terkena penyakit diabetes dan " + str(iya) + "% tidak terkena penyakit diabetes"
    return(hasil)

@app.route('/neurahealth/diabetes/data')
def diabetes_data():
    if 'loggedin' in session:
        return render_template('Data_Pasien_Diabetes.html', doctor_name=session['doctor_name'])
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

# PENYAKIT JANTUNG
@app.route('/neurahealth/jantung')
def jantung_home():
    if 'loggedin' in session:
        return render_template('Beranda_Jantung.html', doctor_name=session['doctor_name'])
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

@app.route('/neurahealth/jantung/diagnose', methods=['GET','POST'])
def jantung_input():
    AI_jantung = load('models/jantung.pkl')
    data2 = [[request.form['umur'], request.form['je_ka'], request.form['cp'], request.form['blood_pres'], request.form['chol'], request.form['fbs'], request.form['res_electro'], request.form['heart_rate'], request.form['angia'], request.form['oldpeak'], request.form['slope'], request.form['n_vena'], request.form['thal']]]
    
    hasil1 = AI_jantung.predict_proba(data2)
    iya1 = hasil[0][0]*100
    tidak1 = hasil[0][1]*100
    return(tidak1)
    hasil1 = "Pasien terdiagnosa " + str(tidak1) +"% terkena penyakit jantung dan " + str(iya1) + "% tidak terkena penyakit jantung"
    
    return(hasil1)

@app.route('/neurahealth/jantung/data')
def jantung_data():
    if 'loggedin' in session:
        return render_template('Data_Pasien_Jantung.html', doctor_name=session['doctor_name'])
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

# MALARIA
@app.route('/neurahealth/malaria', methods=['GET','POST'])
def malaria_home():
    return render_template('Beranda_Malaria.html')

@app.route('/neurahealth/malaria/diagnose')
def malaria_input():
    # CEK APAKAH USER SUDAH LOGIN
    if 'loggedin' in session:
        return render_template('inputan_malaria.html', doctor_name=session['doctor_name'])
    
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

@app.route('/neurahealth/malaria/data', methods=['GET','POST'])
def malaria_data():
    return render_template('Data_Pasien_Malaria.html')

# TUMOR OTAK
@app.route('/neurahealth/tumor', methods=['GET','POST'])
def tumor_home():
    return render_template('Beranda_Tumor.html')

@app.route('/neurahealth/tumor/diagnose')
def tumor_input():
    # CEK APAKAH USER SUDAH LOGIN
    if 'loggedin' in session:
        return render_template('inputan_tumor_otak.html', doctor_name=session['doctor_name'])
    
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

@app.route('/neurahealth/tumor/data', methods=['GET','POST'])
def tumor_data():
    return render_template('Data_Pasien_Tumor.html')

# PARKINSON
@app.route('/neurahealth/parkinson')
def parkinson_home():
    # CEK APAKAH USER SUDAH LOGIN
    if 'loggedin' in session:
        return render_template('Beranda_Parkinson.html', doctor_name=session['doctor_name'])
    
    # JIKA BELUM LOGIN MAKA BALIK KE LAMAN LOGIN
    return redirect(url_for('login'))

@app.route('/neurahealth/parkinson/diagnose', methods=['GET','POST'])
def parkinson_input():
    return render_template('Data_Pasien_Parkinson.html')

@app.route('/neurahealth/parkinson/data', methods=['GET','POST'])
def parkinson_data():
    return render_template('Data_Pasien_Parkinson.html')