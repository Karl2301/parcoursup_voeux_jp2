let sortableInstance = null;
let iaChatHistory = []; // {role: 'user'|'ia', content: '...'}
const iaFab = document.getElementById('ia-fab');
const iaPopup = document.getElementById('ia-chat-popup');
const iaClose = document.getElementById('ia-chat-close');
const iaMessages = document.getElementById('ia-chat-messages');
const iaInput = document.getElementById('ia-chat-input');
const iaSend = document.getElementById('ia-chat-send');
const iaSuggestions = document.getElementById('ia-chat-suggestions');
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
const actionBar = document.getElementById('actionBar');
const toggleStatusBtn = document.getElementById('toggleStatusBtn');
const tbodyEnabled = document.getElementById('sortable');      // tableau classé
const tbodyDisabled = document.getElementById('disabledSortable'); // tableau déclassé


document.addEventListener("DOMContentLoaded", async function () {

    let isEditMode = false;

    let sortOrder = {
        number: true,
        name: true,
        city: true,
        type: true,
        specialty: true
    };

    function cleanEmptyAttributesOnRows() {
        const allRows = document.querySelectorAll('#sortable tr, #disabledSortable tr');
        allRows.forEach(row => {
            const cb = row.querySelector('.select-checkbox');
            if (cb && cb.checked) {
                // Si la case est cochée, on force les attributs
                row.setAttribute('draggable', 'false');
                row.classList.add('selected');
            } else {
                // Si la case n'est pas cochée, on nettoie les attributs vides
                row.setAttribute('draggable', 'false');
                if (row.hasAttribute('class') && row.getAttribute('class').trim() === '') {
                    row.removeAttribute('class');
                }
                if (row.hasAttribute('style') && row.getAttribute('style').trim() === '') {
                    row.removeAttribute('style');
                }
            }
        });
    }

    function getCheckedRows() {
        const checkedInEnabled = Array.from(tbodyEnabled.querySelectorAll('input.select-checkbox:checked'));
        const checkedInDisabled = Array.from(tbodyDisabled.querySelectorAll('input.select-checkbox:checked'));
        return { checkedInEnabled, checkedInDisabled };
    }

    // Affiche ou cache la barre d'action, et bloque le multi-cochage entre tableaux
    function updateActionBar() {
        const { checkedInEnabled, checkedInDisabled } = getCheckedRows();
        if(isEditMode)
            if (checkedInEnabled.length > 0 && checkedInDisabled.length === 0) {
                toggleStatusBtn.textContent = 'Déclasser les vœux sélectionnés';
                toggleStatusBtn.style.backgroundColor = '#dc3545';
                toggleStatusBtn.classList.add('visible');
                toggleStatusBtn.disabled = false;
            } else if (checkedInDisabled.length > 0 && checkedInEnabled.length === 0) {
                toggleStatusBtn.textContent = 'Classer les vœux sélectionnés';
                toggleStatusBtn.style.backgroundColor = '#007bff';
                toggleStatusBtn.classList.add('visible');
                toggleStatusBtn.disabled = false;
            } else if (checkedInDisabled.length > 0 && checkedInEnabled.length > 0) {
                toggleStatusBtn.textContent = 'Vous ne pouvez pas classer et déclasser en même temps.';
                toggleStatusBtn.style.backgroundColor = 'orange';
                toggleStatusBtn.classList.add('visible');
                toggleStatusBtn.disabled = true;
            } else {
                toggleStatusBtn.classList.remove('visible');
                toggleStatusBtn.disabled = true;
            }
        else {
            toggleStatusBtn.classList.remove('visible');
            toggleStatusBtn.disabled = true;
        }
    }

    // Fonction pour déplacer les lignes cochées vers l'autre tableau
    function toggleStatus() {
        const { checkedInEnabled, checkedInDisabled } = getCheckedRows();

        if (checkedInEnabled.length > 0) {
            // Déclasser les lignes cochées du tableau classé vers le tableau déclassé
            checkedInEnabled.forEach(rowCheckbox => {
            const tr = rowCheckbox.closest('tr');

            // Simule le clic sur le bouton "Désactiver" du bouton d'action pour la ligne
            const btn = tr.querySelector('.enable-disable-btn');
            if (btn) btn.click();
            });

        } else if (checkedInDisabled.length > 0) {
            // Classer les lignes cochées du tableau déclassé vers le tableau classé
            checkedInDisabled.forEach(rowCheckbox => {
            const tr = rowCheckbox.closest('tr');

            // Simule le clic sur le bouton "Activer" du bouton d'action pour la ligne
            const btn = tr.querySelector('.enable-disable-btn');
            if (btn) btn.click();
            });
        }

        // Après déplacement, vider les sélections et cacher la barre
        tbodyEnabled.querySelectorAll('input.select-checkbox').forEach(cb => {
            cb.checked = false;
            cb.closest('tr').classList.remove('selected');
        });
        tbodyDisabled.querySelectorAll('input.select-checkbox').forEach(cb => {
            cb.checked = false;
            cb.closest('tr').classList.remove('selected');
        });

        updateRowNumbers();
        updateNoVoeuxMessage();
        updateActionBar();
    }



    // Initialisation
    toggleStatusBtn.addEventListener('click', toggleStatus);

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
        event.stopPropagation();

        if (!isEditMode) return;

        const button = event.target.closest('.enable-disable-btn');
        if (!button) return;

        const row = button.closest('tr');
        const isEnabled = row.closest('tbody').id === 'sortable';

        const sourceTbody = document.getElementById(isEnabled ? 'sortable' : 'disabledSortable');
        const targetTbody = document.getElementById(isEnabled ? 'disabledSortable' : 'sortable');

        if (isEnabled) {
            const numberCell = row.querySelector('.row-number');
            if (numberCell) row.removeChild(numberCell);
        } else {
            const rowNumberCell = document.createElement('td');
            rowNumberCell.className = 'row-number';
            rowNumberCell.textContent = targetTbody.children.length + 1;

            const checkboxCell = row.querySelector('td .select-checkbox')?.parentElement || row.children[0];
            row.insertBefore(rowNumberCell, checkboxCell.nextSibling);
        }

        const checkbox = row.querySelector('.select-checkbox');
        if (checkbox) checkbox.checked = false;
        row.classList.remove('selected');
        updateActionBar();

        targetTbody.appendChild(row);

        updateRowNumbers();

        button.textContent = isEnabled ? 'Activer' : 'Désactiver';
        button.style.backgroundColor = isEnabled ? '#007bff' : '#dc3545';

        updateNoVoeuxMessage();
    }


        let sortableInstance = null;

    async function handleModifyClick() {
        isEditMode = !isEditMode;
        editModeMessage.style.display = isEditMode ? 'block' : 'none';
        editModeMessageUnclassed.style.display = isEditMode ? 'block' : 'none';
        noVoeuxMessage.style.display = isEditMode ? 'none' : 'block';
        validateBtn.disabled = true;
        validateBtn.style.pointerEvents = "none";
        validateBtn.style.opacity = "0.6";

        document.querySelectorAll('.info-btn').forEach(btn => {
            btn.style.display = isEditMode ? 'none' : '';
        });
    
        const rows = document.querySelectorAll('#sortable tr, #disabledSortable tr');
        rows.forEach(row => {
            if (isEditMode) {
                if (!row.querySelector('.select-checkbox')) {
                    const td = document.createElement('td');
                    const cb = document.createElement('input');
                    cb.type = 'checkbox';
                    cb.classList.add('select-checkbox');
                    td.appendChild(cb);
                    row.insertBefore(td, row.firstChild);
                }

                const cb = row.querySelector('.select-checkbox');
                if (cb && !cb.hasAttribute('data-listener')) {
                    cb.setAttribute('data-listener', '1');
                    cb.addEventListener('change', function() {
                        row.classList.toggle('selected', cb.checked);
                        updateActionBar();
                    });
                }

                if (!tbody.hasAttribute('data-click-delegation')) {
                    tbody.setAttribute('data-click-delegation', '1');

                    tbody.addEventListener('click', (e) => {
                        if (e.target.tagName.toLowerCase() === 'input') return;

                        const tr = e.target.closest('tr');
                        if (!tr || !tr.querySelector('.select-checkbox')) return;

                        const cb = tr.querySelector('.select-checkbox');
                        cb.checked = !cb.checked;

                        if (cb.checked) {
                            tr.classList.add('selected');
                        } else {
                            tr.classList.remove('selected');
                        }

                        updateActionBar();
                    });
                }

                if (!disabledTbody.hasAttribute('data-click-delegation')) {
                    disabledTbody.setAttribute('data-click-delegation', 'true');

                    disabledTbody.addEventListener('click', (e) => {
                        if (e.target.tagName.toLowerCase() === 'input') return;

                        const tr = e.target.closest('tr');
                        if (!tr || !tr.querySelector('.select-checkbox')) return;

                        const cb = tr.querySelector('.select-checkbox');
                        cb.checked = !cb.checked;

                        if (cb.checked) {
                            tr.classList.add('selected');
                        } else {
                            tr.classList.remove('selected');
                        }

                        updateActionBar();
                    });
                }


                if (!row.querySelector('.action-cell')) {
                    const newActionCell = document.createElement('td');
                    newActionCell.classList.add('action-cell');
                    newActionCell.innerHTML = `
                        <button class="enable-disable-btn" style="background-color: ${row.closest('tbody').id === 'sortable' ? '#dc3545' : '#007bff'}; color: #fff; border: none; padding: 5px 10px; margin: 3px; border-radius: 3px; cursor: pointer; font-size: 0.8em; transition: background-color 0.3s ease;">
                            ${row.closest('tbody').id === 'sortable' ? 'Désactiver' : 'Activer'}
                        </button>
                    `;
                    row.appendChild(newActionCell);
                    newActionCell.querySelector('.enable-disable-btn').addEventListener('click', handleEnableDisableClick);
                }
            } else {
                const checkboxCell = row.querySelector('td .select-checkbox')?.parentElement;
                if (checkboxCell) checkboxCell.remove();

                const actionCell = row.querySelector('.action-cell');
                if (actionCell) actionCell.remove();

                const newRow = row.cloneNode(true);
                row.parentNode.replaceChild(newRow, row);
            }
        });

        if (isEditMode) {
            checkboxCell = document.getElementById('checkbox-cell');
            unCheckboxCell = document.getElementById('unCheckbox-cell');
            checkboxCell.style.display = 'inline-block';
            unCheckboxCell.style.display = 'inline-block';
            modifyBtn.textContent = "Enregistrer";
            modifyBtn.style.backgroundColor = "green";
            recentOrdersContainer.classList.add('edit-mode');


            
    
            sortableInstance = Sortable.create(tbody, {
                animation: 150,
                ghostClass: 'blue-background-class',
                multiDrag: true,
                selectedClass: 'selected',
                fallbackTolerance: 5,
                onStart: function (evt) {
                    const el = evt.item;
                    const checkbox = el.querySelector('input[type="checkbox"]');
                    if (!checkbox.checked) {
                        return false;
                    }
                },
                onChoose: function (evt) {
                    tbody.querySelectorAll('input.select-checkbox').forEach(cb => {
                        const tr = cb.closest('tr');
                        if (cb.checked) {
                            tr.classList.add('selected');
                        }
                    });
                },
                onUpdate: function (evt) {
                    const draggedRow = evt.item;
                    const selectedRows = Array.from(tbody.querySelectorAll('tr.selected'));
                    if (selectedRows.length <= 1) {
                        updateRowNumbers();
                        return;
                    }
                    const referenceRow = draggedRow.nextSibling;
                    selectedRows.forEach(row => {
                        if (row !== draggedRow) {
                            tbody.insertBefore(row, referenceRow);
                        }
                    });
                    updateRowNumbers();
                },
                onEnd: function (evt) {
                    cleanEmptyAttributesOnRows();
                }

            });

        } else {
            checkboxCell = document.getElementById('checkbox-cell');
            unCheckboxCell = document.getElementById('unCheckbox-cell');
            checkboxCell.style.display = 'none';
            unCheckboxCell.style.display = 'none';
            modifyBtn.textContent = "Modifier";
            modifyBtn.style.backgroundColor = "";
            recentOrdersContainer.classList.remove('edit-mode');
            updateActionBar();
    
            if (sortableInstance) {
                sortableInstance.destroy();
                sortableInstance = null;
            }
            tbody.querySelectorAll('tr.selected').forEach(row => row.classList.remove('selected'));
            tbody.querySelectorAll('input.select-checkbox').forEach(cb => {
                cb.checked = false;
                cb.closest('td').remove();
            });
    
            updateNoVoeuxMessage();
    
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
            event.returnValue = message;
            return message;
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
                popup.style.display = "none";
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
                        <td>
                            <button class="info-btn" style="background:#1976d2;color:#fff;border:none;padding:5px 10px;border-radius:3px;cursor:pointer;" title="Obtenir des infos IA" onclick="openIaPopup(this)">Info</button>
                        </td>
                    `;
            
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
                        row.classList.remove('selected');
                        const checkbox = row.querySelector('.select-checkbox');
                        if (checkbox) checkbox.checked = false;
                        updateActionBar();
                        tbody.appendChild(row);
                    } else {
                        row.classList.remove('selected');
                        const checkbox = row.querySelector('.select-checkbox');
                        if (checkbox) checkbox.checked = false;
                        updateActionBar();
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



// Ajout dynamique du bouton info sur chaque ligne de voeux
function addInfoButtons() {
    document.querySelectorAll('#sortable tr').forEach(row => {
        if (!row.querySelector('.info-btn')) {
            const infoCell = document.createElement('td');
            infoCell.innerHTML = `<button class="info-btn" style="background:#1976d2;color:#fff;border:none;padding:5px 10px;border-radius:3px;cursor:pointer;" title="Obtenir des infos IA" onclick="openIaPopup(this)">Info</button>`;
            row.appendChild(infoCell);
        }
    });
}
document.addEventListener('DOMContentLoaded', addInfoButtons);

// Gestion de la popup IA
let currentVoeu = '';
function openIaPopup(btn) {
   const row = btn.closest('tr');
    // Récupère tous les td sauf ceux qui contiennent une checkbox ou le bouton Info
    const tds = Array.from(row.querySelectorAll('td')).filter(td => {
        // Ignore les td qui contiennent une checkbox
        if (td.querySelector('input.select-checkbox')) return false;
        // Ignore la cellule qui contient le bouton Info (celle du bouton cliqué)
        if (td.contains(btn)) return false;
        // Ignore la cellule numéro si présente (optionnel, voir ci-dessous)
        if (td.classList.contains('row-number')) return false;
        return true;
    });

    // On prend les 4 derniers td filtrés (pour gérer les deux structures)
    const lastTds = tds.slice(-4);

    const voeuVille = lastTds[1]?.innerText || '';
    const voeuNom = lastTds[3]?.innerText || '';
    const voeuNomComplet = `${voeuNom} - ${voeuVille}`;
    currentVoeu = voeuNomComplet;
    document.getElementById('ia-popup').style.display = 'flex';
    document.getElementById('ia-popup-title').innerText = "Question sur : " + currentVoeu;
    document.getElementById('ia-messages').innerHTML = '';
    document.getElementById('ia-popup-content').classList.remove('expanded');
    setTimeout(() => document.getElementById('ia-question').focus(), 100);
}
function closeIaPopup() {
    document.getElementById('ia-popup').style.display = 'none';
}
async function sendIaQuestion() {
    const input = document.getElementById('ia-question');
    const question = input.value.trim();
    if (!question) return;
    input.value = '';
    const messagesDiv = document.getElementById('ia-messages');
    // Ajoute la question de l'utilisateur
    const userDiv = document.createElement('div');
    userDiv.className = 'ia-message user';
    userDiv.textContent = question;
    messagesDiv.appendChild(userDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    // Agrandit la popup si ce n'est pas déjà fait
    document.getElementById('ia-popup-content').classList.add('expanded');
    // Ajoute un div pour la réponse IA
    const iaDiv = document.createElement('div');
    iaDiv.className = 'ia-message ia';
    messagesDiv.appendChild(iaDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    // Appel API backend
    try {
        const res = await fetch('/api/ia_voeux', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question, voeu: currentVoeu})
        });
        const data = await res.json();
        // Affichage mot à mot
        await displayAnimatedIaResponse(iaDiv, data.response || "Aucune réponse IA.");
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (e) {
        iaDiv.textContent = "Erreur lors de la récupération de la réponse IA.";
    }
}
async function displayAnimatedIaResponse(div, text) {
    // Découpe le texte en caractères pour l'effet "mot à mot"
    let current = '';
    for (let i = 0; i < text.length; i++) {
        current += text[i];
        // Utilise marked pour convertir le markdown en HTML
        div.innerHTML = marked.parse(current);
        div.scrollIntoView({behavior: "smooth", block: "end"});
        await new Promise(r => setTimeout(r, 1));
    }
}


// Ouvre la popup
iaFab.onclick = () => {
  iaPopup.style.display = 'flex';
  iaFab.style.display = 'none';
  if (iaMessages.childElementCount === 0) {
    iaAddIaMessage("Bonjour ! Je suis l'assistant Parcoursup. Pose-moi une question ou choisis une suggestion ci-dessous.");
  }
  iaInput.focus();
};
// Ferme la popup
iaClose.onclick = () => {
  iaPopup.style.display = 'none';
  iaFab.style.display = 'block';
};
// Suggestions
Array.from(iaSuggestions.querySelectorAll('button')).forEach(btn => {
  btn.onclick = () => {
    iaInput.value = btn.textContent;
    iaInput.focus();
  };
});
// Envoi par bouton ou entrée
iaSend.onclick = iaSendQuestion;
iaInput.onkeydown = e => { if (e.key === 'Enter') iaSendQuestion(); };

function iaAddUserMessage(text) {
  const div = document.createElement('div');
  div.className = 'ia-chat-message user';
  div.textContent = text;
  iaMessages.appendChild(div);
  iaMessages.scrollTop = iaMessages.scrollHeight;
}
function iaAddIaMessage(text) {
  const div = document.createElement('div');
  div.className = 'ia-chat-message ia';
  div.textContent = text;
  iaMessages.appendChild(div);
  iaMessages.scrollTop = iaMessages.scrollHeight;
  return div;
}
async function iaSendQuestion() {
  const question = iaInput.value.trim();
  if (!question) return;
  iaInput.value = '';
  iaChatHistory.push({role: 'user', content: question});
  iaAddUserMessage(question);
  const iaDiv = iaAddIaMessage('');
  iaMessages.scrollTop = iaMessages.scrollHeight;
  // Appel backend avec historique
  try {
    const res = await fetch('/api/ia_voeux', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        question,
        voeu: '', // tu peux ajouter le voeu courant si besoin
        history: iaChatHistory
      })
    });
    const data = await res.json();
    await iaDisplayAnimatedIaResponse(iaDiv, data.response || "Aucune réponse IA.");
    iaChatHistory.push({role: 'ia', content: data.response || ""});
    iaMessages.scrollTop = iaMessages.scrollHeight;
  } catch (e) {
    iaDiv.textContent = "Erreur lors de la récupération de la réponse IA.";
  }
}

async function iaDisplayAnimatedIaResponse(div, text) {
  // Découpe le markdown en tokens pour garder la fluidité
  let html = marked.parse(text);
  div.innerHTML = ""; // Vide la div
  let i = 0;
  function typeNextChar() {
    if (i <= html.length) {
      div.innerHTML = html.slice(0, i);
      div.scrollIntoView({behavior: "smooth", block: "end"});
      i++;
      setTimeout(typeNextChar, 1);
    }
  }
  typeNextChar();
}


// WEBSOCKETS - SOCKET.IO


document.addEventListener('DOMContentLoaded', function () {
    const socket = io({
        reconnection: true,              
        reconnectionAttempts: 5,         
        reconnectionDelay: 1000,         
        autoConnect: true,               
    });

    const sessionCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('session_cookie='))
        ?.split('=')[1];

    if (sessionCookie) {
        console.log('Envoi du cookie session_cookie au serveur WebSocket');

        socket.on('connect', () => {
            socket.emit('join', { session_cookie: sessionCookie });
        });

    } else {
        console.warn("Aucun cookie 'session_cookie' trouvé");
    }

    socket.on('disconnect', function () {
        console.log('Déconnecté du serveur WebSocket');
    });
});
