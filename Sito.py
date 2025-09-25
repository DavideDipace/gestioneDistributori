from flask import Flask

# ==============================================================================
# 1. CREAZIONE DELL'APPLICAZIONE FLASK PER IL CLIENT
# ==============================================================================

app = Flask(__name__)

# ==============================================================================
# 2. CONFIGURAZIONE E ROTTA WEB
# ==============================================================================

@app.route('/')
def home():
    """
    Pagina principale che serve l'interfaccia web con la mappa.
    Questa pagina si connetterà via JavaScript al server API (server.py).
    """
    
    # !!! IMPORTANTE: Sostituisci questo URL con l'indirizzo pubblico del tuo server.py !!!
    # Esempio: "https://tuo-workspace-xyz-5000.preview.app.github.dev"
    api_server_url = "https://opulent-computing-machine-x7g9wjq679jcvpw4-5000.app.github.dev" # Sostituisci con l'URL pubblico!

    html_content = f'''
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Gestione Distributori Iperstaroil</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
        <style>
            body {{
                display: flex;
            }}
            #sidebar {{
                width: 450px;
                min-width: 400px;
                height: 100vh;
                display: flex;
                flex-direction: column;
                padding: 1rem;
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }}
            #map {{
                flex-grow: 1;
                height: 100vh;
            }}
            .list-group-item .btn-group {{
                visibility: hidden;
            }}
            .list-group-item:hover .btn-group {{
                visibility: visible;
            }}
        </style>
    </head>
    <body>

    <!-- Sidebar per controlli e lista -->
    <div id="sidebar">
        <h3 class="mb-3 text-center">Gestione Iperstaroil ⛽</h3>
        <div id="alert-container-sidebar"></div>
        <div class="d-grid gap-2 mb-3">
            <button class="btn btn-primary" type="button" data-bs-toggle="modal" data-bs-target="#distributoreModal" onclick="prepareAddModal()">
                Aggiungi Nuovo Distributore
            </button>
        </div>
        <div class="card shadow-sm flex-grow-1">
            <div class="card-header">Elenco Distributori</div>
            <div class="card-body" style="overflow-y: auto;">
                <ul id="lista-distributori" class="list-group list-group-flush"></ul>
            </div>
        </div>
    </div>

    <!-- Mappa -->
    <div id="map"></div>

    <!-- Modale per Aggiungere/Modificare Distributore -->
    <div class="modal fade" id="distributoreModal" tabindex="-1" aria-labelledby="modalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="modalLabel">Aggiungi Distributore</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="distributoreForm">
                        <input type="hidden" id="distributoreId">
                        <div class="row">
                            <div class="col-md-6 mb-3"><label class="form-label">Nome</label><input type="text" id="nome" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Indirizzo</label><input type="text" id="indirizzo" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Città</label><input type="text" id="citta" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Provincia</label><input type="text" id="provincia" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Latitudine</label><input type="number" step="any" id="lat" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Longitudine</label><input type="number" step="any" id="lon" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Livello Benzina (L)</label><input type="number" id="livello_benzina" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Capacità Benzina (L)</label><input type="number" id="capacita_benzina" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Livello Diesel (L)</label><input type="number" id="livello_diesel" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Capacità Diesel (L)</label><input type="number" id="capacita_diesel" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Prezzo Benzina (€)</label><input type="number" step="0.001" id="prezzo_benzina" class="form-control" required></div>
                            <div class="col-md-6 mb-3"><label class="form-label">Prezzo Diesel (€)</label><input type="number" step="0.001" id="prezzo_diesel" class="form-control" required></div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annulla</button>
                    <button type="button" class="btn btn-primary" onclick="handleFormSubmit()">Salva</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Modale di Conferma Eliminazione -->
    <div class="modal fade" id="confirmDeleteModal" tabindex="-1" aria-labelledby="confirmDeleteModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="confirmDeleteModalLabel">Conferma Eliminazione</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    Sei sicuro di voler eliminare questo distributore? L'azione è irreversibile.
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annulla</button>
                    <button type="button" class="btn btn-danger" id="confirmDeleteBtn">Elimina</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <script>
        const API_URL = '{api_server_url}'; 
        let map;
        let distributoriData = [];
        let distributoreModal;
        let confirmDeleteModal;

        // --- INIZIALIZZAZIONE ---
        document.addEventListener('DOMContentLoaded', () => {{
            initMap();
            caricaDati();
            distributoreModal = new bootstrap.Modal(document.getElementById('distributoreModal'));
            confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
        }});

        function initMap() {{
            map = L.map('map').setView([41.9, 12.5], 6);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}).addTo(map);
        }}

        // --- GESTIONE DATI (FETCH) ---
        async function caricaDati() {{
            try {{
                const response = await fetch(`${{API_URL}}/api/distributori`);
                const data = await response.json();
                if (!response.ok) throw new Error(data.errore || 'Errore caricamento dati.');
                
                distributoriData = data;
                aggiornaLista(distributoriData);
                aggiornaMappa(distributoriData);
            }} catch (error) {{
                showAlert(error.message, 'danger');
            }}
        }}

        // --- AGGIORNAMENTO UI ---
        function aggiornaLista(distributori) {{
            const listaUl = document.getElementById('lista-distributori');
            listaUl.innerHTML = '';
            distributori.forEach(d => {{
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                li.innerHTML = `
                    <div>
                        <b>${{d.id}}. ${{d.nome}}</b> (${{d.provincia}})<br>
                        <small>Benzina: ${{parseFloat(d.prezzo_benzina).toFixed(3)}}€ | Diesel: ${{parseFloat(d.prezzo_diesel).toFixed(3)}}€</small>
                    </div>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-outline-secondary" onclick="prepareEditModal(${{d.id}})">Modifica</button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteDistributore(${{d.id}})">Elimina</button>
                    </div>
                `;
                listaUl.appendChild(li);
            }});
        }}

        function aggiornaMappa(distributori) {{
            map.eachLayer(layer => {{ if (layer instanceof L.Marker) map.removeLayer(layer); }});
            distributori.forEach(d => {{
                const popupText = `<b>${{d.nome}}</b><br>Provincia: ${{d.provincia}}<br>Benzina: ${{parseFloat(d.prezzo_benzina).toFixed(3)}}€<br>Diesel: ${{parseFloat(d.prezzo_diesel).toFixed(3)}}€`;
                L.marker([d.lat, d.lon]).addTo(map).bindPopup(popupText);
            }});
        }}
        
        // --- MODALE E FORM ---
        function prepareAddModal() {{
            document.getElementById('distributoreForm').reset();
            document.getElementById('distributoreId').value = '';
            document.getElementById('modalLabel').textContent = 'Aggiungi Nuovo Distributore';
        }}

        function prepareEditModal(id) {{
            const distributore = distributoriData.find(d => d.id === id);
            if (!distributore) return;
            
            document.getElementById('distributoreId').value = distributore.id;
            document.getElementById('modalLabel').textContent = `Modifica Distributore ID: ${{distributore.id}}`;
            
            for (const key in distributore) {{
                const element = document.getElementById(key);
                if (element) {{
                    element.value = distributore[key];
                }}
            }}
            distributoreModal.show();
        }}
        
        async function handleFormSubmit() {{
            const id = document.getElementById('distributoreId').value;
            const isEditing = !!id;

            const distributoreData = {{}};
            const formElements = document.getElementById('distributoreForm').elements;
            for (const element of formElements) {{
                if (element.id && element.value !== undefined) {{
                   distributoreData[element.id] = element.value;
                }}
            }}
            delete distributoreData.distributoreId;

            const url = isEditing ? `${{API_URL}}/api/distributori/${{id}}` : `${{API_URL}}/api/distributori`;
            const method = isEditing ? 'PUT' : 'POST';

            // Log per debug
            console.log('Invio dati al server:', {{ url, method, payload: distributoreData }});

            try {{
                const response = await fetch(url, {{
                    method: method,
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(distributoreData)
                }});
                const result = await response.json();
                if (!response.ok) throw new Error(result.errore || `Errore durante il salvataggio.`);
                
                showAlert(result.messaggio, 'success');
                distributoreModal.hide();
                caricaDati();
            }} catch (error) {{
                showAlert(error.message, 'danger');
                console.error("Dettagli errore:", error);
            }}
        }}

        // --- AZIONI CRUD (DELETE) ---
        function deleteDistributore(id) {{
            const confirmBtn = document.getElementById('confirmDeleteBtn');
            confirmBtn.onclick = () => executeDelete(id);
            confirmDeleteModal.show();
        }}

        async function executeDelete(id) {{
            confirmDeleteModal.hide();
            try {{
                const response = await fetch(`${{API_URL}}/api/distributori/${{id}}`, {{ method: 'DELETE' }});
                const result = await response.json();
                if (!response.ok) throw new Error(result.errore || 'Errore durante l-eliminazione.');
                
                showAlert(result.messaggio, 'success');
                caricaDati();
            }} catch (error) {{
                showAlert(error.message, 'danger');
            }}
        }}

        // --- UTILITY ---
        function showAlert(message, category = 'success') {{
            const container = document.getElementById('alert-container-sidebar');
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${{category}} alert-dismissible fade show`;
            alertDiv.role = 'alert';
            alertDiv.innerHTML = `${{message}}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;
            container.innerHTML = '';
            container.appendChild(alertDiv);
        }}

    </script>
    </body>
    </html>
    '''
    return html_content

# ==============================================================================
# 3. ESECUZIONE DELL'APPLICAZIONE
# ==============================================================================

if __name__ == '__main__':
    print("=====================================================")
    print("🚀 Client Web Iperstaroil in esecuzione!")
    print("🔗 Apri il browser e vai all'URL pubblico fornito dal tuo ambiente per la porta 8000")
    print("=====================================================")
    app.run(host='0.0.0.0', debug=True, port=8000)

