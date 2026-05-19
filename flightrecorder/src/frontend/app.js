(function () {
  "use strict";

  var state = {
    currentSessionId: null,
    currentSession: null,
    runtimeReady: false,
    documentSelected: false,
    spaghettiSelected: false,
    currentDocRef: null,
    currentSpaghettiId: null,
  };

  var DOM = {
    sessionForm: document.getElementById("session-form"),
    providerInput: document.getElementById("provider"),
    modelInput: document.getElementById("model"),
    sessionList: document.getElementById("session-list"),
    sessionSummary: document.getElementById("session-summary"),
    assetList: document.getElementById("asset-list"),
    chatArea: document.getElementById("chat-area"),
    transcript: document.getElementById("transcript"),
    messageForm: document.getElementById("message-form"),
    messageInput: document.getElementById("message-input"),
    sendBtn: document.getElementById("send-btn"),
    extractBtn: document.getElementById("extract-btn"),
    uploadFile: document.getElementById("upload-file"),
    uploadBtn: document.getElementById("upload-btn"),
    uploadStatus: document.getElementById("upload-status"),
    statusArea: document.getElementById("status-area"),
    budgetSummary: document.getElementById("budget-summary"),
    callsList: document.getElementById("calls-list"),
    runtimeStatus: document.getElementById("runtime-status"),
    readPanels: document.getElementById("read-panels"),
    documentList: document.getElementById("document-list"),
    documentBody: document.getElementById("document-body"),
    spaghettiList: document.getElementById("spaghetti-list"),
    spaghettiBody: document.getElementById("spaghetti-body"),
    previewSessionBtn: document.getElementById("preview-session-btn"),
    previewDocBtn: document.getElementById("preview-doc-btn"),
    previewSpagBtn: document.getElementById("preview-spag-btn"),
    previewResult: document.getElementById("publish-preview-result"),
    runMatchmakerBtn: document.getElementById("run-matchmaker-btn"),
    matchmakerResult: document.getElementById("matchmaker-result"),
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
    var sessionSelected = Boolean(enabled);
    var chatActive = sessionSelected && state.runtimeReady;
    DOM.messageInput.disabled = !chatActive;
    DOM.sendBtn.disabled = !chatActive;
    DOM.extractBtn.disabled = !chatActive;
    DOM.uploadFile.disabled = !sessionSelected;
    DOM.uploadBtn.disabled = !sessionSelected;
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

  function loadApiCalls() {
    return api("/api/api-calls?limit=5").then(function (res) {
      return res.json();
    });
  }

  function refreshCalls() {
    loadApiCalls().then(function (data) {
      var calls = data.api_calls || [];
      DOM.callsList.innerHTML = "";
      if (calls.length === 0) {
        DOM.callsList.textContent = "No provider calls";
        return;
      }
      calls.forEach(function (call) {
        var cost = Number(call.cost_dkk || 0).toFixed(4);
        var row = document.createElement("div");
        row.className = "call-row";
        row.textContent = String(call.role || "unknown") + " " + String(call.model || "unknown")
          + " in:" + call.input_tokens
          + " out:" + call.output_tokens
          + " " + cost + " DKK";
        DOM.callsList.appendChild(row);
      });
    }).catch(function (err) {
      DOM.callsList.textContent = "Failed: " + err.message;
    });
  }

  function loadRuntime() {
    return api("/api/runtime").then(function (res) {
      return res.json();
    });
  }

  function refreshRuntime() {
    loadRuntime().then(function (status) {
      DOM.runtimeStatus.innerHTML = "";
      var roles = status.roles || {};
      state.runtimeReady = Boolean(
        roles.brainstorm && roles.brainstorm.configured &&
        roles.idea_capture && roles.idea_capture.configured
      );
      Object.keys(roles).forEach(function (name) {
        var role = roles[name];
        var el = document.createElement("span");
        var issues = role.issues || [];
        el.className = "role-entry " + (role.configured ? "configured" : "unconfigured");
        el.textContent = name + ": " + role.provider + "/" + role.model
          + " (" + (role.configured ? "ok" : issues.join(", ")) + ")";
        DOM.runtimeStatus.appendChild(el);
      });
      if (roles.brainstorm && roles.brainstorm.provider !== "none") {
        DOM.providerInput.value = roles.brainstorm.provider;
        DOM.modelInput.value = roles.brainstorm.model;
      }
      if (status.runtime_home) {
        var home = document.createElement("span");
        home.className = "role-entry";
        home.textContent = "home: " + status.runtime_home;
        DOM.runtimeStatus.appendChild(home);
      }
      setChatEnabled(Boolean(state.currentSessionId));
      if (!state.runtimeReady) {
        setStatus("Runtime is not ready for chat/extract; check provider config and pricing.", "status-error");
      }
    }).catch(function (err) {
      state.runtimeReady = false;
      DOM.runtimeStatus.innerHTML = "";
      var el = document.createElement("span");
      el.className = "role-entry error";
      el.textContent = "runtime: " + err.message;
      DOM.runtimeStatus.appendChild(el);
      setChatEnabled(false);
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

  function renderSessionSummary(session) {
    DOM.sessionSummary.innerHTML = "";
    if (!session) {
      DOM.sessionSummary.textContent = "No session selected";
      renderAssetList(null);
      return;
    }
    var fields = [
      ["provider", session.provider || "unknown"],
      ["model", session.model || "unknown"],
      ["messages", session.message_count || 0],
      ["images", session.image_count || 0],
      ["assets", session.assets ? session.assets.length : 0],
      ["extracted", session.extracted ? "yes" : "no"],
    ];
    fields.forEach(function (field) {
      var item = document.createElement("span");
      item.className = "session-summary-item";
      item.textContent = field[0] + ": " + field[1];
      DOM.sessionSummary.appendChild(item);
    });
    renderAssetList(session.assets || []);
  }

  function renderAssetList(assets) {
    DOM.assetList.innerHTML = "";
    if (!assets || assets.length === 0) {
      DOM.assetList.textContent = "";
      return;
    }
    assets.forEach(function (asset) {
      var row = document.createElement("div");
      var label = document.createElement("span");
      var remove = document.createElement("button");
      row.className = "asset-row";
      label.textContent = (asset.filename || "asset") + " (" + (asset.size_bytes || 0) + " bytes)";
      remove.type = "button";
      remove.className = "asset-remove";
      remove.textContent = "Remove";
      remove.addEventListener("click", function () {
        deleteAsset(asset.filename || "");
      });
      row.appendChild(label);
      row.appendChild(remove);
      DOM.assetList.appendChild(row);
    });
  }

  function deleteAsset(filename) {
    if (!state.currentSessionId || !filename) return;
    DOM.uploadStatus.textContent = "Removing " + filename + "...";
    api("/api/sessions/" + encodeURIComponent(state.currentSessionId)
      + "/assets/" + encodeURIComponent(filename), { method: "DELETE" })
      .then(function (res) { return res.json(); })
      .then(function () {
        return loadSession(state.currentSessionId);
      })
      .then(function (session) {
        state.currentSession = session;
        renderSessionSummary(session);
        DOM.uploadStatus.textContent = "Removed: " + filename;
      })
      .catch(function (err) {
        DOM.uploadStatus.textContent = "Remove failed: " + err.message;
      });
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
      renderSessionSummary(session);
      setChatEnabled(true);
      if (state.runtimeReady) {
        clearStatus();
      }
      refreshSessionList();
    }).catch(function (err) {
      setStatus("Failed to load session: " + err.message, "status-error");
      renderSessionSummary(null);
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
          refreshCalls();
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
        loadSession(state.currentSessionId).then(function (session) {
          state.currentSession = session;
          renderSessionSummary(session);
        }).catch(function () {});
        refreshDocumentList();
        refreshSpaghettiList();
        refreshBudget();
        refreshCalls();
        DOM.readPanels.classList.remove("hidden");
      })
      .catch(function (err) {
        setStatus("Extraction failed: " + err.message, "status-error");
      });
  }

  function fetchPublishPreview(sourceKind, sourceId) {
    DOM.previewResult.textContent = "Loading...";
    api("/api/publish/preview?source_kind=" + encodeURIComponent(sourceKind)
      + "&source_id=" + encodeURIComponent(sourceId))
      .then(function (res) { return res.json(); })
      .then(function (data) {
        var lines = [];
        lines.push("source: " + data.source_kind + " / " + data.source_id);
        lines.push("publishable: " + data.publishable);
        lines.push("rejection_reason: " + (data.rejection_reason || "none"));
        lines.push("approved_count: " + data.approved_count);
        if (data.snippets && data.snippets.length > 0) {
          lines.push("snippets: " + data.snippets.length);
        }
        DOM.previewResult.textContent = lines.join("\n");
      })
      .catch(function (err) {
        DOM.previewResult.textContent = "Error: " + err.message;
      });
  }

  function runMatchmakerForIdea(ideaId) {
    DOM.matchmakerResult.textContent = "Running...";
    api("/api/matchmaker/run", {
      method: "POST",
      body: { idea_ids: [ideaId] },
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        var candidates = data.candidates || [];
        var rejected = data.rejected_idea_ids || [];
        var lines = [];
        lines.push("batch: " + data.batch_id);
        lines.push("candidates: " + candidates.length);
        lines.push("rejected: " + rejected.length);
        candidates.forEach(function (candidate) {
          lines.push(
            candidate.idea_id + " -> " + candidate.project_ref
            + " (" + Number(candidate.confidence || 0).toFixed(2) + ")"
          );
          if (candidate.rationale) {
            lines.push(candidate.rationale);
          }
        });
        if (candidates.length === 0) {
          lines.push("No candidates with the current fail-closed scorer.");
        }
        DOM.matchmakerResult.textContent = lines.join("\n");
      })
      .catch(function (err) {
        DOM.matchmakerResult.textContent = "Error: " + err.message;
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
      var firstRef = data.documents[0].ref;
      data.documents.forEach(function (doc) {
        var el = document.createElement("span");
        el.textContent = doc.ref;
        if (!state.documentSelected && doc.ref === firstRef) {
          el.classList.add("active");
        }
        el.addEventListener("click", function () {
          state.documentSelected = true;
          state.currentDocRef = doc.ref;
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
      if (!state.documentSelected) {
        state.currentDocRef = firstRef;
        loadDocument(firstRef).then(function (docData) {
          DOM.documentBody.textContent = docData.body || "";
        }).catch(function (err) {
          DOM.documentBody.textContent = "Error: " + err.message;
        });
      }
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
      var firstId = data.ideas[0].idea_id;
      data.ideas.forEach(function (idea) {
        var el = document.createElement("span");
        el.textContent = idea.idea_id.slice(0, 30);
        if (!state.spaghettiSelected && idea.idea_id === firstId) {
          el.classList.add("active");
        }
        el.addEventListener("click", function () {
          state.spaghettiSelected = true;
          state.currentSpaghettiId = idea.idea_id;
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
      if (!state.spaghettiSelected) {
        state.currentSpaghettiId = firstId;
        loadSpaghettiIdea(firstId).then(function (ideaData) {
          DOM.spaghettiBody.textContent = ideaData.body || "";
        }).catch(function (err) {
          DOM.spaghettiBody.textContent = "Error: " + err.message;
        });
      }
    }).catch(function (err) {
      DOM.spaghettiList.textContent = "Failed: " + err.message;
    });
  }

  function refreshSessionList(autoSelect) {
    listSessions().then(function (data) {
      var sessions = data.sessions || data;
      renderSessionList(sessions);
      if (autoSelect && !state.currentSessionId && sessions && sessions.length > 0) {
        selectSession(sessions[0].session_id);
      }
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

  DOM.uploadBtn.addEventListener("click", function () {
    DOM.uploadFile.click();
  });

  DOM.uploadFile.addEventListener("change", function () {
    var file = DOM.uploadFile.files[0];
    if (!file || !state.currentSessionId) return;
    var formData = new FormData();
    formData.append("file", file);
    DOM.uploadStatus.textContent = "Uploading " + file.name + "...";
    fetch("/api/sessions/" + state.currentSessionId + "/upload", {
      method: "POST",
      body: formData,
    }).then(function (res) {
      if (!res.ok) {
        return res.text().then(function (text) { throw new Error(text); });
      }
      return res.json();
    }).then(function (result) {
      DOM.uploadStatus.textContent = "Uploaded: " + file.name
        + " (" + result.image_count + " images in session)";
      loadSession(state.currentSessionId).then(function (session) {
        state.currentSession = session;
        renderSessionSummary(session);
      }).catch(function (err) {
        DOM.uploadStatus.textContent = "Uploaded, but refresh failed: " + err.message;
      });
    }).catch(function (err) {
      DOM.uploadStatus.textContent = "Upload failed: " + err.message;
    });
  });

  DOM.previewSessionBtn.addEventListener("click", function () {
    if (!state.currentSessionId) {
      DOM.previewResult.textContent = "No session selected.";
      return;
    }
    fetchPublishPreview("session", state.currentSessionId);
  });

  DOM.previewDocBtn.addEventListener("click", function () {
    if (!state.currentDocRef) {
      DOM.previewResult.textContent = "No document selected.";
      return;
    }
    fetchPublishPreview("document", state.currentDocRef);
  });

  DOM.previewSpagBtn.addEventListener("click", function () {
    if (!state.currentSpaghettiId) {
      DOM.previewResult.textContent = "No spaghetti idea selected.";
      return;
    }
    fetchPublishPreview("spaghetti", state.currentSpaghettiId);
  });

  DOM.runMatchmakerBtn.addEventListener("click", function () {
    if (!state.currentSpaghettiId) {
      DOM.matchmakerResult.textContent = "No spaghetti idea selected.";
      return;
    }
    runMatchmakerForIdea(state.currentSpaghettiId);
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
    refreshCalls: refreshCalls,
    loadRuntime: loadRuntime,
    refreshRuntime: refreshRuntime,
    renderSessionSummary: renderSessionSummary,
    sendMessage: sendMessage,
    runExtraction: runExtraction,
    createSSEParser: createSSEParser,
    loadDocuments: loadDocuments,
    loadDocument: loadDocument,
    loadSpaghetti: loadSpaghetti,
    loadSpaghettiIdea: loadSpaghettiIdea,
    fetchPublishPreview: fetchPublishPreview,
    runMatchmakerForIdea: runMatchmakerForIdea,
    deleteAsset: deleteAsset,
  };

  refreshSessionList(true);
  refreshBudget();
  refreshCalls();
  refreshRuntime();
  DOM.readPanels.classList.remove("hidden");
  refreshDocumentList();
  refreshSpaghettiList();
})();
