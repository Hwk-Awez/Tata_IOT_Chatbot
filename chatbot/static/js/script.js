// static/js/script.js

const chatWindow = document.getElementById("chatWindow");
const queryInput = document.getElementById("queryInput");
const sendBtn = document.getElementById("sendBtn");
const robot = document.getElementById("robot");

// Initialize welcome timestamp
document.addEventListener("DOMContentLoaded", () => {
    const welcomeTime = document.getElementById("welcomeTime");

    if (welcomeTime) {
        welcomeTime.textContent = getCurrentTime();
    }

    queryInput.focus();
});


function getCurrentTime() {
    return new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}


function escapeHTML(text) {
    if (!text) return "";

    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}


function askSuggestion(button) {
    queryInput.value = button.textContent;
    sendMessage();
}


function addUserMessage(message) {

    const html = `
        <div class="message user">

            <div class="message-content">
                ${escapeHTML(message)}
            </div>

            <span class="timestamp">
                ${getCurrentTime()}
            </span>

        </div>
    `;

    chatWindow.insertAdjacentHTML("beforeend", html);

    scrollToBottom();
}


function addLoadingMessage() {

    robot.classList.add("thinking");

    const loadingId = `loading-${Date.now()}`;

    const html = `
        <div class="message bot loading"
             id="${loadingId}">

            <div class="message-content">

                <span class="typing-dots">
                    SteelBot is thinking
                    <span>.</span>
                    <span>.</span>
                    <span>.</span>
                </span>

            </div>

            <span class="timestamp">
                ${getCurrentTime()}
            </span>

        </div>
    `;

    chatWindow.insertAdjacentHTML("beforeend", html);

    scrollToBottom();

    return loadingId;
}


function removeLoadingMessage(id) {

    const loading = document.getElementById(id);

    if (loading) {
        loading.remove();
    }

    robot.classList.remove("thinking");
}


function typeMessage(element, text) {

    return new Promise(resolve => {

        let index = 0;

        function type() {

            if (index < text.length) {

                element.innerHTML += text.charAt(index);

                index++;

                scrollToBottom();

                setTimeout(type, 15);

            } else {
                resolve();
            }
        }

        type();
    });
}


async function addBotMessage(answer, sql = "") {

    const wrapper = document.createElement("div");

    wrapper.className = "message bot";

    wrapper.innerHTML = `
        <div class="message-content answer"></div>

        ${sql ? `
        <details class="sql-details">

            <summary>
                View SQL Query
            </summary>

            <pre class="sql-block">
${escapeHTML(sql)}
            </pre>

        </details>
        ` : ""}

        <span class="timestamp">
            ${getCurrentTime()}
        </span>
    `;

    chatWindow.appendChild(wrapper);

    scrollToBottom();

    const answerDiv = wrapper.querySelector(".answer");

    await typeMessage(answerDiv, answer);

    scrollToBottom();
}


async function sendMessage() {

    const query = queryInput.value.trim();

    if (!query) {
        return;
    }

    addUserMessage(query);

    queryInput.value = "";

    sendBtn.disabled = true;

    const loadingId = addLoadingMessage();

    try {

        const response = await fetch("/api/chat/", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                query: query
            })

        });

        removeLoadingMessage(loadingId);

        if (!response.ok) {

            addBotMessage(
                "⚠️ Server error occurred. Please try again."
            );

            return;
        }

        const data = await response.json();

        await addBotMessage(
            data.answer || "No answer generated.",
            data.sql || ""
        );

    }
    catch (error) {

        console.error(error);

        removeLoadingMessage(loadingId);

        addBotMessage(
            "⚠️ Unable to connect to the server. Please try again."
        );
    }
    finally {

        sendBtn.disabled = false;

        queryInput.focus();
    }
}


// Allow suggestions from HTML
window.askSuggestion = askSuggestion;
window.sendMessage = sendMessage;