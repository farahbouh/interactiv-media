const API_URL = "https://interactiv-media.onrender.com";

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
            const dateStr = new Date(event.date).toLocaleDateString('fr-FR', {
                weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
            });
            html += `
                <article class="event-card">
                    <p class="event-date"><strong>${dateStr}</strong></p>
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

async function afficherProchainEvenement() {
    const el = document.getElementById('prochain-evenement');
    if (!el) return;
    try {
        const res = await fetch(API_URL + '/api/evenements');
        const events = await res.json();
        const today = new Date(); today.setHours(0,0,0,0);
        const futur = events
            .filter(e => new Date(e.date) >= today)
            .sort((a, b) => new Date(a.date) - new Date(b.date));
        if (!futur.length) { el.style.display = 'none'; return; }
        const ev = futur[0];
        const dateStr = new Date(ev.date).toLocaleDateString('fr-FR', {
            weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
        });
        el.innerHTML = `<strong>Prochain <a href="evenements.html">débat</a> : ${dateStr}</strong> – ${ev.description}`;
    } catch {
        el.style.display = 'none';
    }
}

chargerEvenements();
afficherProchainEvenement();
