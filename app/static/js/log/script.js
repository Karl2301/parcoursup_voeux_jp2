document.addEventListener('DOMContentLoaded', function () {
    var protocol = location.protocol === 'https:' ? 'wss://' : 'ws://';
    var socket = io.connect(protocol + document.domain + ':' + location.port);

    // Récupérer le cookie session_cookie
    const sessionCookie = document.cookie
        .split('; ')
        .find(row => row.startsWith('session_cookie='))
        ?.split('=')[1];

    if (sessionCookie) {
        console.log('Envoi du cookie session_cookie au serveur WebSocket');
        socket.emit('join', { session_cookie: sessionCookie });
    } else {
        console.warn("Aucun cookie 'session_cookie' trouvé");
    }

    // Écouter les nouveaux logs
    socket.on('new_log', function (data) {
        console.log('Nouveau log reçu:', data);

        // Convertir la description en HTML avec marked.js
        const descriptionHtml = marked.parse(data.description);

        // Créer un nouvel élément de log
        const logContainer = document.createElement('div');
        logContainer.className = `log ${data.etat}`;
        logContainer.innerHTML = `
            <div class="log-indicator"></div>
            <div class="log-content">
                <div class="log-title">${data.title}</div>
                <div class="log-description">${descriptionHtml}</div>
                <div class="log-time">Provenance: ${data.provenance}</div>
                <div class="log-time">Utilisateur: ${data.user_id}</div>
            </div>
            <div class="log-time">${data.time}</div>
        `;

        // Ajouter le log à la page
        document.body.appendChild(logContainer);
        // Faire défiler la page tout en bas
        window.scrollTo(0, document.body.scrollHeight);
    });

    socket.on('disconnect', function () {
        console.log('Déconnecté du serveur WebSocket');
    });

    window.addEventListener('beforeunload', function () {
        console.log('Fermeture de la fenêtre détectée, déconnexion...');
        socket.disconnect();
    });
});