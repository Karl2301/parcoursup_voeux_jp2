document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');

    // Vérifier si les vœux sont validés via l'élément HTML
    const validationStatus = document.getElementById('confirmationMessage');
    const voeuxValides = validationStatus && window.getComputedStyle(validationStatus).display === 'block';
    console.log('Vœux validés:', voeuxValides);

    // Afficher le popup si les vœux ne sont pas validés (à chaque connexion)
    if (!voeuxValides) {
        console.log('Affichage du popup dans 2 secondes si moins de 30 jours...');
        setTimeout(showDeadlinePopup, 500);
    }
});

function showDeadlinePopup() {
    const popup = document.getElementById('deadline-popup');
    const deadlineText = document.querySelector('.deadline-notice strong')?.textContent;
    
    console.log('Deadline text:', deadlineText);
    
    if (!popup || !deadlineText) {
        console.log('Éléments manquants:', { popup: !!popup, deadlineText: !!deadlineText });
        return;
    }

    // Convertir la date française en objet Date
    const [datePart, timePart] = deadlineText.split(' à ');
    if (!datePart || !timePart) {
        console.log('Format de deadlineText invalide:', deadlineText);
        return;
    }

    const [day, month, year] = datePart.split('/');
    const [hours, minutes] = timePart.split(':');
    if (!day || !month || !year || !hours || !minutes) {
        console.log('Composants de date manquants:', { day, month, year, hours, minutes });
        return;
    }

    const deadlineDate = new Date(year, month - 1, day, hours, minutes);
    const today = new Date();
    const diffTime = deadlineDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    console.log('Calcul des jours:', {
        deadlineDate,
        today,
        diffDays
    });

    if (isNaN(diffTime)) {
        console.log('Date invalide:', deadlineDate);
        return;
    }

    if (diffTime <= 0) {
        console.log('Date limite dépassée');
        return;
    }

    // Condition : afficher uniquement si moins de 30 jours restants
    if (diffDays > 30) {
        console.log('Plus de 30 jours restants, pas de popup');
        return;
    }

    const overlay = document.getElementById('popup-overlay');
    const message = document.getElementById('deadline-message');
    if (!overlay || !message) {
        console.log('Overlay ou message manquant');
        return;
    }

    message.textContent = `Il vous reste ${diffDays} jour${diffDays > 1 ? 's' : ''} pour valider votre pré-classement !`;

    // Afficher l'overlay et le popup
    //overlay.style.display = 'block';
    //popup.style.display = 'block';

    // Gérer la fermeture
    const closeButton = popup.querySelector('.close-popup');
    const understandButton = popup.querySelector('.understand-btn');

    function closePopup() {
        overlay.style.display = 'none';
        popup.style.display = 'none';
    }

    if (closeButton) {
        closeButton.addEventListener('click', closePopup);
    }

    if (understandButton) {
        understandButton.addEventListener('click', closePopup);
    }

    overlay.addEventListener('click', (event) => {
        if (event.target === overlay) {
            closePopup();
        }
    });
}