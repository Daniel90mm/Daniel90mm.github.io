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
    sessions: [],
    spaghetti: [],
    budget: null,
  };

  var STICKY_COLORS = ["#e8a04a", "#6aa3ff", "#8fb84a", "#5fb7c7", "#e36363"];
  var STICKY_ROTATIONS = [-1.2, 0.6, -0.4, 1.4, -0.8, 0.3];

  var DOM = {
    sessionForm: document.getElementById("session-form"),
    sessionNameForm: document.getElementById("session-name-form"),
    sessionNameInput: document.getElementById("session-name-input"),
    sessionNameSave: document.getElementById("session-name-save"),
    sessionDeleteBtn: document.getElementById("session-delete-btn"),
    providerInput: document.getElementById("provider"),
    modelInput: document.getElementById("model"),
    sessionList: document.getElementById("session-list"),
    sessionSummary: document.getElementById("session-summary"),
    assetList: document.getElementById("asset-list"),
    chatArea: document.getElementById("chat-area"),
    chatEmpty: document.getElementById("chat-empty"),
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
    budgetBar: document.getElementById("budget-bar"),
    budgetMeta: document.getElementById("budget-meta"),
    callsList: document.getElementById("calls-list"),
    readPanels: document.getElementById("read-panels"),
    documentList: document.getElementById("document-list"),
    documentBody: document.getElementById("document-body"),
    spaghettiList: document.getElementById("spaghetti-list"),
    spaghettiBody: document.getElementById("spaghetti-body"),
    spaghettiGrid: document.getElementById("spaghetti-grid"),
    spaghettiCountTitle: document.getElementById("spaghetti-count-title"),
    previewSessionBtn: document.getElementById("preview-session-btn"),
    previewDocBtn: document.getElementById("preview-doc-btn"),
    previewSpagBtn: document.getElementById("preview-spag-btn"),
    previewResult: document.getElementById("publish-preview-result"),
    runMatchmakerBtn: document.getElementById("run-matchmaker-btn"),
    matchmakerResult: document.getElementById("matchmaker-result"),
    sessionBarId: document.getElementById("session-bar-id"),
    sessionBarMeta: document.getElementById("session-bar-meta"),
    sessionBarStatus: document.getElementById("session-bar-status"),
    sessionBarCounter: document.getElementById("session-bar-counter"),
    composerSessionId: document.getElementById("composer-session-id"),
    composerProvider: document.getElementById("composer-provider"),
    composerBudget: document.getElementById("composer-budget"),
    attachmentRow: document.getElementById("attachment-row"),
    searchForm: document.getElementById("search-form"),
    searchInput: document.getElementById("search-input"),
    searchBtn: document.getElementById("search-btn"),
    searchResults: document.getElementById("search-results"),
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
    DOM.statusArea.className = "fr-status " + (cls || "status-info");
  }

  function clearStatus() {
    DOM.statusArea.textContent = "";
    DOM.statusArea.className = "fr-status";
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
    }).then(function (res) { return res.json(); });
  }

  function renameSession(id, displayName) {
    return api("/api/sessions/" + encodeURIComponent(id), {
      method: "PATCH",
      body: { display_name: displayName },
    }).then(function (res) { return res.json(); });
  }

  function deleteSessionApi(id) {
    return api("/api/sessions/" + encodeURIComponent(id), {
      method: "DELETE",
    }).then(function (res) { return res.json(); });
  }

  function listSessions() {
    return api("/api/sessions").then(function (res) { return res.json(); });
  }

  function loadSession(id) {
    return api("/api/sessions/" + id).then(function (res) { return res.json(); });
  }

  function loadBudget() {
    return api("/api/budget").then(function (res) { return res.json(); });
  }

  function refreshBudget() {
    loadBudget().then(function (budget) {
      state.budget = budget;
      var cost = Number(budget.monthly_cost_dkk || 0);
      var hardStop = Number(budget.hard_stop_dkk || 0);
      var pct = hardStop > 0 ? Math.min(100, (cost / hardStop) * 100) : 0;
      DOM.budgetSummary.innerHTML =
        '<span class="budget-label fr-muted">' + (budget.status || "ok") + '</span>'
        + '<span><span class="budget-spent">' + cost.toFixed(2) + '</span>'
        + '<span class="budget-cap"> / ' + hardStop.toFixed(2) + ' DKK</span></span>';
      DOM.budgetSummary.className = "fr-budget-summary budget-" + (budget.status || "ok");
      DOM.budgetBar.style.width = Math.max(pct, 0.4) + "%";
      DOM.budgetBar.className = "fr-budget-bar" + (budget.status === "warn" ? " warn" : (budget.status === "hard_stop" ? " hard_stop" : ""));
      var meta = "today " + cost.toFixed(2) + " DKK · hard-stop at " + hardStop.toFixed(2) + " DKK";
      if (budget.hard_stop_active) meta += " · hard-stop active";
      DOM.budgetMeta.textContent = meta;

      // composer status strip budget chip
      var dotClass = budget.status === "warn" ? "fr-budget-warn"
                    : budget.status === "hard_stop" ? "fr-budget-stop"
                    : "fr-ok";
      DOM.composerBudget.className = dotClass;
      DOM.composerBudget.textContent = "● " + cost.toFixed(2) + " / " + hardStop.toFixed(2) + " DKK";
    }).catch(function (err) {
      DOM.budgetSummary.textContent = "Failed: " + err.message;
      DOM.budgetSummary.className = "fr-budget-summary budget-error";
      DOM.budgetBar.style.width = "0%";
      DOM.budgetMeta.textContent = "";
    });
  }

  function loadApiCalls() {
    return api("/api/api-calls?limit=3").then(function (res) { return res.json(); });
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
        var left = document.createElement("span");
        left.textContent = String(call.role || "unknown") + " · " + String(call.model || "unknown")
          + " · " + call.input_tokens + "→" + call.output_tokens;
        var right = document.createElement("span");
        right.className = "call-cost";
        right.textContent = cost + " DKK";
        row.appendChild(left);
        row.appendChild(right);
        DOM.callsList.appendChild(row);
      });
    }).catch(function (err) {
      DOM.callsList.textContent = "Failed: " + err.message;
    });
  }

  function loadRuntime() {
    return api("/api/runtime").then(function (res) { return res.json(); });
  }

  function refreshRuntime() {
    loadRuntime().then(function (status) {
      var roles = status.roles || {};
      state.runtimeReady = Boolean(
        roles.brainstorm && roles.brainstorm.configured &&
        roles.idea_capture && roles.idea_capture.configured
      );
      if (roles.brainstorm && roles.brainstorm.provider !== "none") {
        DOM.providerInput.value = roles.brainstorm.provider;
        DOM.modelInput.value = roles.brainstorm.model;
        DOM.composerProvider.textContent = roles.brainstorm.provider + "/" + roles.brainstorm.model;
      }
      setChatEnabled(Boolean(state.currentSessionId));
      if (!state.runtimeReady) {
        setStatus("Runtime is not ready for chat/extract; check provider config and pricing.", "status-error");
      }
    }).catch(function (err) {
      state.runtimeReady = false;
      setStatus("Runtime check failed: " + err.message, "status-error");
      setChatEnabled(false);
    });
  }

  function renderSessionList(sessions) {
    DOM.sessionList.innerHTML = "";
    if (!sessions || sessions.length === 0) {
      var empty = document.createElement("div");
      empty.className = "fr-log-row";
      empty.style.opacity = "0.55";
      empty.innerHTML = '<span></span><span class="fr-log-slug">no sessions</span><span></span>';
      DOM.sessionList.appendChild(empty);
      return;
    }
    sessions.slice(0, 8).forEach(function (s) {
      var row = document.createElement("div");
      var active = s.session_id === state.currentSessionId;
      row.className = "fr-log-row" + (active ? " active" : "");

      var timeStr = "";
      if (s.created_at) {
        var d = new Date(s.created_at);
        if (!isNaN(d)) timeStr = ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
      }
      if (!timeStr && s.session_id) timeStr = s.session_id.slice(0, 5);

      var slug = s.slug || s.session_id.slice(0, 12);
      var statusKind = active ? "live" : (s.status || "ok");

      var time = document.createElement("span");
      time.className = "fr-log-time";
      time.textContent = timeStr;
      var slugEl = document.createElement("span");
      slugEl.className = "fr-log-slug";
      slugEl.textContent = slug;
      var statusEl = document.createElement("span");
      statusEl.className = "fr-log-status " + statusKind;
      statusEl.textContent = "●";

      row.appendChild(time);
      row.appendChild(slugEl);
      row.appendChild(statusEl);
      row.addEventListener("click", function () { selectSession(s.session_id); });
      DOM.sessionList.appendChild(row);
    });
  }

  function turnGlyphForRole(role) {
    if (role === "user") return "> daniel";
    if (role === "assistant") return "∴ brainstorm";
    return "· system";
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  // Tiny markdown renderer: math passthrough, fenced code, inline code, headings, bold, italic.
  // Math is extracted before escaping so '$X_{train}$' survives intact for KaTeX auto-render.
  function renderMarkdown(text) {
    if (!text) return "";
    var t = String(text);

    var maths = [];
    t = t.replace(/\$\$([\s\S]+?)\$\$/g, function (_, src) {
      maths.push({ block: true, src: src });
      return "%%FR_MATH_" + (maths.length - 1) + "%%";
    });
    t = t.replace(/\$([^\$\n]{1,500}?)\$/g, function (_, src) {
      maths.push({ block: false, src: src });
      return "%%FR_MATH_" + (maths.length - 1) + "%%";
    });

    var html = escapeHtml(t);

    var fences = [];
    html = html.replace(/```([\s\S]*?)```/g, function (_, code) {
      fences.push(code);
      return "%%FR_FENCE_" + (fences.length - 1) + "%%";
    });
    var inlines = [];
    html = html.replace(/`([^`\n]+)`/g, function (_, code) {
      inlines.push(code);
      return "%%FR_ICODE_" + (inlines.length - 1) + "%%";
    });

    html = html.replace(/^####\s+(.+)$/gm, "<h4>$1</h4>");
    html = html.replace(/^###\s+(.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^##\s+(.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/^#\s+(.+)$/gm, "<h1>$1</h1>");

    html = html.replace(/\*\*([^*\n][\s\S]*?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/(^|[^*\w])\*([^*\s][^*\n]*?)\*(?!\*)/g, "$1<em>$2</em>");

    html = html.replace(/%%FR_ICODE_(\d+)%%/g, function (_, i) {
      return "<code>" + inlines[+i] + "</code>";
    });
    html = html.replace(/%%FR_FENCE_(\d+)%%/g, function (_, i) {
      return "<pre><code>" + fences[+i] + "</code></pre>";
    });
    html = html.replace(/%%FR_MATH_(\d+)%%/g, function (_, i) {
      var m = maths[+i];
      var delim = m.block ? "$$" : "$";
      return '<span class="fr-math">' + delim + escapeHtml(m.src) + delim + "</span>";
    });
    return html;
  }

  function renderMathIn(el) {
    if (!el || !window.renderMathInElement) return;
    try {
      window.renderMathInElement(el, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$",  right: "$",  display: false },
        ],
        throwOnError: false,
        ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
      });
    } catch (e) { /* ignore */ }
  }

  function isPinnedToBottom(el) {
    if (!el) return true;
    return (el.scrollHeight - el.scrollTop - el.clientHeight) < 48;
  }

  function createTurnElement(role, content, time) {
    var div = document.createElement("div");
    div.className = "fr-turn " + (role || "user");
    var head = document.createElement("div");
    head.className = "fr-turn-head";
    var roleEl = document.createElement("span");
    roleEl.className = "fr-turn-role";
    roleEl.textContent = turnGlyphForRole(role);
    head.appendChild(roleEl);
    if (time) {
      var timeEl = document.createElement("span");
      timeEl.className = "fr-turn-time";
      timeEl.textContent = time;
      head.appendChild(timeEl);
    }
    var body = document.createElement("div");
    body.className = "fr-turn-body";
    body.innerHTML = renderMarkdown(content || "");
    renderMathIn(body);
    div.appendChild(head);
    div.appendChild(body);
    return div;
  }

  function formatMessageTime(m) {
    if (!m || !m.timestamp) return "";
    var d = new Date(m.timestamp);
    if (isNaN(d)) return "";
    return ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2) + ":" + ("0" + d.getSeconds()).slice(-2);
  }

  function renderTranscript(messages) {
    DOM.transcript.innerHTML = "";
    if (!messages || messages.length === 0) {
      var note = document.createElement("div");
      note.className = "fr-muted";
      note.style.padding = "8px 0";
      note.textContent = "no turns yet — start typing below.";
      DOM.transcript.appendChild(note);
      return;
    }
    messages.forEach(function (m) {
      DOM.transcript.appendChild(createTurnElement(m.role || "user", m.content || "", formatMessageTime(m)));
    });
    DOM.transcript.scrollTop = DOM.transcript.scrollHeight;
  }

  function renderSessionBar(session) {
    if (!session) {
      DOM.sessionBarId.textContent = "no session";
      DOM.sessionBarMeta.textContent = "—";
      DOM.sessionBarStatus.textContent = "● idle";
      DOM.sessionBarStatus.className = "fr-session-status";
      DOM.sessionBarCounter.textContent = "0 turns";
      DOM.composerSessionId.textContent = "—";
      DOM.sessionNameInput.value = "";
      DOM.sessionNameInput.disabled = true;
      DOM.sessionNameSave.disabled = true;
      if (DOM.sessionDeleteBtn) DOM.sessionDeleteBtn.disabled = true;
      return;
    }
    var label = session.display_name || session.slug || session.session_id || "";
    DOM.sessionBarId.textContent = "session " + label.slice(0, 32);
    DOM.sessionBarMeta.textContent = (session.provider || "?") + "/" + (session.model || "?");
    DOM.sessionBarStatus.textContent = "● live";
    DOM.sessionBarStatus.className = "fr-session-status live";
    var turns = session.message_count || (session.messages ? session.messages.length : 0);
    DOM.sessionBarCounter.textContent = turns + " turns";
    DOM.composerSessionId.textContent = label.slice(0, 24);
    DOM.sessionNameInput.value = session.display_name || session.slug || "";
    DOM.sessionNameInput.disabled = false;
    DOM.sessionNameSave.disabled = false;
    if (DOM.sessionDeleteBtn) DOM.sessionDeleteBtn.disabled = false;
  }

  function renderSessionSummary(session) {
    if (!session) {
      renderAssetList(null);
      renderAttachmentRow(null);
      return;
    }
    renderAssetList(session.assets || []);
    renderAttachmentRow(session.assets || []);
  }

  function fileKindFromName(name) {
    var lc = (name || "").toLowerCase();
    if (/\.(png|jpe?g|gif|webp|svg|bmp)$/.test(lc)) return "image";
    if (/\.pdf$/.test(lc)) return "pdf";
    if (/\.csv$/.test(lc)) return "csv";
    return "txt";
  }

  function formatBytes(n) {
    if (!n) return "0 B";
    if (n < 1024) return n + " B";
    if (n < 1024 * 1024) return (n / 1024).toFixed(1) + " KB";
    return (n / (1024 * 1024)).toFixed(1) + " MB";
  }

  function renderAttachmentRow(assets) {
    DOM.attachmentRow.innerHTML = "";
    if (!assets || assets.length === 0) return;
    assets.forEach(function (asset) {
      var chip = document.createElement("div");
      chip.className = "fr-chip-attach";
      var thumb = document.createElement("div");
      thumb.className = "fr-chip-thumb";
      var kind = fileKindFromName(asset.filename);
      if (kind === "image" && state.currentSessionId) {
        thumb.style.backgroundImage = "url('/api/sessions/" + encodeURIComponent(state.currentSessionId)
          + "/assets/" + encodeURIComponent(asset.filename) + "')";
      } else {
        thumb.textContent = kind;
      }
      var meta = document.createElement("div");
      meta.className = "fr-chip-meta";
      var name = document.createElement("span");
      name.className = "fr-chip-name";
      name.textContent = asset.filename || "asset";
      var size = document.createElement("span");
      size.className = "fr-chip-size";
      size.textContent = formatBytes(asset.size_bytes || 0);
      meta.appendChild(name);
      meta.appendChild(size);
      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "fr-chip-remove";
      remove.title = "remove";
      remove.textContent = "×";
      remove.addEventListener("click", function () { deleteAsset(asset.filename || ""); });
      chip.appendChild(thumb);
      chip.appendChild(meta);
      chip.appendChild(remove);
      DOM.attachmentRow.appendChild(chip);
    });
  }

  function renderAssetList(assets) {
    DOM.assetList.innerHTML = "";
    if (!assets || assets.length === 0) {
      DOM.assetList.textContent = "No uploaded files";
      return;
    }
    assets.forEach(function (asset) {
      var row = document.createElement("div");
      row.className = "asset-row";
      var link = document.createElement("a");
      link.className = "asset-link";
      link.href = "/api/sessions/" + encodeURIComponent(state.currentSessionId || "")
        + "/assets/" + encodeURIComponent(asset.filename || "");
      link.target = "_self";
      link.textContent = (asset.filename || "asset") + " · " + formatBytes(asset.size_bytes || 0);
      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "asset-remove";
      remove.textContent = "remove";
      remove.addEventListener("click", function () { deleteAsset(asset.filename || ""); });
      row.appendChild(link);
      row.appendChild(remove);
      DOM.assetList.appendChild(row);
    });
  }

  function deleteAsset(filename) {
    if (!state.currentSessionId || !filename) return;
    DOM.uploadStatus.textContent = "Removing " + filename + "…";
    api("/api/sessions/" + encodeURIComponent(state.currentSessionId)
      + "/assets/" + encodeURIComponent(filename), { method: "DELETE" })
      .then(function (res) { return res.json(); })
      .then(function () { return loadSession(state.currentSessionId); })
      .then(function (session) {
        state.currentSession = session;
        renderSessionSummary(session);
        renderSessionBar(session);
        DOM.uploadStatus.textContent = "removed " + filename;
      })
      .catch(function (err) {
        DOM.uploadStatus.textContent = "remove failed: " + err.message;
      });
  }

  function searchWeb(query) {
    if (!query || !query.trim()) {
      DOM.searchResults.textContent = "enter a query";
      return;
    }
    DOM.searchResults.textContent = "searching...";
    api("/api/search?q=" + encodeURIComponent(query.trim()))
      .then(function (res) { return res.json(); })
      .then(function (data) {
        var results = data.results || [];
        DOM.searchResults.innerHTML = "";
        if (results.length === 0) {
          DOM.searchResults.textContent = "no results";
          return;
        }
        results.forEach(function (r) {
          var row = document.createElement("div");
          row.className = "fr-search-row";
          var title = document.createElement("div");
          title.className = "fr-search-title";
          title.textContent = r.title || "untitled";
          var url = document.createElement("div");
          url.className = "fr-search-url";
          url.textContent = r.url || "";
          var snippet = document.createElement("div");
          snippet.className = "fr-search-snippet";
          snippet.textContent = r.snippet || "";
          row.appendChild(title);
          row.appendChild(url);
          row.appendChild(snippet);
          DOM.searchResults.appendChild(row);
        });
      })
      .catch(function (err) {
        DOM.searchResults.textContent = "search failed: " + err.message;
      });
  }

  function renderExtractionResult(result) {
    var el = document.getElementById("extraction-result");
    if (!el) {
      el = document.createElement("div");
      el.id = "extraction-result";
      el.className = "fr-read-body";
      el.style.marginTop = "8px";
      DOM.chatArea.appendChild(el);
    }
    el.textContent = JSON.stringify(result, null, 2);
  }

  function selectSession(id) {
    state.currentSessionId = id;
    setStatus("Loading session…", "status-info");
    setChatEnabled(false);
    loadSession(id).then(function (session) {
      state.currentSession = session;
      DOM.chatArea.classList.remove("hidden");
      if (DOM.chatEmpty) DOM.chatEmpty.classList.add("hidden");
      renderTranscript(session.messages);
      renderSessionBar(session);
      renderSessionSummary(session);
      setChatEnabled(true);
      if (state.runtimeReady) clearStatus();
      refreshSessionList();
    }).catch(function (err) {
      setStatus("Failed to load session: " + err.message, "status-error");
      renderSessionSummary(null);
      renderSessionBar(null);
    });
  }

  function sendMessage(content) {
    if (!state.currentSessionId) return;
    setStatus("Sending…", "status-info");
    var assistantText = "";
    var streamDone = false;

    var nowTime = (function () {
      var d = new Date();
      return ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2) + ":" + ("0" + d.getSeconds()).slice(-2);
    })();

    DOM.transcript.appendChild(createTurnElement("user", content, nowTime));
    var assistantTurn = createTurnElement("assistant", "", nowTime);
    var assistantBody = assistantTurn.querySelector(".fr-turn-body");
    DOM.transcript.appendChild(assistantTurn);
    // User just submitted -- pin them to bottom for the start of the stream.
    DOM.transcript.scrollTop = DOM.transcript.scrollHeight;

    function handleSSEEvents(events) {
      events.forEach(function (event) {
        var data = event.data || {};
        if (event.event === "token") {
          var pinned = isPinnedToBottom(DOM.transcript);
          assistantText += data.token || "";
          assistantBody.innerHTML = renderMarkdown(assistantText);
          if (pinned) DOM.transcript.scrollTop = DOM.transcript.scrollHeight;
        } else if (event.event === "done") {
          var pinnedDone = isPinnedToBottom(DOM.transcript);
          assistantBody.innerHTML = renderMarkdown(assistantText);
          renderMathIn(assistantBody);
          if (pinnedDone) DOM.transcript.scrollTop = DOM.transcript.scrollHeight;
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
            if (!streamDone) setStatus("Stream ended without done event", "status-error");
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
    setStatus("Extracting…", "status-info");
    api("/api/sessions/" + state.currentSessionId + "/extract", { method: "POST" })
      .then(function (res) { return res.json(); })
      .then(function (result) {
        renderExtractionResult(result);
        setStatus("Extraction complete", "status-success");
        loadSession(state.currentSessionId).then(function (session) {
          state.currentSession = session;
          renderSessionSummary(session);
          renderSessionBar(session);
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
    DOM.previewResult.textContent = "Loading…";
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
    DOM.matchmakerResult.textContent = "Running…";
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
          if (candidate.rationale) lines.push(candidate.rationale);
        });
        if (candidates.length === 0) lines.push("No candidates with the current fail-closed scorer.");
        DOM.matchmakerResult.textContent = lines.join("\n");
      })
      .catch(function (err) {
        DOM.matchmakerResult.textContent = "Error: " + err.message;
      });
  }

  function loadDocuments() { return api("/api/documents").then(function (res) { return res.json(); }); }
  function loadDocument(ref) { return api("/api/documents/" + encodeURIComponent(ref)).then(function (res) { return res.json(); }); }
  function loadSpaghetti() { return api("/api/spaghetti").then(function (res) { return res.json(); }); }
  function loadSpaghettiIdea(ideaId) { return api("/api/spaghetti/" + encodeURIComponent(ideaId)).then(function (res) { return res.json(); }); }

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
        if (!state.documentSelected && doc.ref === firstRef) el.classList.add("active");
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

  function ageString(idea) {
    var ts = idea.created_at || idea.captured_at || idea.touched_at;
    if (!ts) return "";
    var d = new Date(ts);
    if (isNaN(d)) return "";
    var diffMin = Math.max(0, Math.floor((Date.now() - d.getTime()) / 60000));
    if (diffMin < 60) return diffMin + "m";
    if (diffMin < 60 * 24) return Math.floor(diffMin / 60) + "h";
    return Math.floor(diffMin / (60 * 24)) + "d";
  }

  function colorForIdea(idea, i) {
    var pref = (idea.project_ref || idea.project || "").toLowerCase();
    if (pref.indexOf("museum") === 0) return "#6aa3ff";
    if (pref.indexOf("matchmaker") >= 0) return "#8fb84a";
    if (pref.indexOf("voice") >= 0) return "#5fb7c7";
    if (pref.indexOf("flightrecorder") === 0) return "#e8a04a";
    if (idea.is_private || pref.indexOf("private") >= 0) return "#e36363";
    return STICKY_COLORS[i % STICKY_COLORS.length];
  }

  function tagForIdea(idea) {
    if (idea.cross_project && idea.cross_project.length) {
      return "— (orphan) · cross: " + idea.cross_project.join(", ");
    }
    if (idea.project_ref) return idea.project_ref;
    if (idea.project) return idea.project;
    return "— (orphan)";
  }

  function renderSpaghettiGrid(ideas) {
    DOM.spaghettiGrid.innerHTML = "";
    var count = (ideas || []).length;
    DOM.spaghettiCountTitle.textContent = "spaghetti · " + count;
    if (count === 0) {
      var empty = document.createElement("div");
      empty.className = "fr-muted";
      empty.style.padding = "8px 4px";
      empty.style.fontSize = "11.5px";
      empty.textContent = "no loose ideas yet.";
      DOM.spaghettiGrid.appendChild(empty);
      return;
    }
    ideas.slice(0, 6).forEach(function (idea, i) {
      var note = document.createElement("div");
      note.className = "fr-sticky";
      note.style.transform = "rotate(" + (STICKY_ROTATIONS[i] || 0) + "deg)";
      note.style.borderLeftColor = colorForIdea(idea, i);
      if (state.spaghettiSelected && idea.idea_id === state.currentSpaghettiId) note.classList.add("active");

      var head = document.createElement("div");
      head.className = "fr-sticky-head";
      var titleEl = document.createElement("span");
      titleEl.className = "fr-sticky-title";
      titleEl.textContent = idea.title || (idea.idea_id || "").slice(0, 24) || "idea";
      var ageEl = document.createElement("span");
      ageEl.className = "fr-sticky-age";
      ageEl.textContent = ageString(idea);
      head.appendChild(titleEl);
      head.appendChild(ageEl);

      var bodyEl = document.createElement("div");
      bodyEl.className = "fr-sticky-body";
      bodyEl.textContent = (idea.body || idea.summary || "").slice(0, 260);

      var tagEl = document.createElement("div");
      tagEl.className = "fr-sticky-tag";
      var arrowEl = document.createElement("span");
      arrowEl.textContent = "↬";
      var tagTextEl = document.createElement("span");
      tagTextEl.textContent = tagForIdea(idea);
      tagEl.appendChild(arrowEl);
      tagEl.appendChild(tagTextEl);

      note.appendChild(head);
      note.appendChild(bodyEl);
      note.appendChild(tagEl);
      note.addEventListener("click", function () {
        state.spaghettiSelected = true;
        state.currentSpaghettiId = idea.idea_id;
        renderSpaghettiGrid(state.spaghetti);
        loadSpaghettiIdea(idea.idea_id).then(function (ideaData) {
          DOM.spaghettiBody.textContent = ideaData.body || "";
        }).catch(function (err) {
          DOM.spaghettiBody.textContent = "Error: " + err.message;
        });
        var items = DOM.spaghettiList.querySelectorAll("span");
        items.forEach(function (item) {
          item.classList.toggle("active", item.dataset.id === idea.idea_id);
        });
      });

      DOM.spaghettiGrid.appendChild(note);
    });
  }

  function refreshSpaghettiList() {
    loadSpaghetti().then(function (data) {
      var ideas = data.ideas || [];
      state.spaghetti = ideas;
      DOM.spaghettiList.innerHTML = "";
      renderSpaghettiGrid(ideas);
      if (ideas.length === 0) {
        DOM.spaghettiList.textContent = "No ideas";
        DOM.spaghettiBody.textContent = "";
        return;
      }
      var firstId = ideas[0].idea_id;
      ideas.forEach(function (idea) {
        var el = document.createElement("span");
        el.dataset.id = idea.idea_id;
        el.textContent = (idea.title || idea.idea_id).slice(0, 30);
        if (!state.spaghettiSelected && idea.idea_id === firstId) el.classList.add("active");
        if (state.spaghettiSelected && idea.idea_id === state.currentSpaghettiId) el.classList.add("active");
        el.addEventListener("click", function () {
          state.spaghettiSelected = true;
          state.currentSpaghettiId = idea.idea_id;
          var items = DOM.spaghettiList.querySelectorAll("span");
          items.forEach(function (item) { item.classList.remove("active"); });
          el.classList.add("active");
          renderSpaghettiGrid(state.spaghetti);
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
      DOM.spaghettiGrid.innerHTML = "";
    });
  }

  function refreshSessionList(autoSelect) {
    listSessions().then(function (data) {
      var sessions = data.sessions || data;
      state.sessions = sessions || [];
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
    setStatus("Creating session…", "status-info");
    createSession(provider, model, slug).then(function (session) {
      refreshSessionList();
      selectSession(session.session_id);
    }).catch(function (err) {
      setStatus("Failed to create session: " + err.message, "status-error");
    });
  });

  DOM.sessionNameForm.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!state.currentSessionId) return;
    var displayName = DOM.sessionNameInput.value.trim();
    if (!displayName) {
      setStatus("Session name is required", "status-error");
      return;
    }
    setStatus("Renaming session…", "status-info");
    renameSession(state.currentSessionId, displayName).then(function () {
      clearStatus();
      return loadSession(state.currentSessionId);
    }).then(function (session) {
      state.currentSession = session;
      renderSessionBar(session);
      renderSessionSummary(session);
      refreshSessionList();
    }).catch(function (err) {
      setStatus("Rename failed: " + err.message, "status-error");
    });
  });

  if (DOM.sessionDeleteBtn) {
    DOM.sessionDeleteBtn.addEventListener("click", function () {
      var id = state.currentSessionId;
      if (!id) return;
      var label = (state.currentSession && (state.currentSession.display_name || state.currentSession.slug)) || id;
      if (!window.confirm("Delete session \"" + label + "\"?\n\nRemoves the session file and uploaded assets. Keeps cost history and any extracted ideas.")) {
        return;
      }
      DOM.sessionDeleteBtn.disabled = true;
      setStatus("Deleting session…", "status-info");
      deleteSessionApi(id).then(function () {
        state.currentSessionId = null;
        state.currentSession = null;
        DOM.chatArea.classList.add("hidden");
        if (DOM.chatEmpty) DOM.chatEmpty.classList.remove("hidden");
        DOM.transcript.innerHTML = "";
        renderSessionBar(null);
        renderSessionSummary(null);
        setChatEnabled(false);
        clearStatus();
        refreshSessionList();
      }).catch(function (err) {
        setStatus("Delete failed: " + err.message, "status-error");
        DOM.sessionDeleteBtn.disabled = false;
      });
    });
  }

  DOM.messageForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var content = DOM.messageInput.value.trim();
    if (!content) return;
    DOM.messageInput.value = "";
    sendMessage(content);
  });

  DOM.messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      DOM.messageForm.requestSubmit();
    }
  });

  DOM.extractBtn.addEventListener("click", function () { runExtraction(); });

  DOM.uploadBtn.addEventListener("click", function () { DOM.uploadFile.click(); });

  DOM.uploadFile.addEventListener("change", function () {
    var file = DOM.uploadFile.files[0];
    if (!file || !state.currentSessionId) return;
    var formData = new FormData();
    formData.append("file", file);
    DOM.uploadStatus.textContent = "uploading " + file.name + "…";
    fetch("/api/sessions/" + state.currentSessionId + "/upload", {
      method: "POST",
      body: formData,
    }).then(function (res) {
      if (!res.ok) return res.text().then(function (text) { throw new Error(text); });
      return res.json();
    }).then(function (result) {
      DOM.uploadStatus.textContent = "uploaded " + file.name
        + " (" + result.image_count + " imgs)";
      loadSession(state.currentSessionId).then(function (session) {
        state.currentSession = session;
        renderSessionSummary(session);
        renderSessionBar(session);
      }).catch(function (err) {
        DOM.uploadStatus.textContent = "uploaded, refresh failed: " + err.message;
      });
    }).catch(function (err) {
      DOM.uploadStatus.textContent = "upload failed: " + err.message;
    });
  });

  DOM.previewSessionBtn.addEventListener("click", function () {
    if (!state.currentSessionId) { DOM.previewResult.textContent = "No session selected."; return; }
    fetchPublishPreview("session", state.currentSessionId);
  });

  DOM.previewDocBtn.addEventListener("click", function () {
    if (!state.currentDocRef) { DOM.previewResult.textContent = "No document selected."; return; }
    fetchPublishPreview("document", state.currentDocRef);
  });

  DOM.previewSpagBtn.addEventListener("click", function () {
    if (!state.currentSpaghettiId) { DOM.previewResult.textContent = "No spaghetti idea selected."; return; }
    fetchPublishPreview("spaghetti", state.currentSpaghettiId);
  });

  DOM.runMatchmakerBtn.addEventListener("click", function () {
    if (!state.currentSpaghettiId) { DOM.matchmakerResult.textContent = "No spaghetti idea selected."; return; }
    runMatchmakerForIdea(state.currentSpaghettiId);
  });

  DOM.searchForm.addEventListener("submit", function (e) {
    e.preventDefault();
    var query = DOM.searchInput.value;
    searchWeb(query);
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
          } catch (e) { /* skip unparseable data */ }
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
    renameSession: renameSession,
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
    searchWeb: searchWeb,
  };

  refreshSessionList(true);
  refreshBudget();
  refreshCalls();
  refreshRuntime();
  DOM.readPanels.classList.remove("hidden");
  refreshDocumentList();
  refreshSpaghettiList();
})();
