from flask import Flask, render_template, request, redirect, flash, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
db = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='sistem_pakar'
)

# Function to fetch data from tbl_t_fuzzy_rules table
def get_rules():
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            r.id_ttfr,
            v.name_tmv AS variable_name,
            l.label_tml AS label_name,
            r.rule_ttfr AS rule,
            r.output_ttfr AS output
        FROM
            tbl_t_fuzzy_rules r
        INNER JOIN
            tbl_m_variabel v ON r.id_tmv = v.id_tmv
        INNER JOIN
            tbl_m_linguistic l ON r.id_tml = l.id_tml
    """)
    rules = cursor.fetchall()
    cursor.close()
    return rules

# Function to fetch data from tbl_m_variabel table
def get_variables():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tbl_m_variabel")
    variables = cursor.fetchall()
    cursor.close()
    return variables

# Function to fetch data from tbl_m_linguistic table
def get_labels(id_tmv):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tbl_m_linguistic WHERE id_tmv = %s", (id_tmv,))
    labels = cursor.fetchall()
    cursor.close()
    return labels

# Create Rule
@app.route('/add_rule', methods=['POST'])
def add_rule():
    if request.method == 'POST':
        id_tmv = request.form['id_tmv']
        id_tml = request.form['id_tml']
        rule_ttfr = request.form['rule_ttfr']
        output_ttfr = request.form['output_ttfr']
        
        cursor = db.cursor()
        cursor.execute("INSERT INTO tbl_t_fuzzy_rules (id_tmv, id_tml, rule_ttfr, output_ttfr) VALUES (%s, %s, %s, %s)", (id_tmv, id_tml, rule_ttfr, output_ttfr))
        db.commit()
        cursor.close()
        flash('Rule added successfully', 'success')
        return redirect('/')

# Edit Rule
@app.route('/edit_rule/<int:id_ttfr>', methods=['GET', 'POST'])
def edit_rule(id_ttfr):
    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tbl_t_fuzzy_rules WHERE id_ttfr = %s", (id_ttfr,))
        rule = cursor.fetchone()
        cursor.close()
        variables = get_variables()
        labels = get_labels(rule[1]) if rule else []
        return render_template('edit_rule.html', rule=rule, variables=variables, labels=labels)
    elif request.method == 'POST':
        id_tmv = request.form['id_tmv']
        id_tml = request.form['id_tml']
        rule_ttfr = request.form['rule_ttfr']
        output_ttfr = request.form['output_ttfr']
        
        cursor = db.cursor()
        cursor.execute("UPDATE tbl_t_fuzzy_rules SET id_tmv = %s, id_tml = %s, rule_ttfr = %s, output_ttfr = %s WHERE id_ttfr = %s", (id_tmv, id_tml, rule_ttfr, output_ttfr, id_ttfr))
        db.commit()
        cursor.close()
        flash('Rule updated successfully', 'success')
        return redirect('/')

# Delete Rule
@app.route('/delete_rule/<int:id_ttfr>', methods=['POST'])
def delete_rule(id_ttfr):
    cursor = db.cursor()
    cursor.execute("DELETE FROM tbl_t_fuzzy_rules WHERE id_ttfr = %s", (id_ttfr,))
    db.commit()
    cursor.close()
    flash('Rule deleted successfully', 'success')
    return redirect('/')

# Main Route
@app.route('/')
def index():
    variables = get_variables()
    rules = get_rules()
    return render_template('rule.html', variables=variables, rules=rules)

# AJAX route to load labels based on selected variable
@app.route('/load_labels')
def load_labels():
    id_tmv = request.args.get('id_tmv')
    labels = get_labels(id_tmv)
    return jsonify({'labels': labels})

if __name__ == '__main__':
    app.run(debug=True)
