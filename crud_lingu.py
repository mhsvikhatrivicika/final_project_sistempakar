from flask import Flask, render_template, request, redirect, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret_key"

# Koneksi ke database
db = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='sistem_pakar'
)

# Fungsi untuk mendapatkan semua data linguistik
def get_linguistic():
    cursor = db.cursor()
    cursor.execute("SELECT l.id_tml, v.name_tmv, l.label_tml FROM tbl_m_linguistic l INNER JOIN tbl_m_variabel v ON l.id_tmv = v.id_tmv")
    linguistic = cursor.fetchall()
    cursor.close()
    return linguistic

# Fungsi untuk menambahkan data linguistik baru
def add_linguistic(name_tmv, label_tml):
    cursor = db.cursor()
    cursor.execute("INSERT INTO tbl_m_linguistic (id_tmv, label_tml) SELECT id_tmv, %s FROM tbl_m_variabel WHERE name_tmv = %s", (label_tml, name_tmv))
    db.commit()
    cursor.close()

# Fungsi untuk menghapus data linguistik berdasarkan ID
def delete_linguistic(id_tml):
    cursor = db.cursor()
    cursor.execute("DELETE FROM tbl_m_linguistic WHERE id_tml = %s", (id_tml,))
    db.commit()
    cursor.close()

# Fungsi untuk mengedit data linguistik berdasarkan ID
def edit_linguistic(id_tml, label_tml):
    cursor = db.cursor()
    cursor.execute("UPDATE tbl_m_linguistic SET label_tml = %s WHERE id_tml = %s", (label_tml, id_tml))
    db.commit()
    cursor.close()

# Halaman utama
@app.route('/')
def index():
    linguistic = get_linguistic()
    return render_template('lingu.html', linguistic=linguistic)

# Halaman tambah data
@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        name_tmv = request.form['name_tmv']
        label_tml = request.form['label_tml']
        add_linguistic(name_tmv, label_tml)
        flash('Data linguistik berhasil ditambahkan', 'success')
        return redirect('/')

# Halaman edit data
@app.route('/edit/<int:id_tml>', methods=['POST', 'GET'])
def edit(id_tml):
    cursor = db.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT v.name_tmv, l.label_tml FROM tbl_m_linguistic l INNER JOIN tbl_m_variabel v ON l.id_tmv = v.id_tmv WHERE l.id_tml = %s", (id_tml,))
        linguistic = cursor.fetchone()
        return render_template('edit_lingu.html', linguistic=linguistic)
    if request.method == 'POST':
        label_tml = request.form['label_tml']
        edit_linguistic(id_tml, label_tml)
        flash('Data linguistik berhasil diperbarui', 'success')
        return redirect('/')

# Halaman hapus data
@app.route('/delete/<int:id_tml>', methods=['POST'])
def delete(id_tml):
    if request.method == 'POST':
        delete_linguistic(id_tml)
        flash('Data linguistik berhasil dihapus', 'success')
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
