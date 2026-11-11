function generateSummary() {
    const text = document.getElementById("newsInput").value.trim();
    const output = document.getElementById("output");

    if (!text) {
        output.textContent = "Please enter an article to analyze.";
        return;
    }

    const words = text.split(/\s+/);
    const preview = words.slice(0, 30).join(" ");

    output.textContent = "Article preview (" + words.length +
        " words): " + preview + (words.length > 30 ? "..." : "");
}
