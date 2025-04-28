var identifiantSave = "";

function send_login_post_data(event) {
  event.preventDefault();  // Empêche le rechargement de la page

  const identifiant = document.getElementById("identifiant").value;
  const password = document.getElementById("password").value;
  const data = { "identifiant": identifiant, "password": password };

  fetch("/login", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
  })
  .then((response) => response.json())
  .then((data) => {
      if (data.success) {
          document.cookie = `session_cookie=${data.cookie}; path=/`;
          window.location.href = "/dashboard";
      } else {
          alert(data.message);
      }
  })
  .catch((error) => {
      console.error("Erreur lors de la requête de connexion:", error);
  });
}