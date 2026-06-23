// Réveille Render immédiatement au chargement (avec timeout pour ne pas bloquer)
fetch("https://interactiv-media.onrender.com/health", {
    mode: "no-cors",
    signal: AbortSignal.timeout(3000)
}).catch(function() {});

// Ping aussi au survol du lien Événements dans le nav
// pour anticiper le cold start avant que l'utilisateur clique
document.addEventListener('DOMContentLoaded', function () {
    var lienEvenements = document.querySelector('a[href="evenements.html"]');
    if (lienEvenements) {
        var pingFait = false;
        lienEvenements.addEventListener('mouseenter', function () {
            if (!pingFait) {
                fetch("https://interactiv-media.onrender.com/health", {
                    mode: "no-cors",
                    signal: AbortSignal.timeout(3000)
                }).catch(function() {});
                pingFait = true;
            }
        });
        // Sur mobile : touch
        lienEvenements.addEventListener('touchstart', function () {
            if (!pingFait) {
                fetch("https://interactiv-media.onrender.com/health", {
                    mode: "no-cors",
                    signal: AbortSignal.timeout(3000)
                }).catch(function() {});
                pingFait = true;
            }
        }, { passive: true });
    }
});
