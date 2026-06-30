const API_URL = "https://interactiv-media.onrender.com";

let token = null;

function afficherFeedback(idElement, message, type = 'succes') {
    const el = document.getElementById(idElement);
    if (!el) return;
    el.textContent = message;
    el.className = type === 'succes' ? 'feedback-succes' : 'feedback-erreur';
    setTimeout(() => { el.textContent = ''; el.className = ''; }, 4000);
}

async function login() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
        document.getElementById('errorMsg').textContent = 'Veuillez remplir tous les champs.';
        return;
    }

    try {
        const response = await fetch(API_URL + '/api/admin/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (response.ok) {
            token = data.token;
            document.getElementById('loginDiv').classList.add('hidden');
            document.getElementById('adminDiv').classList.remove('hidden');
            chargerEvenements();
        } else {
            document.getElementById('errorMsg').textContent = data.erreur || 'Identifiants incorrects';
        }
    } catch (error) {
        document.getElementById('errorMsg').textContent = 'Erreur de connexion : ' + error.message;
    }
}

async function chargerEvenements() {
    try {
        const response = await fetch(API_URL + '/api/admin/evenements', {
            headers: { 'Authorization': 'Bearer ' + token }
        });
        if (!response.ok) throw new Error('Erreur HTTP ' + response.status);
        const evenements = await response.json();

        let html = '';
        for (let event of evenements) {
            html += `
                <div class="event-item">
                    <div id="feedback_${event.id}" role="alert"></div>
                    <div>
                        <label>Type</label>
                        <input type="text" id="type_${event.id}" value="${escHtml(event.type || '')}" placeholder="Type (Débat, Projection...)">
                    </div>
                    <div>
                        <label>Titre *</label>
                        <input type="text" id="titre_${event.id}" value="${escHtml(event.titre || '')}" placeholder="Titre">
                    </div>
                    <div>
                        <label>Date *</label>
                        <input type="date" id="date_${event.id}" value="${escHtml(event.date || '')}">
                    </div>
                    <div>
                        <label>Lieu</label>
                        <input type="text" id="lieu_${event.id}" value="${escHtml(event.lieu || '')}" placeholder="Lieu">
                    </div>
                    <div>
                        <label>Description *</label>
                        <textarea id="desc_${event.id}" rows="3">${escHtml(event.description || '')}</textarea>
                    </div>
                    <button type="button" onclick="modifierEvenement(${event.id})" class="btn-ajouter">Modifier</button>
                    <button type="button" onclick="supprimerEvenement(${event.id})" class="btn-supprimer">Supprimer</button>
                </div>
            `;
        }
        document.getElementById('evenementsList').innerHTML = html || '<p>Aucun événement.</p>';
    } catch (error) {
        afficherFeedback('feedbackListe', 'Erreur de chargement : ' + error.message, 'erreur');
    }
}

async function ajouterEvenement() {
    const type        = document.getElementById('newType').value.trim();
    const titre       = document.getElementById('newTitre').value.trim();
    const date        = document.getElementById('newDate').value;
    const lieu        = document.getElementById('newLieu').value.trim();
    const description = document.getElementById('newDescription').value.trim();

    if (!titre) { afficherFeedback('feedbackAjout', 'Le titre est obligatoire.', 'erreur'); return; }
    if (!date)  { afficherFeedback('feedbackAjout', 'La date est obligatoire.', 'erreur'); return; }
    if (!description) { afficherFeedback('feedbackAjout', 'La description est obligatoire.', 'erreur'); return; }

    try {
        const response = await fetch(API_URL + '/api/admin/evenements', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
            body: JSON.stringify({ type, titre, date, lieu, description })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.erreur || 'Erreur HTTP ' + response.status);
        }

        afficherFeedback('feedbackAjout', '✓ Événement ajouté avec succès.', 'succes');

        document.getElementById('newType').value = '';
        document.getElementById('newTitre').value = '';
        document.getElementById('newDate').value = '';
        document.getElementById('newLieu').value = '';
        document.getElementById('newDescription').value = '';

        chargerEvenements();
    } catch (error) {
        afficherFeedback('feedbackAjout', 'Erreur : ' + error.message, 'erreur');
    }
}

async function modifierEvenement(id) {
    const type        = document.getElementById('type_' + id).value.trim();
    const titre       = document.getElementById('titre_' + id).value.trim();
    const date        = document.getElementById('date_' + id).value;
    const lieu        = document.getElementById('lieu_' + id).value.trim();
    const description = document.getElementById('desc_' + id).value.trim();

    if (!titre) { afficherFeedback('feedback_' + id, 'Le titre est obligatoire.', 'erreur'); return; }
    if (!date)  { afficherFeedback('feedback_' + id, 'La date est obligatoire.', 'erreur'); return; }
    if (!description) { afficherFeedback('feedback_' + id, 'La description est obligatoire.', 'erreur'); return; }

    try {
        const response = await fetch(API_URL + '/api/admin/evenements/' + id, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
            body: JSON.stringify({ type, titre, date, lieu, description })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.erreur || 'Erreur HTTP ' + response.status);
        }

        afficherFeedback('feedback_' + id, '✓ Événement modifié avec succès.', 'succes');
        chargerEvenements();
    } catch (error) {
        afficherFeedback('feedback_' + id, 'Erreur : ' + error.message, 'erreur');
    }
}

async function supprimerEvenement(id) {
    if (!confirm('Supprimer cet événement ?')) return;

    try {
        const response = await fetch(API_URL + '/api/admin/evenements/' + id, {
            method: 'DELETE',
            headers: { 'Authorization': 'Bearer ' + token }
        });

        if (!response.ok) throw new Error('Erreur HTTP ' + response.status);
        afficherFeedback('feedbackListe', '✓ Événement supprimé.', 'succes');
        chargerEvenements();
    } catch (error) {
        afficherFeedback('feedbackListe', 'Erreur suppression : ' + error.message, 'erreur');
    }
}

function deconnexion() {
    token = null;
    document.getElementById('loginDiv').classList.remove('hidden');
    document.getElementById('adminDiv').classList.add('hidden');
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}

// Échapper le HTML pour éviter les injections XSS
function escHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btnLogin').addEventListener('click', login);
    document.getElementById('btnAjouter').addEventListener('click', ajouterEvenement);
    document.getElementById('btnDeconnexion').addEventListener('click', deconnexion);

    // Permettre connexion avec Entrée
    document.getElementById('password').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') login();
    });
});