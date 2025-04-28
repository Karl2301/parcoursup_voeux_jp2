document.addEventListener("DOMContentLoaded", async function () {
    const toggle = document.querySelector('.toggle');
    const navigation = document.querySelector('.navigation');
    const main = document.querySelector('.main');
    const aide_nav = document.getElementById('aide_nav');
    const notification_nav = document.getElementById('notification_nav');
    const elevesNav = document.getElementById('eleves_nav');
    const statistiques_nav = document.getElementById('statistiques_nav');
    const body = document.body;
    const siteweb_nav = document.getElementById('siteweb_nav');

    // Gestion du thème
    fetch('/get_theme', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.darkTheme === true) {
            body.classList.add("dark");
            localStorage.setItem("dark-theme", "enabled");
        } else {
            body.classList.remove("dark");
            localStorage.setItem("dark-theme", "disabled");
        }
    });

    // Initialisation des données
    async function fetchData() {
        try {
            const response = await fetch('/get_data', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Erreur lors de la récupération des données:', error);
        }
    }

    async function initialize() {
        const data = await fetchData();
        
        if (data.professeur) {
            aide_nav.style.display = 'none';
            notification_nav.style.display = 'block';
            if (data.admin) {
                siteweb_nav.style.display = 'block';
                statistiques_nav.style.display = 'block';
            }
            if (elevesNav) elevesNav.style.display = 'none';
        }
    }
    

    initialize();

    // Toggle navigation
    toggle.addEventListener('click', () => {
        navigation.classList.toggle('active');
        main.classList.toggle('active');
    });
});