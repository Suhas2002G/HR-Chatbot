const chatFeed = document.getElementById("chat-feed");
const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question-input");
const sendBtn = document.getElementById("send-btn");
const ingestBtn = document.getElementById("ingest-btn");
const ingestSideBtn = document.getElementById("ingest-side-btn");
const refreshStatusBtn = document.getElementById("refresh-status-btn");
const scrollChatBtn = document.getElementById("scroll-chat-btn");
const clearChatBtn = document.getElementById("clear-chat-btn");
const chips = document.querySelectorAll(".chip");
const ingestResult = document.getElementById("ingest-result");
const toast = document.getElementById("toast");

const apiStatus = document.getElementById("api-status");
const docCount = document.getElementById("doc-count");
const docPath = document.getElementById("doc-path");
const vectorPath = document.getElementById("vector-path");
const systemNote = document.getElementById("system-note");

let toastTimer = null;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.remove("visible"), 2400);
}

function autoResizeTextarea() {
  questionInput.style.height = "auto";
  questionInput.style.height = `${Math.min(questionInput.scrollHeight, 220)}px`;
}

function scrollFeedToBottom(smooth = true) {
  chatFeed.scrollTo({ top: chatFeed.scrollHeight, behavior: smooth ? "smooth" : "auto" });
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatMessage(text) {
  return escapeHtml(text).replace(/\n/g, "<br>");
}

function addMessage({ role, label, text, sources = [], retrievedChunks = null, typing = false }) {
  const article = document.createElement("article");
  article.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "HR";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const labelNode = document.createElement("p");
  labelNode.className = "message-label";
  labelNode.textContent = label;
  bubble.appendChild(labelNode);

  const contentNode = document.createElement("div");
  if (typing) {
    contentNode.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  } else {
    contentNode.innerHTML = `<p>${formatMessage(text)}</p>`;
  }
  bubble.appendChild(contentNode);

  if (!typing && sources.length) {
    const sourceWrap = document.createElement("div");
    sourceWrap.className = "sources";
    sources.forEach((source) => {
      const pill = document.createElement("span");
      pill.className = "source-pill";
      pill.textContent = source;
      sourceWrap.appendChild(pill);
    });
    bubble.appendChild(sourceWrap);
  }

  if (!typing && Number.isInteger(retrievedChunks)) {
    const meta = document.createElement("div");
    meta.className = "meta-line";
    meta.textContent = `Retrieved ${retrievedChunks} policy chunk${retrievedChunks === 1 ? "" : "s"}.`;
    bubble.appendChild(meta);
  }

  article.appendChild(avatar);
  article.appendChild(bubble);
  chatFeed.appendChild(article);
  scrollFeedToBottom();
  return article;
}

function clearConversation() {
  chatFeed.innerHTML = `
    <article class="message assistant intro-card">
      <div class="avatar">HR</div>
      <div class="bubble">
        <p class="message-label">Assistant</p>
        <p>I can answer questions from the indexed HR policy PDFs. If the collection is empty, use <strong>Index HR policies</strong> first.</p>
      </div>
    </article>
  `;
}

function setBusy(buttons, busy, labelMap = new Map()) {
  buttons.forEach((button) => {
    if (!button) return;
    if (busy) {
      if (!button.dataset.originalLabel) {
        button.dataset.originalLabel = button.textContent;
      }
      button.disabled = true;
      if (labelMap.has(button.id)) {
        button.textContent = labelMap.get(button.id);
      }
    } else {
      button.disabled = false;
      if (button.dataset.originalLabel) {
        button.textContent = button.dataset.originalLabel;
      }
    }
  });
}

async function fetchHealth() {
  apiStatus.textContent = "Checking";
  systemNote.textContent = "Refreshing system health...";

  try {
    const response = await fetch("/api/v1/health");
    if (!response.ok) {
      throw new Error("Health check failed.");
    }
    const data = await response.json();
    apiStatus.textContent = data.status === "ok" ? "Online" : "Issue";
    docCount.textContent = String(data.document_count ?? 0);
    docPath.textContent = data.documents_path ?? "Unknown";
    vectorPath.textContent = data.vector_store_path ?? "Unknown";
    systemNote.textContent = `API ready. ${data.document_count ?? 0} HR PDF files detected.`;
  } catch (error) {
    apiStatus.textContent = "Offline";
    docCount.textContent = "-";
    docPath.textContent = "Unavailable";
    vectorPath.textContent = "Unavailable";
    systemNote.textContent = error.message || "Could not reach the API.";
    showToast("Health check failed");
  }
}

async function runIngestion() {
  setBusy([ingestBtn, ingestSideBtn], true, new Map([
    ["ingest-btn", "Indexing..."],
    ["ingest-side-btn", "Running..."],
  ]));
  ingestResult.textContent = "Indexing HR policy PDFs into ChromaDB...";

  try {
    const response = await fetch("/api/v1/ingest/", { method: "POST" });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Ingestion failed.");
    }

    ingestResult.innerHTML = `Indexed <strong>${data.indexed_documents}</strong> documents and <strong>${data.indexed_chunks}</strong> chunks into <strong>${data.collection_name}</strong>.`;
    showToast("Policies indexed successfully");
    await fetchHealth();
  } catch (error) {
    ingestResult.textContent = error.message || "Ingestion failed.";
    showToast("Ingestion failed");
  } finally {
    setBusy([ingestBtn, ingestSideBtn], false);
  }
}

async function sendQuestion(question) {
  const trimmed = question.trim();
  if (!trimmed) {
    return;
  }

  addMessage({ role: "user", label: "You", text: trimmed });
  questionInput.value = "";
  autoResizeTextarea();

  const typingMessage = addMessage({
    role: "assistant",
    label: "Assistant",
    text: "",
    typing: true,
  });

  setBusy([sendBtn], true, new Map([["send-btn", "Sending..."]]));

  try {
    const response = await fetch("/api/v1/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: trimmed }),
    });
    const data = await response.json();
    typingMessage.remove();

    if (!response.ok) {
      throw new Error(data.detail || "Chat request failed.");
    }

    addMessage({
      role: "assistant",
      label: "Assistant",
      text: data.answer,
      sources: data.sources || [],
      retrievedChunks: data.retrieved_chunks,
    });
  } catch (error) {
    typingMessage.remove();
    addMessage({
      role: "assistant",
      label: "Assistant",
      text: error.message || "The request failed.",
    });
    showToast("Chat request failed");
  } finally {
    setBusy([sendBtn], false);
    questionInput.focus();
  }
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await sendQuestion(questionInput.value);
});

questionInput.addEventListener("input", autoResizeTextarea);
questionInput.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    await sendQuestion(questionInput.value);
  }
});

refreshStatusBtn.addEventListener("click", fetchHealth);
ingestBtn.addEventListener("click", runIngestion);
ingestSideBtn.addEventListener("click", runIngestion);
scrollChatBtn.addEventListener("click", () => document.getElementById("chat-panel").scrollIntoView({ behavior: "smooth", block: "start" }));
clearChatBtn.addEventListener("click", () => {
  clearConversation();
  showToast("Conversation cleared");
});

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    questionInput.value = chip.dataset.question || "";
    autoResizeTextarea();
    questionInput.focus();
  });
});

clearConversation();
autoResizeTextarea();
fetchHealth();
