document.addEventListener("DOMContentLoaded", () => {
    /* initialisation */
    let questions = [];
    let index = 0;
    let score = 0;

    /* recuperation de la data puis des question et enclenchement du quiz */
    fetch("data/questions.json").then(res => res.json()).then(data => {
            questions = data;
            afficherQuestion();
        })
        .catch(() => {
            document.getElementById("quiz-container").innerHTML = "<p>Erreur chargement du quiz.</p>";
        });

    function afficherQuestion() 
    {
/* Recuperation des elements html pour integrer les questions (quiz container) et le resultats (results) */
        if (index >= questions.length) {
            document.getElementById("quiz-container").innerHTML = "";
            document.getElementById("result").innerHTML = "<h2>Score : " + score + " / " + questions.length + "</h2><p>" + messageFinal() + "</p>";
            return; /* cas d'arret */
        }
        const q = questions[index];
        let html = "<div class=\"quiz-card\"><h3>" + q.question + "</h3>";
        q.options.forEach((opt, i) => {
            html += "<button class=\"quiz-option\" data-val=\"" + i + "\">" + opt + "</button>";
        });
        html += "</div>";
        document.getElementById("quiz-container").innerHTML = html;

        document.querySelectorAll(".quiz-option").forEach(btn => {
            btn.onclick = () => { /* Lors d'un click si reponse valide alors on ajoute 1 point */
                if (parseInt(btn.dataset.val) === q.answer)
                {
                    score++;
                }     
                index++;
                afficherQuestion(); /* Recursif */
            };
        });
    }

    function messageFinal() {
        const total = questions.length;
        if (score === total) {
            return "Parfait !";
        }
        if (score >= total - 1) {
            return "Très bien !";
        }
        if (score >= total / 2) {
            return "Pas mal.";
        }
        return "Peut mieux faire.";
    }
});