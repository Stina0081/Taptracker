document.addEventListener("DOMContentLoaded", function() {
    const existingSelect = document.getElementById("existing_name");
    const newNameInput = document.getElementById("new_name");

    if (existingSelect && newNameInput) {
        existingSelect.addEventListener("change", function() {
            if (this.value) {
                newNameInput.disabled = true;
                newNameInput.value = "";
            } else {
                newNameInput.disabled = false;
            }
        });
    }
});
