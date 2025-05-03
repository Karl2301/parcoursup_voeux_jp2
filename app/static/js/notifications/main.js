// add hovered class to selected list item
let list = document.querySelectorAll(".navigation li");
const aide_nav = document.getElementById('aide_nav');
const notification_nav = document.getElementById('notification_nav');
const elevesNav = document.getElementById('eleves_nav');
const statistiques_nav = document.getElementById('statistiques_nav');
const siteweb_nav = document.getElementById('siteweb_nav');


function activeLink() {
  list.forEach((item) => {
    item.classList.remove("hovered");
  });
  this.classList.add("hovered");
}

list.forEach((item) => item.addEventListener("mouseover", activeLink));

// Menu Toggle
let toggle = document.querySelector(".toggle");
let navigation = document.querySelector(".navigation");
let main = document.querySelector(".main");

toggle.onclick = function () {
  navigation.classList.toggle("active");
  main.classList.toggle("active");
};

function getUpdatedData() {
    // Récupérer les données mises à jour depuis le DOM
    const rows = document.querySelectorAll('#sortable tr');
    const updatedData = [];
    rows.forEach(row => {
        const rowNumber = row.querySelector('td:nth-child(1)').textContent;
        const school = row.querySelector('td:nth-child(2)').textContent;
        const city = row.querySelector('td:nth-child(3)').textContent;
        const degree = row.querySelector('td:nth-child(4)').textContent;
        const specialization = row.querySelector('td:nth-child(5)').textContent;
        updatedData.push({ row_number: parseInt(rowNumber), school, city, degree, specialization });
    });
    return updatedData;
}


async function fetchVoeux() {
    const response = await fetch('/get_data', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    const data = await response.json();
    console.log(data)
    let voeux = data.voeux_etablissements;

    // Vérifier si l'utilisateur est un élève
    if (data.professeur) {
        aide_nav.style.display = 'none';
        if(data.admin)  {
            statistiques_nav.style.display = 'block';
            siteweb_nav.style.display = 'block';
        }
        const elevesNav = document.getElementById('eleves_nav');
        if (elevesNav) {
            elevesNav.style.display = 'none';
        }

        const notificationNav = document.getElementById('notification_nav');
        if (notificationNav) {
            notificationNav.style.display = 'block';
        }

    }

    if(!data.professeur) {
        console.log("Eleve")
    } else {
        console.log("Professeur")
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const body = document.body;
    const dashboardTheme = body.getAttribute("data-theme");

    if (dashboardTheme === "1") {
        body.classList.add("dark");  // Applique le mode sombre
    } else {
        body.classList.remove("dark");  // Applique le mode clair
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const body = document.body;
    const recentOrdersContainer = document.getElementById('recentOrdersContainer');
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
            if (recentOrdersContainer) {
                recentOrdersContainer.style.backgroundColor = "#333333";
            }
            body.style.color = "white"; // Set text color to white
        } else {
            body.classList.remove("dark");
            localStorage.setItem("dark-theme", "disabled");
            if (recentOrdersContainer) {
                recentOrdersContainer.style.backgroundColor = "";
            }
            body.style.color = ""; // Reset text color
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    // Gestionnaire d'événements pour les boutons de suppression
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', async function () {
            const row = this.closest('tr');
            const id = row.getAttribute('data-id');

            // Suppression de la ligne du DOM
            row.remove();

            // Envoi de la requête de suppression au serveur
            await fetch(`/delete_demande/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        });
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

    // Détecter la déconnexion
    socket.on('disconnect', function () {
        console.log('Déconnecté du serveur WebSocket');
    });
});

window.onload = fetchVoeux;