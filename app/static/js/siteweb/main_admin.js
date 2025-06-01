document.addEventListener("DOMContentLoaded", async function () {
    console.log("Admin")
    const elevesConnectes = document.getElementById('elevesConnectes');
    const elevesValideVoeux = document.getElementById('elevesValideVoeux');
    const vosMessagesDemandes = document.getElementById('vosMessagesDemandes');
    const nombreClasses = document.getElementById('nombreClasses');
    const cards = document.querySelectorAll('.cardBox');
    const elevesNav = document.getElementById('eleves_nav');
    const toggle = document.querySelector('.toggle');
    const navigation = document.querySelector('.navigation');
    const main = document.querySelector('.main');
    const profSortable = document.getElementById('ProfSortable');
    const aide_nav = document.getElementById('aide_nav');
    const notification_nav = document.getElementById('notification_nav');
    const statistiques_nav = document.getElementById('statistiques_nav');
    const admin_nav = document.getElementById('admin_nav');
    const siteweb_nav = document.getElementById('siteweb_nav');
    const body = document.body;
    
    fetch('/get_theme', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.darkTheme === true) {
            body.classList.add("dark");
            localStorage.setItem("dark-theme", "enabled");
        } else {
            body.classList.remove("dark");
            localStorage.setItem("dark-theme", "disabled");
        }
    });
    async function fetchData() {
        try {
            const response = await fetch('/get_data', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            console.log("data recu : ", data);
            return data;
        } catch (error) {
            console.error('Erreur lors de la récupération des données:', error);
        }
    }

    async function initialize() {
        const data = await fetchData();
        console.log(data);
        console.log("Admin")
        if (data.professeur) {
            console.log("Admin")
            aide_nav.style.display = 'none';
            notification_nav.style.display = 'block';
            statistiques_nav.style.display = 'block';
            if(data.admin) {
                siteweb_nav.style.display = 'block';
                statistiques_nav.style.display = 'block';

            }
            //admin_nav.style.display = 'block';
            cards.forEach(card => card.style.display = 'grid');
            if (elevesNav) elevesNav.style.display = 'none';

            if (data.niveau_classe) {
                let niveauClasseArray = data.niveau_classe;
                if (typeof niveauClasseArray === 'string') {
                    try {
                        niveauClasseArray = JSON.parse(niveauClasseArray);
                    } catch (error) {
                        console.error('Erreur lors de la conversion de niveau_classe en tableau:', error);
                        return;
                    }
                }
            }

            if (elevesConnectes) elevesConnectes.textContent = data.eleve_online;
            if (elevesValideVoeux) elevesValideVoeux.textContent = data.eleve_choix_validees;
            if (vosMessagesDemandes) vosMessagesDemandes.textContent = data.identifiant_perdus;
            if (nombreClasses) nombreClasses.textContent = data.classes;
        } else {
            const tableVoeux = document.querySelectorAll('.details');
            tableVoeux.forEach(table => table.style.display = 'block');

            if (typeof data.voeux_etablissements === 'string') {
                try {
                    data.voeux_etablissements = JSON.parse(data.voeux_etablissements);
                } catch (error) {
                    console.error('Erreur lors de la conversion de voeux en tableau:', error);
                    return;
                }
            }
        }
    }

    initialize();
    // Toggle navigation
    toggle.addEventListener('click', () => {
        navigation.classList.toggle('active');
        main.classList.toggle('active');
    });

});


let previousState = {};

// Afficher une popup et sauvegarder l'état initial du switch
function showPopup(popupId, condition = true, inputElement = null) {
    if (condition) {
        if (inputElement) {
            // Sauvegarder l'état initial du switch
            previousState[popupId] = inputElement.checked;
        }
        document.getElementById(popupId).style.display = 'flex';
    }
}

// Fermer une popup et réinitialiser l'état du switch si nécessaire
function closePopup(popupId, inputElement = null) {
    const email_input_switch = document.getElementById("input-switch");
    const email = document.getElementById('emailInput').value;
    const maintenance_input_switch = document.getElementById("is_in_maintenance");
    const maintenance_message = document.getElementById('MaintenanceInput').value;
    document.getElementById(popupId).style.display = 'none';
    if(popupId === 'emailPopup' && email === "") {
        email_input_switch.checked = false;
    } else if (popupId === 'MaintenancePopup' && maintenance_message === "") {
        maintenance_input_switch.checked = false;
    }
    if (inputElement && previousState[popupId] !== undefined) {
        // Réinitialiser l'état du switch
        inputElement.checked = previousState[popupId];
    }
}

