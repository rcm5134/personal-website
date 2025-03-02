

function toggleMenu() {
    let dropdown = document.getElementById("dropdownMenu");
    dropdown.classList.toggle("active");
    const dropdownIcon = document.getElementById("dropdownIcon");
    // Toggle the "open" class on the dropdown icon
    dropdownIcon.classList.toggle("open");
}