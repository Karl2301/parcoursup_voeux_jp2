function Show_Didacticiel() {
    const validateBtn = document.getElementById("validateBtn");
    if (window.innerWidth < 768) {
        console.log("Le didacticiel ne s'exécute pas sur un téléphone.");
        return;
    }

    // Création de l'overlay (fond grisé)
    const tutorialOverlay = document.createElement('div');
    tutorialOverlay.id = "tutorial-overlay";
    tutorialOverlay.style = "position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.0); z-index: 2000; pointer-events: auto;";

    // Création du rectangle de surbrillance
    const transparentShape = document.createElement('div');
    transparentShape.id = "transparent-shape";
    transparentShape.style = "position: absolute; border-radius: 15px; background-color: transparent; box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.8); pointer-events: none; z-index: 2001;";

    // Création du conteneur de description
    const tutorialDescription = document.createElement('div');
    tutorialDescription.className = "tutorial-description";
    tutorialDescription.style = "position: absolute; background: #fff; color: #000; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); text-align: center; max-width: 300px; z-index: 2002;";

    document.body.appendChild(tutorialOverlay);
    document.body.appendChild(transparentShape);
    document.body.appendChild(tutorialDescription);

    // On commence par le welcome step
    let step = 0;
    const steps = [
        {
            isWelcome: true,
            text: "<h2>🎓 Bienvenue sur Voeux-JP2 !</h2><br><br> Cet outil vous permet d'organiser vos vœux Parcoursup de manière simple et efficace. Vous pouvez activer, désactiver et classer vos choix en toute tranquillité.<br><br> <strong>📌 Note :</strong> Cet outil n'est pas lié au site officiel Parcoursup."
        },
        {
            elementId: 'modifyBtn',
            text: "Ce bouton active le mode édition, vous permettant d’<strong>activer ou de désactiver</strong> certains vœux, puis de <strong>modifier leur ordre</strong>."
        },
        {
            elementId: 'disabledOrdersContainer',
            text: "Ce tableau sert de <strong>dépôt</strong> pour vos vœux désactivés. Vous pouvez les réactiver afin de les transférer dans le <strong>tableau principal</strong>.",
            alignTable: true,
            centerTop: true
        },
        {
            elementId: 'recentOrdersContainer',
            text: "Ce tableau vous permet de réorganiser vos vœux grâce au <strong>glisser-déposer</strong>.",
            alignTable: true,
            centerTop: true
        },
        {
            elementId: 'validateBtn',
            text: "Une fois vos vœux organisés, ce bouton vous permet de les <strong>valider définitivement</strong>."
        },
        {
            elementId: 'aide_nav',
            text: "Utilisez ce bouton pour communiquer avec votre <strong>professeur principal</strong>. Chaque demande inclut votre identifiant, veillez donc à l’utiliser avec <strong>discernement</strong>."
        }
    ];

    function showTutorial() {
        // Si toutes les étapes sont passées, on termine le didacticiel
        if (step >= steps.length) {
            console.log("Didacticiel terminé.");
            tutorialOverlay.remove();
            transparentShape.remove();
            tutorialDescription.remove();
            return;
        }

        const stepData = steps[step];

        // Si c'est le welcome step, on centre la popup
        if (stepData.isWelcome) {
            // On masque le transparentShape pour le welcome
            transparentShape.style = "position: absolute; border-radius: 15px; background-color: transparent; box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.8); pointer-events: none; z-index: 2001;";
            tutorialDescription.style.top = "50%";
            tutorialDescription.style.left = "50%";
            tutorialDescription.style.transform = "translate(-50%, -50%)";
            tutorialDescription.style.maxWidth = "800px";
            tutorialDescription.innerHTML = `
                <p>${stepData.text}</p>
                <button class="btn tutorial-next-btn">Commencer</button>
            `;
            return;
        } else {
            // Pour les autres étapes, on s'assure que le transparentShape est visible et on réinitialise la transformation
            transparentShape.style = "position: absolute; border-radius: 15px; background-color: transparent; box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.8); pointer-events: none; z-index: 2001;";
            tutorialDescription.style = "position: absolute; background: #fff; color: #000; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); text-align: center; max-width: 400px; z-index: 2002;";
            transparentShape.style.display = "";
            tutorialDescription.style.transform = "";
        }

        const element = document.getElementById(stepData.elementId);
        let rect;
        if (!element && stepData.elementId === 'modifyBtn') {
            // Attente que le bouton modifyBtn soit disponible
            const interval = setInterval(() => {
                const el = document.getElementById('modifyBtn');
                if (el) {
                    clearInterval(interval);
                    rect = el.getBoundingClientRect();
                    positionShapeAndDescription(rect, stepData);
                }
            }, 100);
            return;
        } else if (!element) {
            console.error(`Élément ${stepData.elementId} introuvable.`);
            return;
        } else {
            rect = element.getBoundingClientRect();
            positionShapeAndDescription(rect, stepData);
        }

        // Pour l'étape 5, centrer le haut du div "disabledOrdersContainer" verticalement sur l'écran
        if (stepData.elementId === 'disabledOrdersContainer') {
            const viewportHeight = window.innerHeight;
            const targetScrollPosition = rect.top + window.scrollY - (viewportHeight / 4);

            // Effectuer un défilement fluide
            window.scrollTo({
                top: targetScrollPosition,
                behavior: 'smooth'
            });
        } else if (stepData.elementId === 'recentOrdersContainer') {
            const viewportHeight = window.innerHeight;
            const targetScrollPosition = 0;

            // Effectuer un défilement fluide
            window.scrollTo({
                top: targetScrollPosition,
                behavior: 'smooth'
            });
        }
    }

    function positionShapeAndDescription(rect, stepData) {
        transparentShape.style.width = `${rect.width + 40}px`;
        transparentShape.style.height = `${rect.height + 20}px`;
        transparentShape.style.borderRadius = "15px";
        transparentShape.style.top = `${rect.top + window.scrollY - 10}px`;
        transparentShape.style.left = `${rect.left + window.scrollX - 20}px`;

        if (stepData.elementId === 'modifyBtn') {
            // Positionner la description à gauche du bouton "Modifier"
            tutorialDescription.style.top = `${rect.top + window.scrollY}px`;
            tutorialDescription.style.left = `${rect.left + window.scrollX - tutorialDescription.offsetWidth - 30}px`;
        } else if (stepData.elementId === 'aide_nav') {
            // Positionner la description à droite du bouton "Aide"
            tutorialDescription.style.top = `${rect.top + window.scrollY}px`;
            tutorialDescription.style.left = `${rect.right + window.scrollX + 40}px`;
        } else if (stepData.alignTable) {
            // Positionner la description au-dessus des tableaux, centrée horizontalement par rapport au tableau
            tutorialDescription.style.top = `${rect.top + window.scrollY - 60}px`;
            tutorialDescription.style.left = `${rect.left + window.scrollX + rect.width / 2 - tutorialDescription.offsetWidth / 2}px`;
        } else if (stepData.centerTop) {
            // Aligner le haut de "disabledOrdersContainer" au centre de l'écran
            const screenCenter = window.innerHeight / 2;
            const offsetTop = rect.top + window.scrollY;
            const offset = screenCenter - offsetTop;
            tutorialDescription.style.top = `${offset + window.scrollY}px`;
            tutorialDescription.style.left = `${rect.left + window.scrollX}px`;
        } else {
            // Positionner la description en dessous par défaut
            tutorialDescription.style.top = `${rect.bottom + window.scrollY + 15}px`;
            tutorialDescription.style.left = `${rect.left + window.scrollX}px`;
        }

        tutorialDescription.innerHTML = `
            <p>${stepData.text}</p>
            <button class="btn tutorial-${step === steps.length - 1 ? 'finish' : 'next'}-btn">${step === steps.length - 1 ? 'Terminer' : 'Suivant'}</button>
        `;
    }

    document.body.addEventListener("click", (event) => {
        if (event.target.classList.contains("tutorial-next-btn")) {
            validateBtn.style.opacity = "1";
            step++;
            showTutorial();
        } else if (event.target.classList.contains("tutorial-finish-btn")) {
            tutorialOverlay.remove();
            transparentShape.remove();
            tutorialDescription.remove();
            try {
                fetch('/didacticiel_completed', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ didacticielCompleted: true })
                }).then(response => {
                    if (response.ok) {
                        console.log('Didacticiel terminé avec succès');
                    } else {
                        console.error('Erreur lors de la mise à jour du statut du didacticiel');
                    }
                }).catch(error => {
                    console.error('Erreur lors de la requête didacticiel :', error);
                });
            } catch (error) {
                console.error('Erreur lors de la requête didacticiel :', error);
            }
            validateBtn.style.opacity = "0.6";
        }
    });

    showTutorial();
}
