import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS

# ==============================================================================
# 1. CONFIGURAZIONE DEL DATABASE MYSQL (AIVEN)
# ==============================================================================

# Credenziali per il database Aiven fornite dall'utente
db_config = {
    'host': 'mysql-2421b5ed-iisgalvanimi-a660.j.aivencloud.com',
    'user': 'avnadmin',
    'password': 'AVNS_LMO-6TXmScL79ECZTot',
    'database': 'gestioneDistributori',
    'port': 23707
}

def get_db_connection():
    """Crea e ritorna una connessione al database."""
    conn = mysql.connector.connect(**db_config)
    return conn

# ==============================================================================
# 2. CREAZIONE DELL'APPLICAZIONE FLASK
# ==============================================================================

app = Flask(__name__)
CORS(app) # Abilita CORS per permettere le chiamate dall'interfaccia web

# ==============================================================================
# 3. ROTTE API (CRUD - Create, Read, Update, Delete)
# ==============================================================================

# --- READ (GET all) ---
@app.route('/api/distributori', methods=['GET'])
def get_distributori():
    """API: Ritorna l'elenco di tutti i distributori dal database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # CORREZIONE: 'distributori' cambiato in 'distributore'
        cursor.execute("SELECT * FROM distributore ORDER BY id")
        distributori_db = cursor.fetchall()
        
        for distributore_item in distributori_db:
            if 'prezzo_benzina' in distributore_item and distributore_item['prezzo_benzina'] is not None:
                distributore_item['prezzo_benzina'] = float(distributore_item['prezzo_benzina'])
            if 'prezzo_diesel' in distributore_item and distributore_item['prezzo_diesel'] is not None:
                distributore_item['prezzo_diesel'] = float(distributore_item['prezzo_diesel'])

        return jsonify(distributori_db)
    except mysql.connector.Error as err:
        return jsonify({"errore": f"Errore del database: {err}"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- CREATE (POST) ---
@app.route('/api/distributori', methods=['POST'])
def add_distributore():
    """API: Aggiunge un nuovo distributore al database."""
    data = request.get_json()
    if not data:
        return jsonify({"errore": "Dati non forniti"}), 400

    # CORREZIONE: 'distributori' cambiato in 'distributore'
    query = """
    INSERT INTO distributore (nome, indirizzo, citta, provincia, lat, lon, livello_benzina, capacita_benzina, livello_diesel, capacita_diesel, prezzo_benzina, prezzo_diesel)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        data.get('nome'), data.get('indirizzo'), data.get('citta'), data.get('provincia'),
        data.get('lat'), data.get('lon'), data.get('livello_benzina'), data.get('capacita_benzina'),
        data.get('livello_diesel'), data.get('capacita_diesel'), data.get('prezzo_benzina'), data.get('prezzo_diesel')
    )

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        new_id = cursor.lastrowid
        return jsonify({"messaggio": "Distributore aggiunto con successo", "id": new_id}), 201
    except mysql.connector.Error as err:
        if conn: conn.rollback()
        return jsonify({"errore": f"Errore del database: {err}"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- UPDATE (PUT) ---
@app.route('/api/distributori/<int:id>', methods=['PUT'])
def update_distributore(id):
    """API: Aggiorna un distributore esistente nel database."""
    data = request.get_json()
    if not data:
        return jsonify({"errore": "Dati non forniti"}), 400

    # CORREZIONE: 'distributori' cambiato in 'distributore'
    query = """
    UPDATE distributore SET 
    nome=%s, indirizzo=%s, citta=%s, provincia=%s, lat=%s, lon=%s, 
    livello_benzina=%s, capacita_benzina=%s, livello_diesel=%s, capacita_diesel=%s, 
    prezzo_benzina=%s, prezzo_diesel=%s
    WHERE id = %s
    """
    params = (
        data.get('nome'), data.get('indirizzo'), data.get('citta'), data.get('provincia'),
        data.get('lat'), data.get('lon'), data.get('livello_benzina'), data.get('capacita_benzina'),
        data.get('livello_diesel'), data.get('capacita_diesel'), data.get('prezzo_benzina'), data.get('prezzo_diesel'),
        id
    )

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"errore": "Nessun distributore trovato con questo ID"}), 404
        return jsonify({"messaggio": f"Distributore ID {id} aggiornato con successo"})
    except mysql.connector.Error as err:
        if conn: conn.rollback()
        return jsonify({"errore": f"Errore del database: {err}"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- DELETE ---
@app.route('/api/distributori/<int:id>', methods=['DELETE'])
def delete_distributore(id):
    """API: Elimina un distributore dal database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # CORREZIONE: 'distributori' cambiato in 'distributore'
        cursor.execute("DELETE FROM distributore WHERE id = %s", (id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"errore": "Nessun distributore trovato con questo ID"}), 404
        return jsonify({"messaggio": f"Distributore ID {id} eliminato con successo"})
    except mysql.connector.Error as err:
        if conn: conn.rollback()
        return jsonify({"errore": f"Errore del database: {err}"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# --- UPDATE PRICES BY PROVINCE (existing endpoint) ---
@app.route('/api/prezzo/provincia/<string:provincia>', methods=['POST'])
def set_prezzo_provincia(provincia):
    """API: Modifica il prezzo per tutti i distributori di una provincia."""
    data = request.get_json()
    conn = None
    
    query_parts = []
    params = []
    if 'prezzo_benzina' in data and data['prezzo_benzina']:
        query_parts.append("prezzo_benzina = %s")
        params.append(float(data['prezzo_benzina']))
    if 'prezzo_diesel' in data and data['prezzo_diesel']:
        query_parts.append("prezzo_diesel = %s")
        params.append(float(data['prezzo_diesel']))

    if not query_parts:
        return jsonify({"errore": "Nessun prezzo fornito"}), 400

    params.append(provincia)
    # CORREZIONE: 'distributori' cambiato in 'distributore'
    query = f"UPDATE distributore SET {', '.join(query_parts)} WHERE provincia = %s"

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        conn.commit()
        modificati = cursor.rowcount
        if modificati > 0:
            return jsonify({"messaggio": f"Prezzi aggiornati per {modificati} distributori in provincia di {provincia.upper()}."})
        else:
            return jsonify({"errore": f"Nessun distributore trovato per la provincia {provincia.upper()}"}), 404
    except mysql.connector.Error as err:
        if conn: conn.rollback()
        return jsonify({"errore": f"Errore del database: {err}"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# ==============================================================================
# 4. ESECUZIONE DELL'APPLICAZIONE
# ==============================================================================

if __name__ == '__main__':
    print("=====================================================")
    print("🚀 Server API Iperstaroil in esecuzione!")
    print("🔗 Endpoint base: http://127.0.0.1:5000")
    print("=====================================================")
    app.run(debug=True, port=5000)