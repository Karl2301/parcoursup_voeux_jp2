document.addEventListener("DOMContentLoaded", async function () {
    const elevesConnectes = document.getElementById('elevesConnectes');
    const elevesValideVoeux = document.getElementById('elevesValideVoeux');
    const vosMessagesDemandes = document.getElementById('vosMessagesDemandes');
    const nombreClasses = document.getElementById('nombreClasses');
    const cards = document.querySelectorAll('.cardBox');
    const elevesNav = document.getElementById('eleves_nav');
    const notificationNav = document.getElementById('notification_nav');
    const toggle = document.querySelector('.toggle');
    const navigation = document.querySelector('.navigation');
    const main = document.querySelector('.main');
    const aide_nav = document.getElementById('aide_nav');
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
        
        if (data.professeur) {
            aide_nav.style.display = 'none';
            cards.forEach(card => card.style.display = 'grid');
            if (elevesNav) elevesNav.style.display = 'none';
            if (notificationNav) notificationNav.style.display = 'block';

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
                    const cardContainer = document.createElement('div');
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
                    const hr = document.querySelector('.barre-separatrice');
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
    }

    initialize();
    // Toggle navigation
    toggle.addEventListener('click', () => {
        navigation.classList.toggle('active');
        main.classList.toggle('active');
    });
});




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