document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

function sendMessage() {
    let inputField = document.getElementById("user-input");
    let message = inputField.value.trim();
    if (message === "") return;

    displayMessage(message, "user-message");
    inputField.value = "";

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        displayMessage(formatBotResponse(data.reply), "bot-message");
    })
    .catch(error => console.error("Error:", error));
}

function displayMessage(message, className) {
    let chatBox = document.getElementById("chat-box");
    let msgDiv = document.createElement("div");
    msgDiv.className = "message " + className;
    msgDiv.innerHTML = message;

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function formatBotResponse(response) {
    if (response.includes("*")) {
        return response.replace(/\* (.+)/g, "<li>$1</li>").replace(/\n/g, "");
    }
    return response;
}
