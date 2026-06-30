// ═══════════════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════════════
var voiceActive = false;
var gestureActive = false;
var recognition = null;
var hands = null;
var camera = null;
var gestureCooldown = false;
var lastGesture = "";
var gestureFrames = 0;
var frameCount = 0;
var cursorMode = true; // ON by default
var SR = null;
var voiceTimer = null;

// Smooth cursor — exponential moving average
var smoothX = 0.5,
    smoothY = 0.5;

// Pinch state — track enter/exit to fire only ONCE per pinch
var wasPinching = false;

// ═══════════════════════════════════════════════════════════
// AUTO RESTART VOICE on tab focus
// ═══════════════════════════════════════════════════════════
document.addEventListener("visibilitychange", function() {
    if (document.visibilityState === "visible" && voiceActive) {
        clearTimeout(voiceTimer);
        voiceTimer = setTimeout(nextListen, 400);
    }
});
window.addEventListener("focus", function() {
    if (voiceActive) {
        clearTimeout(voiceTimer);
        voiceTimer = setTimeout(nextListen, 400);
    }
});

// ═══════════════════════════════════════════════════════════
// UI
// ═══════════════════════════════════════════════════════════
function addLog(msg, type) {
    var el = document.getElementById("log");
    var row = document.createElement("div");
    row.className = "log-row " + (type || "info");
    row.textContent = "[" + new Date().toLocaleTimeString() + "] " + msg;
    el.insertBefore(row, el.firstChild);
    if (el.children.length > 80) el.removeChild(el.lastChild);
}

function setLastCmd(text, type) {
    var el = document.getElementById("last-command");
    el.textContent = text;
    el.className = "last-cmd " + (type || "");
}

function setVoiceBtn(on) {
    var b = document.getElementById("btn-voice");
    b.classList.toggle("active", on);
    document.getElementById("dot-voice").classList.toggle("live", on);
    b.querySelector(".btn-label").textContent = on ?
        "🎤 Voice: ON (click to stop)" : "🎤 Voice: OFF";
}

function setGestureBtn(on) {
    var b = document.getElementById("btn-gesture");
    b.classList.toggle("active", on);
    document.getElementById("dot-gesture").classList.toggle("live", on);
    b.querySelector(".btn-label").textContent = on ?
        "✋ Gesture: ON (click to stop)" : "✋ Gesture: OFF";
}

function niceMsg(s) {
    return (s || "done").replace(/^done:\s*/i, "").replace(/_/g, " ").toLowerCase();
}

// Set cursor button state on load
window.addEventListener("load", function() {
    var b = document.getElementById("btn-cursor");
    if (b) {
        b.classList.add("active");
        b.textContent = "🖱 Cursor Mode: ON";
    }
});

// ═══════════════════════════════════════════════════════════
// VOICE
// ═══════════════════════════════════════════════════════════
function toggleVoice() { voiceActive ? stopVoice() : startVoice(); }

function startVoice() {
    SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { addLog("❌ Speech recognition not supported", "error"); return; }
    voiceActive = true;
    setVoiceBtn(true);
    addLog("🎤 Voice ON — bolo command", "success");
    nextListen();
}

function nextListen() {
    clearTimeout(voiceTimer);
    if (!voiceActive || !SR) return;
    if (recognition) {
        try { recognition.abort(); } catch (e) {}
        recognition = null;
    }

    var r = new SR();
    r.lang = "en-US";
    r.continuous = false;
    r.interimResults = false;
    r.maxAlternatives = 3;
    recognition = r;
    var done = false;

    r.onresult = function(e) {
        if (done) return;
        done = true;
        recognition = null;

        var best = "",
            conf = 0;
        var alts = e.results[0];
        for (var i = 0; i < alts.length; i++) {
            if (alts[i].confidence >= conf) {
                conf = alts[i].confidence;
                best = alts[i].transcript.trim().toLowerCase();
            }
        }
        if (!best) { voiceTimer = setTimeout(nextListen, 300); return; }

        addLog("🗣 \"" + best + "\" (" + Math.round(conf * 100) + "%)", "info");
        setLastCmd("🎤 Processing: " + best + "…", "voice");

        sendVoiceCommand(best)
            .then(function(d) {
                var msg = niceMsg(d.action);
                setLastCmd("🎤 \"" + best + "\"  →  " + msg, "voice");
                addLog("✅ " + msg, "success");
                speak(msg);
            })
            .catch(function(err) {
                addLog("❌ " + err.message, "error");
                setLastCmd("❌ Backend not reachable", "error");
            })
            .finally(function() {
                voiceTimer = setTimeout(nextListen, 1500);
            });
    };

    r.onerror = function(e) {
        if (done) return;
        recognition = null;
        if (e.error === "no-speech") { voiceTimer = setTimeout(nextListen, 200); return; }
        if (e.error === "aborted") { voiceTimer = setTimeout(nextListen, 200); return; }
        if (e.error === "network") { voiceTimer = setTimeout(nextListen, 1000); return; }
        if (e.error === "not-allowed") { stopVoice(); return; }
        addLog("Voice error: " + e.error, "error");
        voiceTimer = setTimeout(nextListen, 1500);
    };

    r.onend = function() {
        if (!done && voiceActive) {
            recognition = null;
            voiceTimer = setTimeout(nextListen, 200);
        }
    };

    try { r.start(); } catch (e) {
        recognition = null;
        voiceTimer = setTimeout(nextListen, 800);
    }
}

