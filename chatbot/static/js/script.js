const chatWindow   = document.getElementById("chatWindow");
const queryInput   = document.getElementById("queryInput");
const sendBtn      = document.getElementById("sendBtn");
const robot        = document.getElementById("robot");
const suggestions  = document.getElementById("suggestions");

let firstMessage = true;

document.addEventListener("DOMContentLoaded", () => {
    const welcomeTime = document.getElementById("welcomeTime");
    if (welcomeTime) welcomeTime.textContent = getCurrentTime();
    queryInput.focus();
});

function getCurrentTime() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function escapeHTML(text) {
    if (!text) return "";
    const d = document.createElement("div");
    d.textContent = text;
    return d.innerHTML;
}

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function askSuggestion(button) {
    queryInput.value = button.textContent;
    sendMessage();
}

function hideSuggestions() {
    if (suggestions) {
        suggestions.style.transition = "opacity 200ms ease";
        suggestions.style.opacity = "0";
        setTimeout(() => { suggestions.style.display = "none"; }, 200);
    }
}

function addUserMessage(message) {
    const div = document.createElement("div");
    div.className = "message user";
    div.innerHTML = `
        <div class="msg-meta">
            <span class="msg-sender">You</span>
            <span class="timestamp">${getCurrentTime()}</span>
        </div>
        <div class="message-content">${escapeHTML(message)}</div>
    `;
    chatWindow.appendChild(div);
    scrollToBottom();
}

function addLoadingMessage() {
    robot.classList.add("thinking");

    const id = `loading-${Date.now()}`;
    const div = document.createElement("div");
    div.className = "message bot loading";
    div.id = id;
    div.innerHTML = `
        <div class="msg-meta">
            <span class="msg-sender">Assistant</span>
            <span class="timestamp">${getCurrentTime()}</span>
        </div>
        <div class="message-content">
            <div class="typing-row">
                <span>Thinking</span>
                <span class="typing-dots"><span></span><span></span><span></span></span>
            </div>
        </div>
    `;
    chatWindow.appendChild(div);
    scrollToBottom();
    return id;
}

function removeLoadingMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
    robot.classList.remove("thinking");
}

function typeMessage(element, text) {
    return new Promise(resolve => {
        let i = 0;
        function tick() {
            if (i < text.length) {
                element.innerHTML += escapeHTML(text.charAt(i++));
                scrollToBottom();
                setTimeout(tick, 10);
            } else {
                resolve();
            }
        }
        tick();
    });
}

async function addBotMessage(answer, sql = "") {
    const div = document.createElement("div");
    div.className = "message bot";
    div.innerHTML = `
        <div class="msg-meta">
            <span class="msg-sender">Assistant</span>
            <span class="timestamp">${getCurrentTime()}</span>
        </div>
        <div class="message-content"><span class="answer"></span>${sql ? `
        <details class="sql-details">
            <summary>View SQL</summary>
            <pre class="sql-block">${escapeHTML(sql)}</pre>
        </details>` : ""}</div>
    `;
    chatWindow.appendChild(div);
    scrollToBottom();
    await typeMessage(div.querySelector(".answer"), answer || "No answer generated.");
    scrollToBottom();
}

async function sendMessage() {
    const query = queryInput.value.trim();
    if (!query) return;

    // On first real message, hide welcome block + suggestions
    if (firstMessage) {
        firstMessage = false;
        const wb = document.querySelector(".welcome-block");
        if (wb) {
            wb.style.transition = "opacity 250ms ease";
            wb.style.opacity = "0";
            setTimeout(() => wb.remove(), 250);
        }
        hideSuggestions();
    }

    addUserMessage(query);
    queryInput.value = "";
    sendBtn.disabled = true;

    const loadingId = addLoadingMessage();

    try {
        const response = await fetch("/api/chat/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });

        removeLoadingMessage(loadingId);

        if (!response.ok) {
            await addBotMessage("Server error. Please try again.");
            return;
        }

        const data = await response.json();
        await addBotMessage(data.answer || "No answer generated.", data.sql || "");
    } catch (err) {
        console.error(err);
        removeLoadingMessage(loadingId);
        await addBotMessage("Unable to reach the server. Please try again.");
    } finally {
        sendBtn.disabled = false;
        queryInput.focus();
    }
}

window.askSuggestion = askSuggestion;
window.sendMessage   = sendMessage;