// add hovered class to selected list item
let list = document.querySelectorAll(".navigation li");
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
const aide_nav = document.getElementById('aide_nav');

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
    const elevesConnectes = document.getElementById('elevesConnectes');
    const elevesValideVoeux = document.getElementById('elevesValideVoeux');
    const vosMessagesDemandes = document.getElementById('vosMessagesDemandes');
    const nombreClasses = document.getElementById('nombreClasses');

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
            siteweb_nav.style.display = 'block';
            statistiques_nav.style.display = 'block';
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

    if (elevesConnectes) elevesConnectes.textContent = data.eleve_online;
    if (elevesValideVoeux) elevesValideVoeux.textContent = data.eleve_choix_validees;
    if (vosMessagesDemandes) vosMessagesDemandes.textContent = data.identifiant_perdus;
    if (nombreClasses) nombreClasses.textContent = data.classes;
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

document.addEventListener('DOMContentLoaded', function() {
    const resetBtn = document.getElementById('resetPasswordBtn');
    const popup = document.getElementById('resetPasswordPopup');
    const overlay = document.getElementById('popup-overlay-eleve');
    const confirmBtn = document.getElementById('confirmResetBtn');
    const cancelBtn = document.getElementById('cancelResetBtn');
    const notification = document.getElementById('successNotification');
    const reset_voeux = document.getElementById('resetValidateVoeux');

    function showPopup() {
        popup.style.display = 'flex';
        overlay.style.display = 'block';
    }

    function hidePopup() {
        popup.style.display = 'none';
        overlay.style.display = 'none';
    }

    function showNotification() {
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 3000);
    }

    async function handleReset() {
        const identifiant = document.querySelector('.card p').textContent.trim();
        try {
            const response = await fetch(`/reset_password/${identifiant}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            if (response.ok && data.success) {
                hidePopup();
                showNotification();
            } else {
                throw new Error(data.error || 'Erreur lors de la réinitialisation');
            }
        } catch (error) {
            console.error('Erreur:', error);
            hidePopup();
            alert('Une erreur est survenue lors de la réinitialisation du mot de passe.');
        }
    }

    async function reset_voeux_validation() {
        const identifiant = document.querySelector('.card p').textContent.trim();
        fetch('/reset_voeux_validation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({user_to_reset: identifiant})
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.success) {
                reset_voeux.style.display = 'none';
                alert('Voeux réinitialisés avec succès.');
                
            } else {
                throw new Error(data.error || 'Erreur lors de la réinitialisation');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            hidePopup();
            alert('Une erreur est survenue lors de la réinitialisation des voeux.');
        });
    }

    resetBtn.addEventListener('click', showPopup);
    confirmBtn.addEventListener('click', handleReset);
    cancelBtn.addEventListener('click', hidePopup);
    overlay.addEventListener('click', hidePopup);
    reset_voeux.addEventListener('click', reset_voeux_validation);
});


window.onload = fetchVoeux;


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