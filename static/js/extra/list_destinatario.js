const destinatarioRadios = document.querySelectorAll('.destinatario-radio');
const destinatarioIdInput = document.getElementById('destinatario_id'); // Mantén el ID del input

destinatarioRadios.forEach(radio => {
    radio.addEventListener('change', () => {
        if (radio.checked) {
            destinatarioIdInput.value = radio.value; // Actualiza el valor del input oculto
        }
    });
});