// Vérifier l'entrée pour la confirmation de suppression
function checkConfirmationInput() {
    const input = document.getElementById('confirmationInput').value;
    const confirmButton = document.getElementById('confirmDeleteBtn');
    confirmButton.disabled = input !== "Suppression";
}

// Action pour supprimer tous les élèves
function deleteAllStudents() {
    console.log("Tous les élèves ont été supprimés.");
    closePopup('deletePopup');
}

// Action pour envoyer un email
function sendEmail() {
    const email = document.getElementById('emailInput').value;
    if (email) {
        console.log(`Email envoyé à : ${email}`);
        closePopup('emailPopup');
        fetch('/update_email_on_validation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email , active: true})
        })
        .then(response => {
            if (response.ok) {
                console.log("Email mis à jour avec succès.");
            } else {
                console.error("Erreur lors de la mise à jour de l'email.");
            }
        })
        .catch(error => {
            console.error("Erreur réseau ou serveur :", error);
        });
    } else {
        alert("Veuillez renseigner une adresse email valide.");
    }
}

function saveMaintenance() {
    const msg = document.getElementById('MaintenanceInput').value;
    const level = document.getElementById('maintenanceLevel').value;
    if (msg) {
        console.log(`Maintenance envoyé au serveur: ${msg}, niveau: ${level}`);
        closePopup('MaintenancePopup');
        update_config(msg, level);
        window.location.reload();
    } else {
        alert("Veuillez renseigner un message valide.");
    }
}

document.addEventListener("DOMContentLoaded", function () {                 
    const input_canStudentAccess = document.getElementById("can_student_access");
    const input_canProfAccess = document.getElementById("can_prof_access");
    const input_canProfResetVoeux = document.getElementById("can_prof_reset_voeux");
    const input_canStudentValidate = document.getElementById("can_student_validate");
    const want_email_switch = document.getElementById("want_email_switch");
    const input_MaintenanceInput = document.getElementById("is_in_maintenance");

    console.log(input_MaintenanceInput)

    input_canStudentAccess.checked = canStudentAccess === "true" ? true : false;
    input_canProfAccess.checked = canProfAccess === "true" ? true : false;
    input_canProfResetVoeux.checked = canProfResetVoeux === "true" ? true : false;
    input_canStudentValidate.checked = canStudentValidate === "true" ? true : false;
    want_email_switch.checked = want_email === "true" ? true : false;
    input_MaintenanceInput.checked = isInMaintenanceVar === "true" ? true : false;

    if (want_email === "true") {
        const emailInput = document.getElementById("emailInput");
        if (emailInput) {
            emailInput.value = email;
        }
    }
    
});

// Ajouter un écouteur pour détecter les changements sur les cases à cocher
function handleCheckboxChange(event) {
    const checkbox = event.target;
    const checkboxId = checkbox.id;
    const isChecked = checkbox.checked;

    console.log(`La valeur de ${checkboxId} a changé : ${isChecked}`);

    // Effectuer une action spécifique en fonction de la case à cocher modifiée
    switch (checkboxId) {
        case "can_student_access":
            console.log("Modification de l'accès des élèves.");
            update_config();
            break;
        case "can_prof_access":
            console.log("Modification de l'accès des professeurs.");
            update_config();
            break;
        case "can_prof_reset_voeux":
            console.log("Modification de la réinitialisation des vœux par les professeurs.");
            update_config();
            break;
        case "can_student_validate":
            console.log("Modification de la validation des vœux par les élèves.");
            update_config();
            break;
        case "want_email_switch":
            console.log("Modification de l'activation de l'email.");
            const emailInput = document.getElementById("emailInput");
            if (isChecked) {
                showPopup('emailPopup', true, checkbox);
            } else {
                closePopup('emailPopup', checkbox);
                fetch('/update_email_on_validation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email: "", active: false })
                })
                .then(response => {
                    if (response.ok) {
                        console.log("Email désactivé avec succès.");
                    } else {
                        console.error("Erreur lors de la désactivation de l'email.");
                    }
                })
                .catch(error => {
                    console.error("Erreur réseau ou serveur :", error);
                });
            }
            break;
        case "is_in_maintenance":
            console.log("Modification de l'état de maintenance.");
            if (!isChecked) {
                update_config("");
                window.location.reload();
            }
            break;
        default:
            console.log("Changement détecté sur une case inconnue.");
    }
}

