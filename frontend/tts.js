function speak(text) {
    if (!window.speechSynthesis) return;
    var u = new SpeechSynthesisUtterance(String(text));
    u.rate = 1;
    u.pitch = 1;
    speechSynthesis.cancel();
    speechSynthesis.speak(u);
}