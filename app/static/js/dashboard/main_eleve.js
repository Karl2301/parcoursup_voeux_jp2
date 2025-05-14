document.addEventListener("DOMContentLoaded", async function () {
    const validateBtn = document.getElementById('validateBtn');
    const modifyBtn = document.getElementById('modifyBtn');
    const downloadMenu = document.getElementById('downloadMenu');
    const downloadBtn = document.getElementById('downloadBtn');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const downloadXls = document.getElementById('downloadXls');
    const downloadPdf = document.getElementById('downloadPdf');
    const confirmationMessage = document.getElementById('confirmationMessage');
    const popup = document.getElementById('popup');
    const cancelBtn = document.getElementById('cancelBtn');
    const confirmBtn = document.getElementById('confirmBtn');
    const recentOrdersContainer = document.getElementById('recentOrdersContainer');
    const editModeMessage = document.getElementById('editModeMessage');
    const tbody = document.getElementById('sortable');
    const disabledTbody = document.getElementById('disabledSortable');
    const editModeMessageUnclassed = document.getElementById('editModeMessageUnclassed');
    const noVoeuxMessage = document.getElementById('noVoeuxMessage');
    const toggle = document.querySelector('.toggle');
    const navigation = document.querySelector('.navigation');
    const main = document.querySelector('.main');
    const body = document.body;

    let isEditMode = false;

    let sortOrder = {
        number: true,
        name: true,
        city: true,
        type: true,
        specialty: true
    };

    function sortTableByColumn(tbodyId, columnIndex, isNumeric = false, order = true) {
        const tbody = document.getElementById(tbodyId);
        const rows = Array.from(tbody.getElementsByTagName('tr'));
        if (rows.length === 0) return;
    
        rows.sort((a, b) => {
            const cellA = a.cells[columnIndex] ? a.cells[columnIndex].innerText.toLowerCase() : '';
            const cellB = b.cells[columnIndex] ? b.cells[columnIndex].innerText.toLowerCase() : '';
    
            if (isNumeric) {
                return order ? cellA - cellB : cellB - cellA;
            } else {
                return order ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            }
        });
    
        rows.forEach(row => tbody.appendChild(row));
    }

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

    function updateRowNumbers() {
        const rows = document.querySelectorAll('#sortable tr');
        rows.forEach((row, index) => {
            const rowNumberElement = row.querySelector('.row-number');
            if (rowNumberElement) {
                rowNumberElement.textContent = index + 1;
            }
        });
    
        const disabledRows = document.querySelectorAll('#disabledSortable tr');
        disabledRows.forEach((row, index) => {
            const rowNumberElement = row.querySelector('.row-number');
            if (rowNumberElement) {
                rowNumberElement.textContent = index + 1;
            }
        });
    }

    function getUpdatedData() {
        const rows = document.querySelectorAll('#sortable tr');
        const updatedData = [];
        rows.forEach(row => {
            const rowNumber = row.querySelector('td:nth-child(1)').textContent;
            const school = row.querySelector('td:nth-child(2)').textContent;
            const city = row.querySelector('td:nth-child(3)').textContent;
            const degree = row.querySelector('td:nth-child(4)').textContent;
            const specialization = row.querySelector('td:nth-child(5)').textContent;
            updatedData.push({ row_number: parseInt(rowNumber), school, city, degree, specialization, enable: true });
        });

        const disabledRows = document.querySelectorAll('#disabledSortable tr');
        disabledRows.forEach(row => {
            const rowNumber = "0";
            const school = row.querySelector('td:nth-child(1)').textContent;
            const city = row.querySelector('td:nth-child(2)').textContent;
            const degree = row.querySelector('td:nth-child(3)').textContent;
            const specialization = row.querySelector('td:nth-child(4)').textContent;
            updatedData.push({ row_number: parseInt(rowNumber), school, city, degree, specialization, enable: false });
        });

        console.log('Données mises à jour:', updatedData);
        return updatedData;
    }

    function handleEnableDisableClick(event) {
        if (!isEditMode) return;
    
        const row = event.target.closest('tr');
        const isEnabled = row.closest('tbody').id === 'sortable';
        const targetTable = isEnabled ? disabledTbody : tbody;
    
        // Ajouter ou retirer la cellule contenant le numéro de ligne
        if (!isEnabled) {
            const rowNumberCell = document.createElement('td');
            rowNumberCell.className = 'row-number';
            rowNumberCell.textContent = tbody.children.length + 1;
            row.insertBefore(rowNumberCell, row.firstChild);
        } else {
            row.removeChild(row.querySelector('.row-number'));
        }
    
        targetTable.appendChild(row);
        updateRowNumbers();
    
        // Mettre à jour le texte et le style du bouton
        event.target.textContent = isEnabled ? 'Activer' : 'Désactiver';
        event.target.style.backgroundColor = isEnabled ? '#007bff' : '#dc3545';
    
        // Appeler la fonction pour mettre à jour le message
        updateNoVoeuxMessage();
    }

        let sortableInstance = null; // Variable pour stocker l'instance Sortable

    async function handleModifyClick() {
        isEditMode = !isEditMode;
        editModeMessage.style.display = isEditMode ? 'block' : 'none';
        editModeMessageUnclassed.style.display = isEditMode ? 'block' : 'none';
        noVoeuxMessage.style.display = isEditMode ? 'none' : 'block';
        validateBtn.disabled = true;
        validateBtn.style.pointerEvents = "none";
        validateBtn.style.opacity = "0.6";
    
        // Mettre à jour les lignes pour afficher ou masquer les boutons
        const rows = document.querySelectorAll('#sortable tr, #disabledSortable tr');
        rows.forEach(row => {
            const actionCell = row.querySelector('.action-cell');
            if (isEditMode) {
                // Ajouter le bouton si en mode édition
                if (!actionCell) {
                    const newActionCell = document.createElement('td');
                    newActionCell.classList.add('action-cell');
                    newActionCell.innerHTML = `
                        <button class="enable-disable-btn" style="background-color: ${row.closest('tbody').id === 'sortable' ? '#dc3545' : '#007bff'}; color: #fff; border: none; padding: 5px 10px; margin: 3px; border-radius: 3px; cursor: pointer; font-size: 0.8em; transition: background-color 0.3s ease;">
                            ${row.closest('tbody').id === 'sortable' ? 'Désactiver' : 'Activer'}
                        </button>
                    `;
                    row.appendChild(newActionCell);
    
                    // Ajouter l'événement au bouton
                    newActionCell.querySelector('.enable-disable-btn').addEventListener('click', handleEnableDisableClick);
                }
            } else {
                // Supprimer le bouton si hors mode édition
                if (actionCell) {
                    actionCell.remove();
                }
            }
        });
    
        // Activer ou désactiver le drag-and-drop
        if (isEditMode) {
            modifyBtn.textContent = "Enregistrer";
            modifyBtn.style.backgroundColor = "green";
            recentOrdersContainer.classList.add('edit-mode');
    
            // Activer le drag-and-drop
            sortableInstance = Sortable.create(tbody, {
                animation: 150,
                ghostClass: 'blue-background-class',
                onUpdate: updateRowNumbers
            });
        } else {
            modifyBtn.textContent = "Modifier";
            modifyBtn.style.backgroundColor = "";
            recentOrdersContainer.classList.remove('edit-mode');
    
            // Désactiver le drag-and-drop
            if (sortableInstance) {
                sortableInstance.destroy();
                sortableInstance = null;
            }
    
            updateNoVoeuxMessage();
    
            // Sauvegarder les données mises à jour
            const updatedData = getUpdatedData();
            try {
                const response = await fetch('/update_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(updatedData)
                });
                const result = await response.json();
                if (result.success) {
                    console.log('Données mises à jour avec succès');
                } else {
                    console.error('Erreur lors de la mise à jour des données:', result.message);
                }
            } catch (error) {
                console.error('Erreur lors de la requête de mise à jour:', error);
            }
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        const toggle = document.querySelector('.toggle');
        const navigation = document.querySelector('.navigation');
        const main = document.querySelector('.main');
    
        toggle.addEventListener('click', () => {
            navigation.classList.toggle('active');
            main.classList.toggle('active');
        });
    });

    function handleBeforeUnload(event) {
        if (isEditMode) {
            const message = "Vous avez des modifications non sauvegardées. Si vous quittez la page, elles seront perdues.";
            event.returnValue = message; // Standard pour la plupart des navigateurs
            return message; // Pour certains navigateurs
        }
    }

    function handleDownloadClick(event) {
        event.preventDefault();
        dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
    }

    function handleDownloadFormatClick(event, format) {
        event.preventDefault();
        window.location.href = `/download_voeux?format=${format}`;
    }

    function handleOutsideClick(event) {
        if (!downloadMenu.contains(event.target) && dropdownMenu.style.display === "block") {
            dropdownMenu.style.display = "none";
        }
    }

    async function handleConfirmClick() {
        try {
            const response = await fetch('/validate_voeux', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ validate: true })
            });
            const data = await response.json();
            console.log('Réponse de validation des vœux:', data);
            if (data.status) {
                validateBtn.style.pointerEvents = "none";
                validateBtn.style.opacity = "0.6";
                modifyBtn.style.display = "none";
                confirmationMessage.style.display = "block";
                downloadMenu.style.display = "block";
                popup.style.display = "none"; // Fermer la popup
            } else {
                console.error('Erreur lors de la validation des vœux:', data.message);
            }
        } catch (error) {
            console.error('Erreur lors de la requête de validation:', error);
        }
    }

    function handleValidateClick(event) {
        event.preventDefault();
        popup.style.display = "flex";
    }

    function handleCancelClick() {
        popup.style.display = "none";
    }

    function updateNoVoeuxMessage() {
        const noVoeuxMessage = document.getElementById('noVoeuxMessage');
        const tbody = document.getElementById('sortable');
        if (tbody.children.length === 0) {
            if(!isEditMode) {
                noVoeuxMessage.style.display = 'block';
            }
            validateBtn.disabled = true;
            validateBtn.style.pointerEvents = "none";
            validateBtn.style.opacity = "0.6";
        } else {
            noVoeuxMessage.style.display = 'none';
            validateBtn.disabled = false;
            validateBtn.style.pointerEvents = "auto";
            validateBtn.style.opacity = "1";
        }
        if (isEditMode) {
            validateBtn.disabled = true;
            validateBtn.style.pointerEvents = "none";
            validateBtn.style.opacity = "0.6";
        }
    }

    async function initialize() {
        const data = await fetchData();

        if (!data.professeur) {
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

            if (Array.isArray(data.voeux_etablissements)) {
                data.voeux_etablissements.forEach((item, index) => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        ${item.enable ? `<td class="row-number">${index + 1}</td>` : ''}
                        <td>${item.school}</td>
                        <td>${item.city}</td>
                        <td>${item.degree}</td>
                        <td style="text-align: left;">${item.specialization}</td>
                    `;
            
                    // Ajouter le bouton "Désactiver" uniquement si isEditMode est activé
                    if (isEditMode && item.enable) {
                        const actionCell = document.createElement('td');
                        actionCell.innerHTML = `
                            <button class="enable-disable-btn" style="background-color: #dc3545; color: #fff; border: none; padding: 5px 10px; margin: 3px; border-radius: 3px; cursor: pointer; font-size: 0.8em; transition: background-color 0.3s ease;">
                                Désactiver
                            </button>
                        `;
                        row.appendChild(actionCell);
                    }
            
                    if (item.enable) {
                        tbody.appendChild(row);
                    } else {
                        disabledTbody.appendChild(row);
                    }
                });
            
                updateRowNumbers();
            } else {
                console.error('voeux_etablissements is not an array:', data.voeux_etablissements);
            }

            document.querySelectorAll('.enable-disable-btn').forEach(button => {
                button.addEventListener('click', handleEnableDisableClick);
            });

            try {
                const response = await fetch('/get_voeux_status', {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                const statusData = await response.json();
                console.log('Statut des vœux:', statusData);
                if (statusData.choix_validees) {
                    console.log("Voeux déjà validés");
                    modifyBtn.style.display = "none";
                    validateBtn.style.display = "none";
                    downloadMenu.style.display = "block";
                }
            } catch (error) {
                console.error("Erreur lors de la récupération du statut des vœux :", error);
            }

            // Appeler la fonction pour mettre à jour le message
            updateNoVoeuxMessage();
        }
        didacticielStart();
    }

    initialize();
    function didacticielStart() {
        fetch('/didacticiel_get_state', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.didacticielCompleted) {
                console.log("Didacticiel déjà complété, pas besoin de l'afficher.");
                return;
            } else {
                console.log("Didacticiel non complété, affichage en cours...");
                Show_Didacticiel();
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération de l\'état du didacticiel:', error);
        });
    }

    modifyBtn.addEventListener('click', handleModifyClick);
    downloadBtn.addEventListener('click', handleDownloadClick);
    downloadXls.addEventListener('click', (event) => handleDownloadFormatClick(event, 'xls'));
    downloadPdf.addEventListener('click', (event) => handleDownloadFormatClick(event, 'pdf'));
    document.addEventListener('click', handleOutsideClick);
    confirmBtn.addEventListener('click', handleConfirmClick);
    validateBtn.addEventListener("click", handleValidateClick);
    cancelBtn.addEventListener("click", handleCancelClick);
    window.addEventListener('beforeunload', handleBeforeUnload);
    // Toggle navigation
    toggle.addEventListener('click', () => {
        navigation.classList.toggle('active');
        main.classList.toggle('active');
    });

    document.getElementById('sortByName').addEventListener('click', function() {
        sortOrder.name = !sortOrder.name;
        sortTableByColumn('disabledSortable', 0, false, sortOrder.name);
    });

    document.getElementById('sortByCity').addEventListener('click', function() {
        sortOrder.city = !sortOrder.city;
        sortTableByColumn('disabledSortable', 1, false, sortOrder.city);
    });

    document.getElementById('sortByType').addEventListener('click', function() {
        sortOrder.type = !sortOrder.type;
        sortTableByColumn('disabledSortable', 2, false, sortOrder.type);
    });

    document.getElementById('sortBySpecialty').addEventListener('click', function() {
        sortOrder.specialty = !sortOrder.specialty;
        sortTableByColumn('disabledSortable', 3, false, sortOrder.specialty);
    });
});








// WEBSOCKETS - SOCKET.IO


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
