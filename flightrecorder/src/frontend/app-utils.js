(function () {
  "use strict";

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

  window.flightrecorderUtils = {
    createSSEParser: createSSEParser,
  };
}());