// Fonction pour mettre à jour la configuration
async function update_config(msg = undefined) {
    console.log("Mise à jour de la configuration...");
    const canStudentAccess = document.getElementById("can_student_access").checked;
    const canProfAccess = document.getElementById("can_prof_access").checked;
    const canProfResetVoeux = document.getElementById("can_prof_reset_voeux").checked;
    const canStudentValidate = document.getElementById("can_student_validate").checked;
    const isInMaintenance_box = document.getElementById("is_in_maintenance").checked;
    const maintenance_message = msg;
    console.log("message de maintenance : ", maintenance_message);

    var maintenance_level = document.getElementById('maintenanceLevel').value;
    console.log("Niveau de maintenance : ", maintenance_level);
    if (!isInMaintenance_box) {
        maintenance_level = "none";
    }
    const config = {
        can_student_access: canStudentAccess,
        can_prof_access: canProfAccess,
        can_prof_reset_voeux: canProfResetVoeux,
        can_student_validate: canStudentValidate,
        is_in_maintenance: isInMaintenance_box,
        maintenance_message: maintenance_message,
        maintenance_level: maintenance_level,
    };
    try {
        const response = await fetch('/update_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            console.log("Configuration mise à jour avec succès.");
        } else {
            console.error("Erreur lors de la mise à jour de la configuration.");
        }
    } catch (error) {
        console.error("Erreur réseau ou serveur :", error);
    }
}

// Ajouter les écouteurs sur les cases à cocher
document.addEventListener("DOMContentLoaded", function () {
    const checkboxes = [
        document.getElementById("can_student_access"),
        document.getElementById("can_prof_access"),
        document.getElementById("can_prof_reset_voeux"),
        document.getElementById("can_student_validate"),
        document.getElementById("want_email_switch"),
        document.getElementById("saveMaintenance"),
        document.getElementById("is_in_maintenance"),
    ];

    checkboxes.forEach(checkbox => {
        if (checkbox) {
            checkbox.addEventListener("change", handleCheckboxChange);
        }
    });
});

function toggleAction(input) {
    if (input.checked) {
        console.log("Action activée");
    } else {
        console.log("Action désactivée");
    }
}

function toggleActionBtn(button) {

    if (button.textContent === "Activer") {
        button.textContent = "Désactiver";
        button.classList.add("active");
    } else {
        button.textContent = "Activer";
        button.classList.remove("active");
    }
}


document.addEventListener('DOMContentLoaded', function () {
    const socket = io({
        reconnection: true,              // ✅ autorise la reconnexion automatique
        reconnectionAttempts: 5,         // ✅ nombre de tentatives
        reconnectionDelay: 1000,         // ✅ délai entre chaque tentative
        autoConnect: true,               // se connecte automatiquement
    });

    // Récupérer le cookie session_cookie
    const sessionCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('session_cookie='))
        ?.split('=')[1];

    if (sessionCookie) {
        console.log('Envoi du cookie session_cookie au serveur WebSocket');

        // Lorsque la connexion WebSocket est prête
        socket.on('connect', () => {
            socket.emit('join', { session_cookie: sessionCookie });
        });

    } else {
        console.warn("Aucun cookie 'session_cookie' trouvé");
    }

    // Écouter les messages du serveur
    socket.on('message', function (data) {
        console.log('Message reçu:', data);
        if (data.total_online_students !== undefined) {
            const elevesConnectes = document.getElementById('elevesConnectes');
            if (elevesConnectes) {
                elevesConnectes.textContent = data.total_online_students;
            }
        }
    });

    // Détecter la déconnexion
    socket.on('disconnect', function () {
        console.log('Déconnecté du serveur WebSocket');
    });


});