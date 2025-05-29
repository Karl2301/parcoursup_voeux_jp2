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
            alert(data.error);
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
