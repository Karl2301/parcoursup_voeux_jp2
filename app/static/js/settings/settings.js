
document.addEventListener("DOMContentLoaded", function () {
    let list = document.querySelectorAll(".navigation li");

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

    

    const checkbox = document.getElementById("checkbox");
    const body = document.body;

    function updateTheme() {
        if (localStorage.getItem("dark-theme") === "enabled") {
            body.classList.add("dark");
            checkbox.checked = true;
        } else {
            body.classList.remove("dark");
            checkbox.checked = false;
        }

        fetch('/update-theme', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({ darkTheme: checkbox.checked })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }


    checkbox.addEventListener("change", function () {
        if (checkbox.checked) {
            localStorage.setItem("dark-theme", "enabled");
        } else {
            localStorage.setItem("dark-theme", "disabled");
        }
        updateTheme();
    });

    updateTheme();
});

// Menu Toggle
let toggle = document.querySelector(".toggle");
let navigation = document.querySelector(".navigation");
let main = document.querySelector(".main");
const aide_nav = document.getElementById('aide_nav');
const statistiques_nav = document.getElementById('statistiques_nav');
const siteweb_nav = document.getElementById('siteweb_nav');
const card_email = document.getElementById('card_email');
const input_email = document.getElementById('emailNotificationCheckbox');
const text_email_emailInput = document.getElementById('emailInput');

toggle.onclick = function () {
  navigation.classList.toggle("active");
  main.classList.toggle("active");
};

function updateRowNumbers() {
  const rows = document.querySelectorAll('#sortable tr');
  rows.forEach((row, index) => {
    const rowNumberElement = row.querySelector('.row-number');
    if (rowNumberElement) {
      rowNumberElement.textContent = index + 1;
    } else {
      console.error('Element with class "row-number" not found in row:', row);
    }
  });
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
        if(data.admin)  {
            statistiques_nav.style.display = 'block';
            siteweb_nav.style.display = 'block';
        }
        aide_nav.style.display = 'none';
        card_email.style.display = 'flex';

        if (data.want_email) {
            console.log("L'utilisateur a déjà un email enregistré");
            input_email.checked = true;
            text_email_emailInput.value = data.email;
        }

        const elevesNav = document.getElementById('eleves_nav');
        if (elevesNav) {
            elevesNav.style.display = 'none';
        }

        const notificationNav = document.getElementById('notification_nav');
        if (notificationNav) {
            notificationNav.style.display = 'block';
        }

        const change_username = document.getElementById('change_username');
        if (change_username) {
            change_username.style.display = 'flex';
            console.log("change_username")
        }else {
            console.log("change_username not found")
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
  }
);  


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


function handleEmailNotificationToggle() {
    const checkbox = document.getElementById('emailNotificationCheckbox');
    const popup = document.getElementById('emailPopup');

    if (checkbox.checked) {
        popup.style.display = 'flex';
    } else {
        // Si l'utilisateur décoche la case, envoyer une requête pour désactiver les notifications
        fetch('/update_email_on_validation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: '', active: false }),
        })
        .then(response => {
            if (response.ok) {
                console.log('Notification désactivée avec succès !');
            } else {
                alert('Une erreur est survenue.');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('Une erreur est survenue.');
        });
    }
}

function closePopup(popupId) {
    const popup = document.getElementById(popupId);
    const checkbox = document.getElementById('emailNotificationCheckbox');

    popup.style.display = 'none';
    checkbox.checked = false; // Désactiver la checkbox si l'utilisateur annule
}

function sendEmail() {
    const emailInput = document.getElementById('emailInput').value;
    const popup = document.getElementById('emailPopup');

    if (emailInput) {
        // Envoyer une requête POST avec l'email
        fetch('/update_email_on_validation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email: emailInput , active: true }),
        })
        .then(response => {
            if (response.ok) {
                alert('Notification activée avec succès !');
            } else {
                alert('Une erreur est survenue.');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('Une erreur est survenue.');
        });

        popup.style.display = 'none';
    } else {
        alert('Veuillez entrer un email valide.');
    }
}


window.onload = fetchVoeux;