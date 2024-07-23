window.addEventListener('DOMContentLoaded', (event) => {
    const resultDiv = document.getElementById('result');
    let recognition;

    // Check for browser support
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
    } else if ('SpeechRecognition' in window) {
        recognition = new SpeechRecognition();
    } else {
        alert('Your browser does not support the Web Speech API');
        return;
    }

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = 0; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        resultDiv.innerHTML = finalTranscript + '<span style="color: #ccc;">' + interimTranscript + '</span>';
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error detected: ' + event.error);
    };

    window.addEventListener('keydown', (event) => {
        if (event.code === 'Space') {
            recognition.start();
        }
    });

    window.addEventListener('keyup', (event) => {
        if (event.code === 'Space') {
            recognition.stop();
        }
    });
});
