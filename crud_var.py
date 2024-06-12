from flask import Flask, render_template, request, redirect, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Koneksi ke database
db = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='sistem_pakar'
)
cursor = db.cursor()

# Fungsi CRUD
def get_variabels():
    cursor.execute("SELECT * FROM tbl_m_variabel")
    return cursor.fetchall()

def get_variabel(id):
    cursor.execute("SELECT * FROM tbl_m_variabel WHERE id_tmv = %s", (id,))
    return cursor.fetchone()

def add_variabel(name, type, question):
    cursor.execute("INSERT INTO tbl_m_variabel (name_tmv, type_tmv, question_tmv) VALUES (%s, %s, %s)", (name, type, question))
    db.commit()

def update_variabel(id, name, type, question):
    cursor.execute("UPDATE tbl_m_variabel SET name_tmv = %s, type_tmv = %s, question_tmv = %s WHERE id_tmv = %s", (name, type, question, id))
    db.commit()

def delete_variabel(id):
    cursor.execute("DELETE FROM tbl_m_variabel WHERE id_tmv = %s", (id,))
    db.commit()

# Routes
@app.route('/')
def index():
    variabels = get_variabels()
    return render_template('admin.html', variabels=variabels)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    type = request.form['type']
    question = request.form['question']
    add_variabel(name, type, question)
    flash('Variabel berhasil ditambahkan!', 'success')
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    variabel = get_variabel(id)
    return render_template('edit.html', variabel=variabel)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    name = request.form['name']
    type = request.form['type']
    question = request.form['question']
    update_variabel(id, name, type, question)
    flash('Variabel berhasil diperbarui!', 'success')
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    delete_variabel(id)
    flash('Variabel berhasil dihapus!', 'success')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
