document.addEventListener("DOMContentLoaded", () => {
    let questions = [];
    let index = 0;
    let score = 0;

    fetch("data/questions.json").then(res => res.json()).then(data => {
        questions = data;
        afficherQuestion();
    }).catch(() => {
        document.getElementById("quiz-container").innerHTML = "<p>Erreur chargement du quiz.</p>";
    });

    function afficherQuestion() {
        if (index >= questions.length) {
            document.getElementById("quiz-container").innerHTML = "";
            document.getElementById("result").innerHTML = `
                <h2>Score : ${score} / ${questions.length}</h2>
                <p>${messageFinal()}</p>
                <input type="text" id="pseudo-input" placeholder="Ton pseudo" maxlength="20" />
                <button id="btn-envoyer">Envoyer mon score</button>
                <p id="msg-envoi"></p>
            `;

            document.getElementById("btn-envoyer").onclick = () => {
                const pseudo = document.getElementById("pseudo-input").value.trim();
                if (!pseudo) {
                    document.getElementById("msg-envoi").textContent = "Entre un pseudo !";
                    return;
                }
                envoyerScore(pseudo, score);
            };
            return;
        }

        const q = questions[index];
        let html = `<div class="quiz-card"><h3>${q.question}</h3>`;
        q.options.forEach((opt, i) => {
            html += `<button class="quiz-option" data-val="${i}">${opt}</button>`;
        });
        html += "</div>";
        document.getElementById("quiz-container").innerHTML = html;

        document.querySelectorAll(".quiz-option").forEach(btn => {
            btn.onclick = () => {
                if (parseInt(btn.dataset.val) === q.answer) score++;
                index++;
                afficherQuestion();
            };
        });
    }

    function envoyerScore(pseudo, score) {
        document.getElementById("msg-envoi").textContent = "Envoi en cours...";

        fetch("https://interactiv-media.onrender.com/api/score", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pseudo, score })
        })
        .then(res => res.json())
        .then(() => {
            document.getElementById("msg-envoi").textContent = "Score enregistré ! 🎉";
            afficherLeaderboard();
        })
        .catch(() => {
            document.getElementById("msg-envoi").textContent = "Erreur lors de l'envoi.";
        });
    }

    function afficherLeaderboard() {
        fetch("https://interactiv-media.onrender.com/api/scores")
        .then(res => res.json())
        .then(data => {
            let html = "<h3> Top 10</h3><ol>";
            data.forEach(entry => {
                html += `<li>${entry.pseudo} — ${entry.score}</li>`;
            });
            html += "</ol>";
            document.getElementById("result").innerHTML += html;
        });
    }

    function messageFinal() {
        const total = questions.length;
        if (score === total) return "Parfait !";
        if (score >= total - 1) return "Très bien !";
        if (score >= total / 2) return "Pas mal.";
        return "Peut mieux faire.";
    }
});