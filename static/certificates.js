// Show the chosen page of certificates and hide the others.
// No page reload needed, so you stay in the same spot on the page.
//
// This lives in its own file (not inline in the HTML) because the
// Content-Security-Policy in app.py only allows scripts from files.
function showCertPage(number) {
    document.querySelectorAll(".cert-page").forEach(function (page, i) {
        page.classList.toggle("hidden", i !== number);
    });
    document.querySelectorAll(".cert-button").forEach(function (button, i) {
        button.classList.toggle("bg-white", i === number);
        button.classList.toggle("text-black", i === number);
        button.classList.toggle("bg-neutral-800", i !== number);
        button.classList.toggle("text-neutral-300", i !== number);
    });
}

document.querySelectorAll(".cert-button").forEach(function (button) {
    button.addEventListener("click", function () {
        showCertPage(Number(button.dataset.page));
    });
});
