const API_URL = "https://interactiv-media.onrender.com";

let token = null;

function afficherFeedback(idElement, message, succes) {
    const el = document.getElementById(idElement);
    el.textContent = message;
    el.style.color = succes ? '#2e7d32' : 'var(--red)';
    el.style.fontWeight = '600';
    el.style.marginBottom = '12px';
    setTimeout(() => { el.textContent = ''; }, 4000);
}

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(API_URL + '/api/admin/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (response.ok) {
            token = data.token;
            document.getElementById('loginDiv').style.display = 'none';
            document.getElementById('adminDiv').style.display = 'block';
            chargerEvenements();
        } else {
            document.getElementById('errorMsg').innerText = 'Identifiants incorrects';
        }
    } catch (error) {
        document.getElementById('errorMsg').innerText = 'Erreur de connexion : ' + error.message;
    }
}

async function chargerEvenements() {
    const response = await fetch(API_URL + '/api/admin/evenements', {
        headers: { 'Authorization': 'Bearer ' + token }
    });
    const evenements = await response.json();

    let html = '';
    for (let event of evenements) {
        html += `
            <div class="event-item">
                <input type="text" id="type_${event.id}" value="${event.type || ''}" placeholder="Type (Débat, Projection...)"><br>
                <input type="text" id="titre_${event.id}" value="${event.titre}" placeholder="Titre"><br>
                <input type="date" id="date_${event.id}" value="${event.date}"><br>
                <input type="text" id="lieu_${event.id}" value="${event.lieu || ''}" placeholder="Lieu"><br>
                <textarea id="desc_${event.id}" rows="3">${event.description}</textarea><br>
                <button onclick="modifierEvenement(${event.id})">Modifier</button>
                <button onclick="supprimerEvenement(${event.id})" class="delete-btn">Supprimer</button>
                <div id="feedback_${event.id}" role="alert"></div>
            </div>
        `;
    }
    document.getElementById('evenementsList').innerHTML = html || '<p>Aucun événement.</p>';
}

async function ajouterEvenement() {
    const type = document.getElementById('newType').value;
    const titre = document.getElementById('newTitre').value;
    const date = document.getElementById('newDate').value;
    const lieu = document.getElementById('newLieu').value;
    const description = document.getElementById('newDescription').value;

    if (!titre || !date) {
        afficherFeedback('feedbackAjout', 'Le titre et la date sont obligatoires.', false);
        return;
    }

    try {
        const response = await fetch(API_URL + '/api/admin/evenements', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
            body: JSON.stringify({ type, titre, date, lieu, description })
        });
        if (response.ok) {
            afficherFeedback('feedbackAjout', 'Événement ajouté avec succès.', true);
            document.getElementById('newType').value = '';
            document.getElementById('newTitre').value = '';
            document.getElementById('newDate').value = '';
            document.getElementById('newLieu').value = '';
            document.getElementById('newDescription').value = '';
            chargerEvenements();
        } else {
            afficherFeedback('feedbackAjout', "Erreur : l'événement n'a pas pu être ajouté.", false);
        }
    } catch {
        afficherFeedback('feedbackAjout', 'Erreur réseau. Veuillez réessayer.', false);
    }
}

async function modifierEvenement(id) {
    const type = document.getElementById('type_' + id).value;
    const titre = document.getElementById('titre_' + id).value;
    const date = document.getElementById('date_' + id).value;
    const lieu = document.getElementById('lieu_' + id).value;
    const description = document.getElementById('desc_' + id).value;

    try {
        const response = await fetch(API_URL + '/api/admin/evenements/' + id, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
            body: JSON.stringify({ type, titre, date, lieu, description })
        });
        if (response.ok) {
            afficherFeedback('feedback_' + id, 'Modifications enregistrées.', true);
            chargerEvenements();
        } else {
            afficherFeedback('feedback_' + id, "Erreur : modification échouée.", false);
        }
    } catch {
        afficherFeedback('feedback_' + id, 'Erreur réseau. Veuillez réessayer.', false);
    }
}

async function supprimerEvenement(id) {
    if (confirm('Supprimer cet événement ?')) {
        try {
            const response = await fetch(API_URL + '/api/admin/evenements/' + id, {
                method: 'DELETE',
                headers: { 'Authorization': 'Bearer ' + token }
            });
            if (response.ok) {
                chargerEvenements();
            } else {
                afficherFeedback('feedbackListe', 'Erreur : suppression échouée.', false);
            }
        } catch {
            afficherFeedback('feedbackListe', 'Erreur réseau. Veuillez réessayer.', false);
        }
    }
}

function deconnexion() {
    token = null;
    document.getElementById('loginDiv').style.display = 'block';
    document.getElementById('adminDiv').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btnLogin').addEventListener('click', login);
    document.getElementById('btnAjouter').addEventListener('click', ajouterEvenement);
    document.getElementById('btnDeconnexion').addEventListener('click', deconnexion);
});
