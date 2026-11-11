function generateSummary() {
    const text = document.getElementById("newsInput").value.trim();
    const output = document.getElementById("output");

    if (!text) {
        output.textContent = "Please enter a news article first.";
        return;
    }

    const sentences = text.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [text];
    output.textContent = "Preview summary: " +
        sentences.slice(0, 2).join(" ");
}
