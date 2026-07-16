// =============================================
// Product Extractor V2
// app.js
// =============================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Product Extractor V2 Loaded");

    // Highlight URL input when focused
    const urlInput = document.querySelector("input[name='url']");

    if (urlInput) {

        urlInput.addEventListener("focus", function () {
            this.style.borderColor = "#0d6efd";
        });

        urlInput.addEventListener("blur", function () {
            this.style.borderColor = "#cccccc";
        });

    }

    // Confirm before processing multiple URLs
    const multiForm = document.querySelector("form[action='/extract-all']");

    if (multiForm) {

        multiForm.addEventListener("submit", function (e) {

            const text = document.querySelector("textarea[name='urls']").value.trim();

            if (text === "") {
                alert("Please paste one or more URLs.");
                e.preventDefault();
                return;
            }

            const count = text.split(/\r?\n/).filter(x => x.trim() !== "").length;

            if (!confirm(`Extract ${count} product(s)?`)) {
                e.preventDefault();
            }

        });

    }

});