const API_URL = "https://interactiv-media.onrender.com";

function afficherSkeleton() {
    const container = document.getElementById('events-container');
    if (!container) return;
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

function formaterDate(date) {
    const d = new Date(date);
    if (isNaN(d)) return date;
    return d.toLocaleDateString('fr-FR', {
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    });
}

function getBadge(dateStr) {
    const today = new Date(); today.setHours(0,0,0,0);
    const d = new Date(dateStr); d.setHours(0,0,0,0);
    if (d.getTime() === today.getTime()) {
        return `<span class="event-badge badge-aujourd-hui"><span class="badge-dot"></span>En ce moment</span>`;
    } else if (d > today) {
        return `<span class="event-badge badge-a-venir">A venir</span>`;
    } else {
        return `<span class="event-badge badge-passe">Passe</span>`;
    }
}

async function chargerEvenements() {
    afficherSkeleton();

    try {
        const response = await fetch(API_URL + '/api/evenements');
        const evenements = await response.json();

        const container = document.getElementById('events-container');
        if (!container) return;

        if (evenements.length === 0) {
            container.innerHTML = '<p style="text-align:center">Aucun événement pour le moment.</p>';
            return;
        }

        const tries = [...evenements].sort((a, b) => new Date(b.date) - new Date(a.date));

        let html = '';
        for (let event of tries) {
            html += `
                <article class="event-card">
                    <div class="event-card-header">
                        ${event.type ? `<span class="event-type">${event.type}</span>` : ''}
                        ${getBadge(event.date)}
                    </div>
                    <p class="event-date">${formaterDate(event.date)}</p>
                    <h2 class="event-titre">${event.titre}</h2>
                    ${event.lieu ? `<p class="event-lieu">${event.lieu}</p>` : ''}
                    <p class="event-description">${event.description}</p>
                </article>
            `;
        }
        container.innerHTML = html;

    } catch (error) {
        console.error('Erreur:', error);
        const container = document.getElementById('events-container');
        if (container) container.innerHTML = '<p style="color:red">Erreur de chargement des événements. Veuillez réessayer.</p>';
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
        const dateStr = formaterDate(ev.date);
        const type = ev.type || 'Événement';
        const lieu = ev.lieu ? ` – ${ev.lieu}` : '';
        el.innerHTML = `<strong>Prochain ${type.toLowerCase()} : <a href="evenements.html">« ${ev.titre} »</a></strong> – ${dateStr}${lieu}`;
    } catch {
        el.style.display = 'none';
    }
}

chargerEvenements();
afficherProchainEvenement();
