from flask import Flask, render_template, request, jsonify
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import mysql.connector

app = Flask(__name__)

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Fungsi untuk membuat variabel input dengan nama linguistik khusus
def create_custom_antecedent(name, range_values, linguistic_labels):
    antecedent = ctrl.Antecedent(np.arange(*range_values), name)
    antecedent.automf(3, names=linguistic_labels)
    return antecedent

def create_consequent(name, range_values, linguistic_labels):
    consequent = ctrl.Consequent(np.arange(*range_values), name)
    consequent.automf(3, names=linguistic_labels)
    return consequent

# Koneksi ke database
db = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='',
    database='sistem_pakar'
)

# Definisi variabel input dari database
cursor = db.cursor()
sql_query = """
    SELECT mv.name_tmv AS var_name, GROUP_CONCAT(ml.label_tml ORDER BY ml.id_tml) AS linguistic_labels
    FROM tbl_m_variabel mv
    JOIN tbl_m_linguistic ml ON mv.id_tmv = ml.id_tmv
    WHERE mv.type_tmv = 'input'
    GROUP BY mv.id_tmv;
"""
cursor.execute(sql_query)
input_var_definitions = []
for var_name, linguistic_labels in cursor:
    input_var_definitions.append({'var_name': var_name, 'linguistic_labels': linguistic_labels.split(',')})
cursor.close()

# Inisialisasi variabel input
range_values = (1, 11, 1)
input_vars = {
    item['var_name']: create_custom_antecedent(item['var_name'], range_values, item['linguistic_labels'])
    for item in input_var_definitions
}

# Inisialisasi variabel output
output_linguistic_labels = ['otoriter', 'tidak_terlibat', 'permisif', 'demokratis']
output_var = create_consequent('pola_asuh', range_values, output_linguistic_labels)

# Mendefinisikan aturan fuzzy dari data di database
cursor = db.cursor()
sql_query = "SELECT * FROM vw_fuzzy_rules"
cursor.execute(sql_query)
rules_data = []
for row in cursor:
    rule_data = {
        'rule': row[1],
        'variable': row[2],
        'linguistic': row[3],
        'output': row[4]
    }
    rules_data.append(rule_data)
cursor.close()

def define_rules_from_data(rules_data, input_vars, output_var):
    rules_dict = {}
    rules = []
    for item in rules_data:
        rule_id = item['rule']
        if rule_id not in rules_dict:
            rules_dict[rule_id] = []
        rules_dict[rule_id].append(item)

    for rule_id, conditions in rules_dict.items():
        antecedent = None
        for condition in conditions:
            var_name = condition['variable']
            linguistic_value = condition['linguistic']
            if antecedent is None:
                antecedent = input_vars[var_name][linguistic_value]
            else:
                antecedent &= input_vars[var_name][linguistic_value]
        output = conditions[0]['output']
        rule = ctrl.Rule(antecedent, output_var[output])
        rules.append(rule)
    return rules

# Definisikan aturan fuzzy dari data
fuzzy_rules = define_rules_from_data(rules_data, input_vars, output_var)

# Fungsi untuk menjalankan simulasi dan mendapatkan nilai keanggotaan output
def simulate(inputs, rules, input_values):
    # Buat sistem kontrol dan simulasi
    control_system = ctrl.ControlSystem(rules)
    simulation = ctrl.ControlSystemSimulation(control_system)
    
    # Masukkan nilai-nilai input
    for var, value in input_values.items():
        simulation.input[var] = value
    
    try:
        # Hitung simulasi
        simulation.compute()
        output_value = simulation.output['pola_asuh']
        
        # Dapatkan nilai keanggotaan untuk setiap label linguistik output
        membership_values = {label: fuzz.interp_membership(output_var.universe, output_var[label].mf, output_value)
                             for label in output_linguistic_labels}
        
        # Dapatkan label dengan nilai keanggotaan terbesar
        max_membership_label = max(output_linguistic_labels, key=lambda label: membership_values[label])
        
        # Dapatkan nilai keanggotaan terbesar
        max_membership_value = membership_values[max_membership_label]
        
        # Tampilkan hasil output
        print(f"Pola Asuh: {max_membership_label.capitalize()}")
        print(f"Nilai Keanggotaan Terbesar: {max_membership_value:.4f}")
        
        return output_value, membership_values, max_membership_label.capitalize()
      
            
    except (AssertionError, ValueError):
        return None, None, "-"


# Rute untuk menerima input dan memberikan output
@app.route('/fuzzy', methods=['POST'])
def fuzzy_logic():
    input_values = {key: int(value) for key, value in
                        request.json.items()}
    
    output_value, membership_values, pola_asuh = simulate(input_vars, fuzzy_rules, input_values)
    
    response = {
        "output_value": output_value,
        "membership_values": membership_values,
        "pola_asuh": pola_asuh
    }
    
    return jsonify(response)

# Rute untuk menampilkan halaman index.html
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

