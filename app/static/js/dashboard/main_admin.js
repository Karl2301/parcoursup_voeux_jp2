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
    const body = document.body;
    const siteweb_nav = document.getElementById('siteweb_nav');
    
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

    async function showPopup(profId = null) {
        // Fermer l'autre popup si elle est ouverte
        document.getElementById('addProfPopup').style.display = 'none';

        if (profId) {
            try {
                const response = await fetch(`/get_prof_data?id=${profId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                const profData = await response.json();
                console.log("Prof data:", profData); // Log the data to check if it's correct
                fillPopup(profData);
            } catch (error) {
                console.error('Erreur lors de la récupération des données du professeur:', error);
            }
        } else {
            // Clear the popup for adding a new professor
            document.getElementById('new_identifiant').value = '';
            document.getElementById('new_prenom').value = '';
            document.getElementById('new_nom').value = '';

            const niveauClasseDiv = document.getElementById('new_niveau_classe');
            niveauClasseDiv.innerHTML = ''; // Clear existing checkboxes
            const data = await fetchData();
            const classes = JSON.parse(data.niveau_classe); // Static list of classes
            classes.forEach(classe => {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = classe;
                checkbox.id = `new_classe_${classe}`;

                const label = document.createElement('label');
                label.htmlFor = `new_classe_${classe}`;
                label.textContent = classe;

                const div = document.createElement('div');
                div.appendChild(checkbox);
                div.appendChild(label);

                niveauClasseDiv.appendChild(div);
            });
            document.getElementById('addProfPopup').style.display = 'flex';
        }
    }

    function fillPopup(profData) {
        // Fermer l'autre popup si elle est ouverte
        document.getElementById('addProfPopup').style.display = 'none';
        document.getElementById('identifiant_unique').textContent = profData.identifiant_unique;
        document.getElementById('prenom').value = profData.prenom || '';
        document.getElementById('nom').value = profData.nom || '';
        editClassesAffiliation = document.getElementById('editClassesAffiliation')
        
        const niveauClasseDiv = document.getElementById('niveau_classe');
        niveauClasseDiv.innerHTML = ''; // Clear existing checkboxes
        profData.classe_available.forEach(classe => {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = classe;
            checkbox.id = `classe_${classe}`;
            checkbox.checked = profData.niveau_classe.includes(classe);

            const label = document.createElement('label');
            label.htmlFor = `classe_${classe}`;
            label.textContent = classe;

            const div = document.createElement('div');
            div.appendChild(checkbox);
            div.appendChild(label);

            niveauClasseDiv.appendChild(div);
        });
        if (profData.admin) {
            editClassesAffiliation.style.display = 'none'; // Hide the classes affiliation for admin
        }
        document.getElementById('is_admin').checked = profData.admin || false; // Checkbox for admin
        document.getElementById('profPopup').style.display = 'flex';
    }

    async function saveProfData(event) {
        event.preventDefault();
        const profId = document.getElementById('identifiant_unique').textContent;
        const prenom = document.getElementById('prenom').value;
        const nom = document.getElementById('nom').value;
        const admin = document.getElementById('is_admin').checked; // Checkbox for admin
        const niveau_classe = Array.from(document.querySelectorAll('#niveau_classe input[type="checkbox"]:checked')).map(checkbox => checkbox.value);

        const profData = {
            identifiant_unique: profId,
            prenom,
            nom,
            admin,
            niveau_classe
        };

        try {
            const response = await fetch('/save_prof_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profData)
            });

            if (response.ok) {
                alert('Données enregistrées avec succès');
                document.getElementById('profPopup').style.display = 'none';
                location.reload(); // Recharger la page pour voir les changements
            } else {
                alert('Erreur lors de l\'enregistrement des données');
            }
        } catch (error) {
            console.error('Erreur lors de l\'enregistrement des données:', error);
        }
    }

    async function saveNewProfData(event) {
        event.preventDefault();
        const identifiant = document.getElementById('new_identifiant').value;
        const prenom = document.getElementById('new_prenom').value;
        const nom = document.getElementById('new_nom').value;
        const admin = document.getElementById('new_is_admin').checked; // Checkbox for admin
        const deja_connecte = false; // Nouveau professeur n'est pas déjà connecté
        const niveau_classe = Array.from(document.querySelectorAll('#new_niveau_classe input[type="checkbox"]:checked')).map(checkbox => checkbox.value);

        const profData = {
            identifiant_unique: identifiant,
            prenom,
            nom,
            deja_connecte,
            niveau_classe,
            admin
        };

        try {
            const response = await fetch('/save_prof_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profData)
            });

            if (response.ok) {
                alert('Nouveau professeur ajouté avec succès');
                document.getElementById('addProfPopup').style.display = 'none';
                location.reload(); // Recharger la page pour voir les changements
            } else {
                alert('Erreur lors de l\'ajout du nouveau professeur');
            }
        } catch (error) {
            console.error('Erreur lors de l\'ajout du nouveau professeur:', error);
        }
    }

    document.getElementById('professeurForm').addEventListener('submit', saveProfData);
    document.getElementById('addProfForm').addEventListener('submit', saveNewProfData);

    async function initialize() {
        const data = await fetchData();
        console.log(data);
        console.log("Admin")
        if (data.professeur) {
            console.log("Admin")
            aide_nav.style.display = 'none';
            notification_nav.style.display = 'block';
            statistiques_nav.style.display = 'block';
            siteweb_nav.style.display = 'block';
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
                if (Array.isArray(niveauClasseArray)) {
                    const cardContainer = document.getElementById('listeclasses');
                    cardContainer.classList.add('cardContainer');
                    niveauClasseArray.forEach(classe => {
                        const card = document.createElement('div');
                        card.classList.add('cardBox');
                        card.innerHTML = `
                            <a href="/classe/${classe}" class="card-link" style="text-decoration: none;">
                                <div class="card">
                                    <div>
                                        <div class="numbers">${classe}</div>
                                        <div class="cardName">Classe</div>
                                    </div>
                                    <div class="iconBx"></div>
                                </div>
                            </a>
                        `;
                        cardContainer.appendChild(card);
                    });
                    const hr = document.querySelector('.liste_classe_class');
                    if (hr) {
                        hr.insertAdjacentElement('afterend', cardContainer);
                    } else {
                        console.error('La barre séparatrice n\'a pas été trouvée.');
                    }
                } else {
                    console.error('niveau_classe n\'est pas un tableau:', niveauClasseArray);
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

        if (data.liste_prof) {
            populateProfTable(data.liste_prof);
        }
    }

    function populateProfTable(profList) {
        // Trier les professeurs : les administrateurs en premier
        const sortedProfList = profList.sort((a, b) => b.admin - a.admin);

        sortedProfList.forEach(prof => {
            const row = document.createElement('tr');
            console.log("Prof : ", prof.admin);
            row.innerHTML = `
            <td>${prof.identifiant_unique}</td>
            <td>${prof.prenom || ''} ${prof.nom || ''}</td>
            <td>${prof.classes.join(', ')}</td>
            <td>
                ${prof.admin ? '<span class="status pending">Administrateur</span>' : '<span class="status inProgress">Professeur</span>'}
            </td>
            <td>
                <button class="btn btn-modifier" data-id="${prof.identifiant_unique}">Modifier</button>
                <button class="btn btn-reset" data-id="${prof.identifiant_unique}">Réinitialiser</button>
                <button class="btn btn-supprimer" data-id="${prof.identifiant_unique}">Supprimer</button>
            </td>
            `;
            profSortable.appendChild(row);
        });
        
        const resetButtons = document.querySelectorAll('.btn-reset');
        resetButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const profId = event.target.getAttribute('data-id');
                showResetPopup(profId);
            });
        });

        // Ajouter des gestionnaires d'événements pour les boutons "Modifier"
        const modifierButtons = document.querySelectorAll('.btn-modifier');
        modifierButtons.forEach(button => {
            button.addEventListener('click', async (event) => {
                const profId = event.target.getAttribute('data-id');
                await showPopup(profId);
            });
        });

        // Ajouter des gestionnaires d'événements pour les boutons "Supprimer"
        const supprimerButtons = document.querySelectorAll('.btn-supprimer');
        supprimerButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const profId = event.target.getAttribute('data-id');
                showDeletePopup(profId);
            });
        });
    }

    function showDeletePopup(profId) {
        const deletePopup = document.getElementById('deleteProfPopup');
        deletePopup.style.display = 'flex';
        document.getElementById('confirmDeleteBtn').setAttribute('data-id', profId);
    }

    async function deleteProf(event) {
        const profId = event.target.getAttribute('data-id');

        try {
            const response = await fetch('/delete_prof', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ identifiant_unique: profId })
            });

            if (response.ok) {
                document.getElementById('deleteProfPopup').style.display = 'none';
                location.reload(); // Recharger la page pour voir les changements
            } else {
                alert('Erreur lors de la suppression du professeur');
            }
        } catch (error) {
            console.error('Erreur lors de la suppression du professeur:', error);
        }
    }

    function showResetPopup(profId) {
        const resetPopup = document.getElementById('resetPasswordPopup');
        resetPopup.style.display = 'flex';
        document.getElementById('confirmResetBtn').setAttribute('data-id', profId);
    }
    
    // Gestionnaire pour confirmer la réinitialisation
    document.getElementById('confirmResetBtn').addEventListener('click', async (event) => {
        const profId = event.target.getAttribute('data-id');
        try {
            const response = await fetch('/admin_reset_password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ identifiant_unique: profId })
            });
    
            if (response.ok) {
                alert('Mot de passe réinitialisé avec succès.');
                document.getElementById('resetPasswordPopup').style.display = 'none';
            } else {
                alert('Erreur lors de la réinitialisation du mot de passe.');
            }
        } catch (error) {
            console.error('Erreur lors de la réinitialisation du mot de passe:', error);
        }
    });
    
    // Gestionnaire pour annuler la réinitialisation
    document.getElementById('cancelResetBtn').addEventListener('click', () => {
        document.getElementById('resetPasswordPopup').style.display = 'none';
    });

    initialize();
    // Toggle navigation
    toggle.addEventListener('click', () => {
        navigation.classList.toggle('active');
        main.classList.toggle('active');
    });

    document.getElementById('confirmDeleteBtn').addEventListener('click', deleteProf);
    document.getElementById('cancelDeleteBtn').addEventListener('click', () => {
        document.getElementById('deleteProfPopup').style.display = 'none';
    });

    document.getElementById('NewProf').addEventListener('click', () => {
        // Fermer l'autre popup si elle est ouverte
        document.getElementById('profPopup').style.display = 'none';
        showPopup();
    });

    document.getElementById('cancelBtn').addEventListener('click', () => {
        document.getElementById('profPopup').style.display = 'none';
    });

    document.getElementById('cancelAddBtn').addEventListener('click', () => {
        document.getElementById('addProfPopup').style.display = 'none';
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'fr', // Définir la langue française
        selectable: true,
        dateClick: function(info) {
            var dateStr = formatDate(info.date);
            var deadlineInput = document.getElementById('deadline');
            deadlineInput.value = dateStr;

            fetch('/set_deadline', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ deadline: dateStr })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Date limite enregistrée : ' + dateStr);
                } else {
                    alert('Erreur lors de l\'enregistrement de la date limite.');
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Erreur lors de l\'enregistrement de la date limite.');
            });
        }
    });
});

function formatDate(date) {
    var year = date.getFullYear();
    var month = ('0' + (date.getMonth() + 1)).slice(-2);
    var day = ('0' + date.getDate()).slice(-2);
    var hours = '23';
    var minutes = '59';
    return `${year}-${month}-${day}T${hours}:${minutes}`;
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

    // ❌ Ne pas forcer la déconnexion ici (sinon ça casse la reconnexion)
    /*
    window.addEventListener('beforeunload', function () {
        console.log('Fermeture de la fenêtre détectée, déconnexion...');
        socket.disconnect();
    });
    */
});
