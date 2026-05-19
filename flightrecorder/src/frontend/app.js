(function () {
  "use strict";

  var state = {
    currentSessionId: null,
    currentSession: null,
  };

  var DOM = {
    sessionForm: document.getElementById("session-form"),
    sessionList: document.getElementById("session-list"),
    chatArea: document.getElementById("chat-area"),
    transcript: document.getElementById("transcript"),
    messageForm: document.getElementById("message-form"),
    messageInput: document.getElementById("message-input"),
    sendBtn: document.getElementById("send-btn"),
    extractBtn: document.getElementById("extract-btn"),
    statusArea: document.getElementById("status-area"),
    budgetSummary: document.getElementById("budget-summary"),
    readPanels: document.getElementById("read-panels"),
    documentList: document.getElementById("document-list"),
    documentBody: document.getElementById("document-body"),
    spaghettiList: document.getElementById("spaghetti-list"),
    spaghettiBody: document.getElementById("spaghetti-body"),
  };

  function api(path, options) {
    var opts = options || {};
    return fetch(path, {
      method: opts.method || "GET",
      headers: Object.assign({ "Content-Type": "application/json" }, opts.headers || {}),
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    }).then(function (res) {
      if (!res.ok) {
        return res.text().then(function (text) {
          var msg;
          try { msg = JSON.parse(text).detail; } catch (e) { msg = text; }
          throw new Error(msg || "Request failed (" + res.status + ")");
        });
      }
      return res;
    });
  }

  function setStatus(text, cls) {
    DOM.statusArea.textContent = text;
    DOM.statusArea.className = cls || "status-info";
  }

  function clearStatus() {
    DOM.statusArea.textContent = "";
    DOM.statusArea.className = "";
  }

  function setChatEnabled(enabled) {
    DOM.messageInput.disabled = !enabled;
    DOM.sendBtn.disabled = !enabled;
    DOM.extractBtn.disabled = !enabled;
  }

  function createSession(provider, model, slug) {
    return api("/api/sessions", {
      method: "POST",
      body: { provider: provider, model: model, slug: slug || undefined },
    }).then(function (res) {
      return res.json();
    });
  }

  function listSessions() {
    return api("/api/sessions").then(function (res) {
      return res.json();
    });
  }

  function loadSession(id) {
    return api("/api/sessions/" + id).then(function (res) {
      return res.json();
    });
  }

  function loadBudget() {
    return api("/api/budget").then(function (res) {
      return res.json();
    });
  }

  function refreshBudget() {
    loadBudget().then(function (budget) {
      var cost = Number(budget.monthly_cost_dkk || 0).toFixed(4);
      var hardStop = Number(budget.hard_stop_dkk || 0).toFixed(2);
      DOM.budgetSummary.textContent = budget.status + " | " + cost + " DKK / " + hardStop + " DKK";
      DOM.budgetSummary.className = "budget-" + (budget.status || "ok");
      if (budget.hard_stop_active) {
        DOM.budgetSummary.textContent += " | hard-stop active";
      }
    }).catch(function (err) {
      DOM.budgetSummary.textContent = "Failed: " + err.message;
      DOM.budgetSummary.className = "budget-error";
    });
  }

  function renderSessionList(sessions) {
    DOM.sessionList.innerHTML = "";
    if (!sessions || sessions.length === 0) {
      DOM.sessionList.innerHTML = '<span class="session-item" style="opacity:0.5">No sessions</span>';
      return;
    }
    sessions.forEach(function (s) {
      var el = document.createElement("span");
      el.className = "session-item";
      if (s.session_id === state.currentSessionId) {
        el.classList.add("active");
      }
      el.textContent = s.slug || s.session_id.slice(0, 12);
      el.addEventListener("click", function () {
        selectSession(s.session_id);
      });
      DOM.sessionList.appendChild(el);
    });
  }

  function renderTranscript(messages) {
    DOM.transcript.innerHTML = "";
    if (!messages) return;
    messages.forEach(function (m) {
      DOM.transcript.appendChild(createMessageElement(m.role || "user", m.content || ""));
    });
    DOM.transcript.scrollTop = DOM.transcript.scrollHeight;
  }

  function createMessageElement(role, content) {
    var div = document.createElement("div");
    div.className = "transcript-msg " + role;
    div.textContent = role + "> " + content;
    return div;
  }

  function renderExtractionResult(result) {
    var el = document.getElementById("extraction-result");
    if (!el) {
      el = document.createElement("div");
      el.id = "extraction-result";
      DOM.chatArea.appendChild(el);
    }
    el.textContent = JSON.stringify(result, null, 2);
  }

  function selectSession(id) {
    state.currentSessionId = id;
    setStatus("Loading session...", "status-info");
    setChatEnabled(false);
    loadSession(id).then(function (session) {
      state.currentSession = session;
      DOM.chatArea.classList.remove("hidden");
      renderTranscript(session.messages);
      setChatEnabled(true);
      clearStatus();
      refreshSessionList();
    }).catch(function (err) {
      setStatus("Failed to load session: " + err.message, "status-error");
    });
  }

  function sendMessage(content) {
    if (!state.currentSessionId) return;
    setStatus("Sending...", "status-info");
    var assistantText = "";
    var streamDone = false;

    DOM.transcript.appendChild(createMessageElement("user", content));
    var assistantDiv = createMessageElement("assistant", "");
    DOM.transcript.appendChild(assistantDiv);

    function handleSSEEvents(events) {
      events.forEach(function (event) {
        var data = event.data || {};
        if (event.event === "token") {
          assistantText += data.token || "";
          assistantDiv.textContent = "assistant> " + assistantText;
          DOM.transcript.scrollTop = DOM.transcript.scrollHeight;
        } else if (event.event === "done") {
          streamDone = true;
          clearStatus();
          refreshBudget();
        } else if (event.event === "error") {
          streamDone = true;
          setStatus("Chat error: " + (data.detail || data.error || "unknown"), "status-error");
        }
      });
    }

    fetch("/api/sessions/" + state.currentSessionId + "/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: content }),
    }).then(function (res) {
      if (!res.ok) {
        return res.text().then(function (text) {
          throw new Error(text || "Chat request failed (" + res.status + ")");
        });
      }
      var reader = res.body.getReader();
      var decoder = new TextDecoder();
      var parser = createSSEParser();

      function pump() {
        return reader.read().then(function (result) {
          if (result.done) {
            if (!streamDone) {
              setStatus("Stream ended without done event", "status-error");
            }
            return;
          }
          handleSSEEvents(parser.parseChunk(decoder.decode(result.value, { stream: true })));
          return pump();
        });
      }

      return pump();
    }).catch(function (err) {
      setStatus("Chat failed: " + err.message, "status-error");
    });
  }

  function runExtraction() {
    if (!state.currentSessionId) return;
    setStatus("Extracting...", "status-info");
    api("/api/sessions/" + state.currentSessionId + "/extract", { method: "POST" })
      .then(function (res) { return res.json(); })
      .then(function (result) {
        renderExtractionResult(result);
        setStatus("Extraction complete", "status-success");
        refreshDocumentList();
        refreshSpaghettiList();
        refreshBudget();
        DOM.readPanels.classList.remove("hidden");
      })
      .catch(function (err) {
        setStatus("Extraction failed: " + err.message, "status-error");
      });
  }

  function loadDocuments() {
    return api("/api/documents").then(function (res) {
      return res.json();
    });
  }

  function loadDocument(ref) {
    return api("/api/documents/" + encodeURIComponent(ref)).then(function (res) {
      return res.json();
    });
  }

  function loadSpaghetti() {
    return api("/api/spaghetti").then(function (res) {
      return res.json();
    });
  }

  function loadSpaghettiIdea(ideaId) {
    return api("/api/spaghetti/" + encodeURIComponent(ideaId)).then(function (res) {
      return res.json();
    });
  }

  function refreshDocumentList() {
    loadDocuments().then(function (data) {
      DOM.documentList.innerHTML = "";
      if (!data.documents || data.documents.length === 0) {
        DOM.documentList.textContent = "No documents";
        DOM.documentBody.textContent = "";
        return;
      }
      data.documents.forEach(function (doc) {
        var el = document.createElement("span");
        el.textContent = doc.ref;
        el.addEventListener("click", function () {
          var items = DOM.documentList.querySelectorAll("span");
          items.forEach(function (item) { item.classList.remove("active"); });
          el.classList.add("active");
          loadDocument(doc.ref).then(function (docData) {
            DOM.documentBody.textContent = docData.body || "";
          }).catch(function (err) {
            DOM.documentBody.textContent = "Error: " + err.message;
          });
        });
        DOM.documentList.appendChild(el);
      });
    }).catch(function (err) {
      DOM.documentList.textContent = "Failed: " + err.message;
    });
  }

  function refreshSpaghettiList() {
    loadSpaghetti().then(function (data) {
      DOM.spaghettiList.innerHTML = "";
      if (!data.ideas || data.ideas.length === 0) {
        DOM.spaghettiList.textContent = "No ideas";
        DOM.spaghettiBody.textContent = "";
        return;
      }
      data.ideas.forEach(function (idea) {
        var el = document.createElement("span");
        el.textContent = idea.idea_id.slice(0, 30);
        el.addEventListener("click", function () {
          var items = DOM.spaghettiList.querySelectorAll("span");
          items.forEach(function (item) { item.classList.remove("active"); });
          el.classList.add("active");
          loadSpaghettiIdea(idea.idea_id).then(function (ideaData) {
            DOM.spaghettiBody.textContent = ideaData.body || "";
          }).catch(function (err) {
            DOM.spaghettiBody.textContent = "Error: " + err.message;
          });
        });
        DOM.spaghettiList.appendChild(el);
      });
    }).catch(function (err) {
      DOM.spaghettiList.textContent = "Failed: " + err.message;
    });
  }

  function refreshSessionList() {
    listSessions().then(function (data) {
      renderSessionList(data.sessions || data);
    }).catch(function (err) {
      setStatus("Failed to list sessions: " + err.message, "status-error");
    });
  }

  DOM.sessionForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var provider = document.getElementById("provider").value.trim();
    var model = document.getElementById("model").value.trim();
    var slug = document.getElementById("slug").value.trim();
    if (!provider || !model) {
      setStatus("Provider and model are required", "status-error");
      return;
    }
    setStatus("Creating session...", "status-info");
    createSession(provider, model, slug).then(function (session) {
      refreshSessionList();
      selectSession(session.session_id);
    }).catch(function (err) {
      setStatus("Failed to create session: " + err.message, "status-error");
    });
  });

  DOM.messageForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var content = DOM.messageInput.value.trim();
    if (!content) return;
    DOM.messageInput.value = "";
    sendMessage(content);
  });

  DOM.extractBtn.addEventListener("click", function () {
    runExtraction();
  });

  function createSSEParser() {
    var buffer = "";
    var pendingEvent = null;

    function parseChunk(chunk) {
      buffer += chunk;
      var lines = buffer.split("\n");
      buffer = lines.pop() || "";

      var events = [];
      var eventType = pendingEvent;
      pendingEvent = null;
      for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        if (line.startsWith("event: ")) {
          eventType = line.slice(7);
        } else if (line.startsWith("data: ")) {
          var dataStr = line.slice(6);
          try {
            var data = JSON.parse(dataStr);
            events.push({ event: eventType, data: data });
          } catch (e) {
            /* skip unparseable data */
          }
          eventType = null;
        }
      }
      pendingEvent = eventType;
      return events;
    }

    function flush() {
      if (buffer.length > 0) {
        buffer = "";
        return parseChunk("\n");
      }
      return [];
    }

    return { parseChunk: parseChunk, flush: flush };
  }

  window.flightrecorderApp = {
    api: api,
    createSession: createSession,
    listSessions: listSessions,
    loadSession: loadSession,
    loadBudget: loadBudget,
    refreshBudget: refreshBudget,
    sendMessage: sendMessage,
    runExtraction: runExtraction,
    createSSEParser: createSSEParser,
    loadDocuments: loadDocuments,
    loadDocument: loadDocument,
    loadSpaghetti: loadSpaghetti,
    loadSpaghettiIdea: loadSpaghettiIdea,
  };

  refreshSessionList();
  refreshBudget();
  DOM.readPanels.classList.remove("hidden");
  refreshDocumentList();
  refreshSpaghettiList();
})();
