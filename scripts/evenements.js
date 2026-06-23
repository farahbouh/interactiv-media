const API_URL = "https://interactiv-media.onrender.com";

// Skeleton loader : 3 cartes grises animées pendant le chargement
function afficherSkeleton() {
    const container = document.getElementById('events-container');
    let html = '';
    for (let i = 0; i < 3; i++) {
        html += `
            <article class="event-card skeleton-card">
                <div class="skeleton skeleton-date"></div>
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-text"></div>
                <div class="skeleton skeleton-text" style="width:70%"></div>
            </article>
        `;
    }
    container.innerHTML = html;
}

async function chargerEvenements() {
    afficherSkeleton();

    try {
        const response = await fetch(API_URL + '/api/evenements');
        const evenements = await response.json();

        const container = document.getElementById('events-container');

        if (evenements.length === 0) {
            container.innerHTML = '<p style="text-align:center">Aucun événement à venir pour le moment.</p>';
            return;
        }

        let html = '';
        for (let event of evenements) {
            html += `
                <article class="event-card">
                    <p class="event-date"><strong>${event.date}</strong></p>
                    <h2>${event.titre}</h2>
                    <p>${event.description}</p>
                </article>
            `;
        }
        container.innerHTML = html;

    } catch (error) {
        console.error('Erreur:', error);
        document.getElementById('events-container').innerHTML =
            '<p style="color:red">Erreur de chargement des événements. Veuillez réessayer.</p>';
    }
}

chargerEvenements();
