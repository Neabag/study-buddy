const md = window.markdownit({ breaks: true });

const loginScreen = document.getElementById("loginScreen");
const chatLayout = document.getElementById("chatLayout");
const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const loginInput = document.getElementById("loginUserIdInput");
const threadList = document.getElementById("threadList");

const API_BASE = "http://127.0.0.1:8000";

let userId = null;
let currentThreadId = null;
let threads = [];

async function getThreads() {
    const res = await fetch(`${API_BASE}/threads?user_id=${encodeURIComponent(userId)}`)

    if (!res.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await res.json();
    threads = [...data.threads] || [];
}

function renderThreads() {
    threadList.innerHTML = "";
    threads.forEach((t) => {
        const div = document.createElement("div");
        div.className = "thread-item" + (t.thread_id === currentThreadId ? " active" : "");
        div.textContent = t.title;
        div.dataset.threadId = t.thread_id;
        div.onclick = () => switchThread(t.thread_id);
        threadList.appendChild(div);
    });
}

function switchThread(id) {
    if (id === currentThreadId) return;
    currentThreadId = id;

    //remove active class from last active thread & add in current active
    const prev = threadList.querySelector(".thread-item.active");
    if (prev) prev.classList.remove("active");
    const current = threadList.querySelector(
        `.thread-item[data-thread-id="${id}"]`
    );
    if (current) current.classList.add("active");
    loadChatHistory(id);
}
async function loadChatHistory(thread_id) {
    if (!userId) return;

    try {
        const response = await fetch(
            `${API_BASE}/chats?user_id=${encodeURIComponent(userId)}&thread_id=${thread_id}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Clear existing messages
        chatMessages.innerHTML = "";

        // Display history messages (they should be in chronological order)
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach((msg) => {
                addMessage(msg.content, msg.role);
            });

            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    } catch (error) {
        console.error("Error loading chat history:", error);
        // Don't show error to user, just log it
    }
}


function addMessage(content, role) {
    const div = document.createElement("div");
    div.className = `message ${role}`;

    const c = document.createElement("div");
    c.className = "message-content";
    if (role == 'user') {
        c.innerHTML = content;
    } else c.innerHTML = md.render(content);

    div.appendChild(c);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    enhanceCodeBlocks(c);
    return c;
}

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    addMessage(text, "user");
    messageInput.value = "";

    const assistantDiv = addMessage("", "assistant");

    const res = await fetch(`${API_BASE}/chat_streams`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: userId,
            message: text,
            thread_id: currentThreadId
        }),
    });

    const thread_id = res.headers.get("X-Thread-Id");
    const thread_title = res.headers.get("X-Thread-Title");

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let full = "";

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        full += decoder.decode(value);
        assistantDiv.innerHTML = md.render(full);
        enhanceCodeBlocks(assistantDiv);
    }

    if (!currentThreadId && thread_id) {
        currentThreadId = thread_id;
        threads.unshift({
            thread_id: thread_id,
            title: thread_title
        })
    }
    renderThreads();
}

function enhanceCodeBlocks(container) {
    container.querySelectorAll("pre").forEach((pre) => {
        if (pre.querySelector(".copy-btn")) return;
        const btn = document.createElement("button");
        btn.className = "copy-btn";
        btn.textContent = "Copy";
        btn.onclick = () => {
            navigator.clipboard.writeText(pre.querySelector("code").innerText);
            btn.textContent = "Copied!";
            setTimeout(() => (btn.textContent = "Copy"), 3000);
        };
        pre.appendChild(btn);
    });
}

/* EVENTS */
document.getElementById("sendButton").onclick = sendMessage;

messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.getElementById("newChatBtn").onclick = () => {
    currentThreadId = null;
    chatMessages.innerHTML = "";
    renderThreads();
    messageInput.focus();
};

document.getElementById("loginButton").onclick = async () => {
    userId = loginInput.value.trim();
    if (!userId) return alert("Enter user id");
    loginScreen.style.display = "none";
    chatLayout.classList.add("active");
    threads = [];
    currentThreadId = null;
    chatMessages.innerHTML = "";
    await getThreads();
    renderThreads();
};
