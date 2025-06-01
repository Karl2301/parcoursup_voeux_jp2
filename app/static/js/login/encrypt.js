document.getElementById('login-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const username = document.getElementById('identifiant').value;
    const password = document.getElementById('password').value;

    const encrypt = new JSEncrypt();
    encrypt.setPublicKey(PUBLIC_KEY);

    const encryptedUsername = encrypt.encrypt(username);
    const encryptedPassword = encrypt.encrypt(password);

    if (!encryptedUsername || !encryptedPassword) {
        alert("Erreur lors du chiffrement des données. Veuillez réessayer.");
        return;
    }

    const formData = {
        username: encryptedUsername,
        password: encryptedPassword
    };

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) throw new Error(`Erreur HTTP ${response.status}`);
        return response.json(); // ou .text() selon la réponse attendue
    })
    .then(data => {
        console.log("Réponse du serveur:", data);
        if (data.error) {
            // Supprime les anciens messages d'erreur
            const errorContainer = document.getElementById('error-container');
            if (errorContainer) {
                errorContainer.innerHTML = ''; // Vide le conteneur
            }
            // Affiche les messages d'erreur
            const errorMessage = document.createElement('div');
            errorMessage.className = 'error-messages';
    
            // Ajoute une icône d'erreur
            const errorIcon = document.createElement('span');
            errorIcon.className = 'icon';
            errorIcon.textContent = '⚠️'; // Icône d'avertissement
            errorMessage.appendChild(errorIcon);
    
            // Ajoute le texte du message d'erreur
            const errorText = document.createElement('p');
            errorText.textContent = data.error;
            errorMessage.appendChild(errorText);
    
            // Insère le message d'erreur dans le conteneur
            errorContainer.appendChild(errorMessage);
            return;
        }
        if (data.set_cookie) {
            // Pose le cookie côté client (attention : path et samesite doivent correspondre à Flask)
            document.cookie = `session_cookie=${data.set_cookie}; path=/; samesite=Lax`;
        }
        if (data.redirect) {
            window.location.href = data.redirect;
        }
    })
    .catch(error => {
        console.error("Erreur lors de la requête de connexion:", error);
    });
});
