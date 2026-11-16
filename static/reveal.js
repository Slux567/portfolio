// Fade elements in when they scroll into view.
//
// Every element with the "reveal" class starts hidden (see the <style> in
// base.html) and gets the "is-visible" class once it enters the screen.
//
// This lives in its own file (not inline in the HTML) because the
// Content-Security-Policy in app.py only allows scripts from files.

// Tell the CSS that JavaScript works, so it's safe to hide the elements.
// Without JavaScript this never runs and everything simply stays visible.
document.documentElement.classList.add("js");

document.addEventListener("DOMContentLoaded", function () {
    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                // Only animate once: stop watching this element.
                observer.unobserve(entry.target);
            }
        });
    }, {
        // Trigger a bit before the element is fully on screen.
        rootMargin: "0px 0px -10% 0px",
    });

    document.querySelectorAll(".reveal").forEach(function (element) {
        observer.observe(element);
    });
});