function stopVoice() {
    voiceActive = false;
    clearTimeout(voiceTimer);
    if (recognition) {
        try { recognition.abort(); } catch (e) {}
        recognition = null;
    }
    setVoiceBtn(false);
    addLog("🎤 Voice stopped", "info");
}

// ═══════════════════════════════════════════════════════════
// GESTURE
// ═══════════════════════════════════════════════════════════
function toggleGesture() { gestureActive ? stopGesture() : startGesture(); }

function startGesture() {
    if (!window.Hands) { addLog("❌ MediaPipe not loaded", "error"); return; }

    var video = document.getElementById("gesture-video");
    var canvas = document.getElementById("gesture-canvas");
    var ctx = canvas.getContext("2d");

    hands = new Hands({
        locateFile: function(f) {
            return "https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1646424915/" + f;
        }
    });
    hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.6
    });

    hands.onResults(function(res) {
        frameCount++;

        // Mirror draw
        ctx.save();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.scale(-1, 1);
        ctx.translate(-canvas.width, 0);
        ctx.drawImage(res.image, 0, 0, canvas.width, canvas.height);
        ctx.restore();

        if (!res.multiHandLandmarks || !res.multiHandLandmarks.length) {
            document.getElementById("gesture-name").textContent = "— no hand —";
            document.getElementById("cursor-pos").textContent = "";
            gestureFrames = 0;
            lastGesture = "";
            wasPinching = false;
            return;
        }

        // Mirror x
        var lm = res.multiHandLandmarks[0].map(function(p) {
            return { x: 1 - p.x, y: p.y, z: p.z };
        });

        // Draw skeleton
        if (window.drawConnectors && window.HAND_CONNECTIONS) {
            drawConnectors(ctx, lm, HAND_CONNECTIONS, { color: "#00e5ff", lineWidth: 2 });
            drawLandmarks(ctx, lm, { color: "#ff9800", lineWidth: 1, radius: 3 });
        }

        var g = detectGesture(lm);
        document.getElementById("gesture-name").textContent = g || "—";

        // ══════════════════════════════════════════════════
        // CURSOR MODE — index finger tip moves OS mouse
        // Works on YouTube, Netflix, any app, any window
        // ══════════════════════════════════════════════════
        if (cursorMode) {

            var ix = lm[8].x; // 0=left, 1=right
            var iy = lm[8].y; // 0=top,  1=bottom

            // Smooth movement — lower alpha = smoother but slower
            smoothX += (ix - smoothX) * 0.35;
            smoothY += (iy - smoothY) * 0.35;

            // Show cursor position
            document.getElementById("cursor-pos").textContent =
                "🖱 " + Math.round(smoothX * 100) + "%, " + Math.round(smoothY * 100) + "%";

            // Move mouse every frame (duration=0 = instant)
            if (frameCount % 2 === 0) {
                sendGestureCommand({
                    action: "MOVE_CURSOR",
                    x: smoothX,
                    y: smoothY
                }).catch(function() {});
            }

            // ── PINCH = CLICK (only on pinch entry, not hold) ──
            var isPinching = (g === "PINCH");
            if (isPinching && !wasPinching) {
                // Just entered pinch — fire click ONCE
                wasPinching = true;
                addLog("🤏 Pinch → Click", "info");
                sendGestureCommand("CLICK")
                    .then(function(d) {
                        var msg = niceMsg(d.action);
                        setLastCmd("🤏 Pinch → " + msg, "gesture");
                        addLog("✅ " + msg, "success");
                    })
                    .catch(function() {});
            } else if (!isPinching) {
                wasPinching = false; // reset when hand opens
            }

            // Non-cursor gestures still work in cursor mode
            // but only if NOT pinching (to avoid conflicts)
            if (!isPinching && g && g !== "POINTING") {
                handleNonCursorGesture(g, lm);
            }
            return;
        }

        // ── Non cursor mode: stability gate ───────────────────
        if (!g) {
            gestureFrames = 0;
            lastGesture = "";
            return;
        }
        if (g !== lastGesture) {
            lastGesture = g;
            gestureFrames = 1;
            return;
        }
        gestureFrames++;
        if (gestureFrames < 12) return;
        if (!gestureCooldown) {
            gestureFrames = 0;
            fireGesture(g, lm);
        }
    });

    camera = new Camera(video, {
        onFrame: async function() { if (hands) await hands.send({ image: video }); },
        width: 320,
        height: 240
    });

    camera.start().then(function() {
        gestureActive = true;
        setGestureBtn(true);
        document.getElementById("camera-box").style.display = "flex";
        addLog("✋ Gesture ON — cursor mode active", "success");
        addLog("💡 Point finger = move mouse | Pinch = click | Thumbs up = vol up", "info");
    }).catch(function(e) {
        addLog("❌ Camera: " + e.message, "error");
    });
}

