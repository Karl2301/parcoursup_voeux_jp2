// add hovered class to selected list item
let list = document.querySelectorAll(".navigation li");
const aide_nav = document.getElementById('aide_nav');
const statistiques_nav = document.getElementById('statistiques_nav');
const siteweb_nav = document.getElementById('siteweb_nav');
const froceValidation = document.getElementById('ValidateBtnAll');

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
    console.log(data);
    let voeux = data.voeux_etablissements;

    if (data.professeur) {
        aide_nav.style.display = 'none';
        const cards = document.querySelectorAll('.cardBox');
        cards.forEach(card => {
            card.style.display = 'grid';
        });
        
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

        // --- Création d'un conteneur en ligne pour afficher chaque classe ---
        if (data.niveau_classe) {
            let niveauClasseArray = data.niveau_classe;
            // Si la donnée est une chaîne JSON, la convertir en tableau
            if (typeof niveauClasseArray === 'string') {
                try {
                    niveauClasseArray = JSON.parse(niveauClasseArray);
                } catch (error) {
                    console.error('Erreur lors de la conversion de niveau_classe en tableau:', error);
                    return;
                }
            }
            if (Array.isArray(niveauClasseArray)) {
                // Créer un conteneur pour les cartes (classes) qui s'afficheront en ligne
                const cardContainer = document.createElement('div');
                cardContainer.classList.add('cardContainer'); // Ce conteneur sera mis en forme en ligne via le CSS

                // Pour chaque valeur de niveau_classe, créer une carte
                niveauClasseArray.forEach(classe => {
                    const card = document.createElement('div');
                    card.classList.add('cardBox'); 
                    card.innerHTML = `
                        <a href="/classes/${classe}" class="card-link" style="text-decoration: none;">
                            <div class="card">
                                <div>
                                    <div class="numbers">${classe}</div>
                                    <div class="cardName">Classe</div>
                                </div>
                                <div class="iconBx">
                                    <!-- inutile je pense -->
                                </div>
                            </div>
                        </a>
                    `;
                    cardContainer.appendChild(card);
                });
            } else {
                console.error('niveau_classe n\'est pas un tableau:', niveauClasseArray);
            }
        }

        // Mise à jour des statistiques pour le professeur
        const elevesConnectes = document.getElementById('elevesConnectes');
        const elevesValideVoeux = document.getElementById('elevesValideVoeux');
        const nombreClasses = document.getElementById('nombreClasses');

        if (elevesConnectes) {
            elevesConnectes.textContent = data.eleve_online;
        }
        if (elevesValideVoeux) {
            elevesValideVoeux.textContent = data.eleve_choix_validees;
        }
        if (nombreClasses) {
            nombreClasses.textContent = data.classes;
        }
        console.log("Professeur");
    } else {
        // Pour l'élève : afficher le tableau des vœux
        const tableVoeux = document.querySelectorAll('.details');
        tableVoeux.forEach(table => {
            table.style.display = 'block';
        });

        console.log("Elève");
        console.log('Type of voeux:', typeof voeux);
        console.log('Content of voeux:', voeux);

        // Convertir la chaîne JSON en tableau si nécessaire
        if (typeof voeux === 'string') {
            try {
                voeux = JSON.parse(voeux);
            } catch (error) {
                console.error('Erreur lors de la conversion de voeux en tableau:', error);
                return;
            }
        }

        if (Array.isArray(voeux)) {
            const tbody = document.getElementById('sortable');
            if (!tbody) {
                console.error('Element with id "sortable" not found.');
                return;
            }
            voeux.forEach((item, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="row-number">${index + 1}</td>
                    <td>${item.school}</td>
                    <td>${item.city}</td>
                    <td>${item.degree}</td>
                    <td>${item.specialization}</td>
                `;
                tbody.appendChild(row);
            });
            updateRowNumbers(); // Mise à jour des numéros de ligne
        } else {
            console.error('voeux_etablissements is not an array:', voeux);
        }
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
window.onload = async function() {
    await fetchVoeux();
}


document.addEventListener("DOMContentLoaded", function () {
    const selectAllCheckbox = document.getElementById('selectAll');
    const rowCheckboxes = document.querySelectorAll('.selectRow');
    const downloadBtn = document.getElementById('downloadBtn');
    const downloadMenu = document.getElementById('dropdownMenu');
    const downloadCsv = document.getElementById('downloadCsv');
    const downloadXls = document.getElementById('downloadXls');
    const downloadPdf = document.getElementById('downloadPdf');

    froceValidation.addEventListener('click', async function () {
        try {
            const response = await fetch('/force_validate_voeux', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ "force": true })
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Validation réussie:', result);
                alert('Validation réussie pour les élèves sélectionnés.');
            } else {
                console.error('Erreur lors de la validation:', response.statusText);
                alert('Erreur lors de la validation.');
            }
        } catch (error) {
            console.error('Erreur réseau:', error);
            alert('Erreur réseau lors de la validation.');
        }
    }
    );
        downloadBtn.addEventListener('click', function () {
      downloadMenu.style.display = downloadMenu.style.display === 'none' ? 'block' : 'none';
    });
  
    selectAllCheckbox.addEventListener('change', function () {
      rowCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
      });
      toggleDownloadButton();
    });
  
    rowCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', toggleDownloadButton);
    });
  
    function toggleDownloadButton() {
      const anyChecked = Array.from(rowCheckboxes).some(checkbox => checkbox.checked);
      downloadBtn.style.display = anyChecked ? 'block' : 'none';
        if (!anyChecked) {
            downloadMenu.style.display = 'none'; // Hide the dropdown menu when no checkboxes are checked
        }
    }
  
    async function downloadVoeux(format) {
      const selectedIds = Array.from(rowCheckboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.closest('tr').querySelector('td:nth-child(2)').textContent);
  
      const response = await fetch(`/download_voeux_users_classe?format=${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ selected_ids: selectedIds })
      });
  
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `voeux_eleves.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        console.error('Failed to download file');
      }
    }
  
  
    downloadXls.addEventListener('click', function () {
      downloadVoeux('xlsx');
    });
  
    downloadPdf.addEventListener('click', function () {
      downloadVoeux('pdf');
    });

  });
