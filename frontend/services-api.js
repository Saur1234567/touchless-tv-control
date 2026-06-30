async function sendVoiceCommand(text) {
    var payload = JSON.stringify({ text: String(text || "").trim() });
    console.log("[VOICE SEND]", payload);
    var res = await fetch(CONFIG.API_BASE + "/voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload
    });
    var json = await res.json();
    console.log("[VOICE RECV]", json);
    return json;
}

async function sendGestureCommand(gesture) {
    var payload;
    if (Array.isArray(gesture)) {
        payload = JSON.stringify({ gesture: gesture });
    } else if (typeof gesture === "object" && gesture !== null) {
        payload = JSON.stringify(gesture); // cursor dict
    } else {
        payload = JSON.stringify({ gesture: String(gesture) });
    }
    var res = await fetch(CONFIG.API_BASE + "/gesture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload
    });
    var json = await res.json();
    return json;
}

// ═══════════════════════════════════════════
// LIVE LOG — Socket.IO real-time update
// ═══════════════════════════════════════════
(function() {
    try {
        // /api hata ke sirf base URL lo — socket.io wahan connect hota hai
        var socketUrl = CONFIG.API_BASE.replace("/api", "");

        var socket = io(socketUrl);

        socket.on("connect", function() {
            addLog("📡 Live log connected", "success");
        });

        socket.on("disconnect", function() {
            addLog("📡 Live log disconnected", "error");
        });

        socket.on("live_log", function(d) {
            if (d.source === "voice") {
                window.addVoiceEvent && addVoiceEvent(d.action, d.result);
            } else {
                window.addGestureEvent && addGestureEvent(d.action, d.result);
            }
        });

    } catch (e) {
        console.warn("Live log connect nahi hua:", e);
    }
})();