// Non-cursor gestures (volume, playback etc.) with stability gate
var ncLastGesture = "",
    ncFrames = 0;

function handleNonCursorGesture(g, lm) {
    if (g !== ncLastGesture) {
        ncLastGesture = g;
        ncFrames = 1;
        return;
    }
    ncFrames++;
    if (ncFrames < 15) return; // must hold 15 frames
    if (gestureCooldown) return;
    ncFrames = 0;
    fireGesture(g, lm);
}

function fireGesture(g, lm) {
    if (gestureCooldown) return;
    gestureCooldown = true;
    setTimeout(function() { gestureCooldown = false; }, 2000);
    addLog("✋ " + g, "info");

    sendGestureCommand(lm)
        .then(function(d) {
            var msg = niceMsg(d.action);
            setLastCmd("✋ " + g + "  →  " + msg, "gesture");
            addLog("✅ " + msg, "success");
            speak(msg);
        })
        .catch(function(err) {
            addLog("❌ Backend: " + err.message, "error");
        });
}

function stopGesture() {
    gestureActive = false;
    if (camera) {
        try { camera.stop(); } catch (e) {}
        camera = null;
    }
    if (hands) {
        try { hands.close(); } catch (e) {}
        hands = null;
    }
    setGestureBtn(false);
    document.getElementById("camera-box").style.display = "none";
    document.getElementById("gesture-name").textContent = "—";
    addLog("✋ Gesture stopped", "info");
}

// ═══════════════════════════════════════════════════════════
// GESTURE DETECTOR
// ═══════════════════════════════════════════════════════════
function detectGesture(lm) {
    function ext(t, p) { return lm[t].y < lm[p].y; }

    var i = ext(8, 6);
    var m = ext(12, 10);
    var r = ext(16, 14);
    var p = ext(20, 18);
    var up = [i, m, r, p].filter(Boolean).length;

    var W = lm[0]; // wrist
    var T = lm[4]; // thumb tip
    var TI = lm[3]; // thumb IP
    var TM = lm[2]; // thumb MCP (base)

    // ── THUMB direction — flip ke baad ──────────────────────

    var tOut = T.x < TM.x - 0.02;

    // ── FIVE FINGER (open palm) ─────────────────────────────────────────────
    if (up === 4 && tOut) return "OPEN_HAND";

    // ── FOUR FINGERS — thumb andar, chaaron bahar ──────────
    if (up === 4 && !tOut) return "FOUR_FINGERS";

    // ── THREE FINGERS ──────────────────────────────────────
    if (i && m && r && !p) return "THREE_FINGERS";

    // ── TWO FINGERS ────────────────────────────────────────
    if (i && m && !r && !p) return "TWO_FINGERS";

    // ── ROCK — index + pinky ───────────────────────────────
    if (i && !m && !r && p) return "ROCK";

    // ── POINTING — sirf index ──────────────────────────────
    if (i && !m && !r && !p) return "POINTING";

    // ── PINCH — up===0 se pehle check karo ────────────────
    var dx = Math.abs(T.x - lm[8].x);
    var dy = Math.abs(T.y - lm[8].y);
    if (dx < 0.09 && dy < 0.09 && !m && !r) return "PINCH";

    // ── Yahan se sirf up===0 wale cases hain ──────────────

    // THUMBS UP: 
    if (up === 0 && T.y < W.y - 0.10 && T.y < TM.y) return "THUMBS_UP";

    // THUMBS DOWN:
    // Condition 1 — tip wrist se BAHUT neeche
    // Condition 2 — thumb vertically downward (tip, MCP se neeche)
    if (up === 0 && T.y > W.y + 0.08 && T.y > TM.y) return "THUMBS_DOWN";

    // FIST — up===0, thumb andar
    if (up === 0 && !tOut) return "FIST";

    return null;
}

// ═══════════════════════════════════════════════════════════
// QUICK BUTTONS
// ═══════════════════════════════════════════════════════════
function quickCmd(action) {
    addLog("🖱 " + action, "info");
    sendGestureCommand(action)
        .then(function(d) {
            var msg = niceMsg(d.action);
            setLastCmd("🖱 " + action + "  →  " + msg, "gesture");
            addLog("✅ " + msg, "success");
            speak(msg);
        })
        .catch(function() {
            setLastCmd("❌ Backend not reachable", "error");
            addLog("❌ Backend not reachable", "error");
        });
}

// ═══════════════════════════════════════════════════════════
// CURSOR MODE TOGGLE
// ═══════════════════════════════════════════════════════════
function toggleCursorMode() {
    cursorMode = !cursorMode;
    var b = document.getElementById("btn-cursor");
    b.classList.toggle("active", cursorMode);
    b.textContent = cursorMode ? "🖱 Cursor Mode: ON" : "🖱 Cursor Mode: OFF";
    wasPinching = false;
    addLog(cursorMode ?
        "🖱 Cursor ON — point=mouse move, pinch=click" :
        "🖱 Cursor OFF", "info");
}