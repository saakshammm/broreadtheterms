document.addEventListener('DOMContentLoaded', () => {
    // DOM refs
    const textarea = document.getElementById('policy-text');
    const analyzeBtn = document.getElementById('analyze-btn');
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const fileUploadBtn = document.getElementById('file-upload-btn');
    const fileNameSpan = document.getElementById('file-name');
    const statusEl = document.getElementById('status');
    const resultsSection = document.getElementById('results');
    const cookedScoreEl = document.getElementById('cooked-score');
    const scoreVerdictEl = document.getElementById('score-verdict');
    const summaryEl = document.getElementById('summary');
    const redFlagsList = document.getElementById('red-flags-list');
    const honestTranslationEl = document.getElementById('honest-translation');
    const privacyRiskEl = document.getElementById('privacy-risk');
    const subTrapEl = document.getElementById('sub-trap');
    const realMeaningsList = document.getElementById('real-meanings');

    let selectedFile = null;

    // file drop zone events
    dropZone.addEventListener('click', (e) => {
        if (e.target === fileUploadBtn) return; // button handles click
        fileInput.click();
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) handleFile(files[0]);
    });
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) handleFile(fileInput.files[0]);
    });

    function handleFile(file) {
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        const allowed = ['.txt','.pdf','.docx'];
        if (!allowed.includes(ext)) {
            showStatus('We only take .txt, .pdf, or .docx. Stop trying to break us.', true);
            return;
        }
        selectedFile = file;
        fileNameSpan.textContent = file.name;
    }

    // status message helpers
    const loadingMessages = [
        "Scanning your soul‑selling contract…",
        "Extracting corporate nonsense…",
        "Roasting the fine print…",
        "Polishing the red flags…",
        "Cooking the legal garbage…"
    ];
    function randomLoadingMsg() {
        return loadingMessages[Math.floor(Math.random() * loadingMessages.length)];
    }

    function showStatus(msg, isError = false) {
        statusEl.textContent = msg;
        statusEl.style.color = isError ? '#ff4d4d' : '';
    }

    // button loading state
    function setLoading(loading) {
        const btnText = analyzeBtn.querySelector('.btn-text');
        const loader = analyzeBtn.querySelector('.loader');
        analyzeBtn.disabled = loading;
        btnText.textContent = loading ? 'Roasting…' : 'Roast This Policy';
        loader.hidden = !loading;
    }

    // score counter animation
    function animateScore(target) {
        const duration = 800;
        const start = performance.now();
        const from = 0;
        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const current = Math.floor(from + (target - from) * progress);
            cookedScoreEl.textContent = current + '%';
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }

    // render results
    function render(data) {
        // cooked score & verdict
        animateScore(data.cooked_score);
        const s = data.cooked_score;
        let verdict = s <= 20 ? "almost human. almost." :
                      s <= 40 ? "a few red flags but nothing new." :
                      s <= 60 ? "standard corporate hunger." :
                      s <= 80 ? "they want your soul (and data)." :
                      "generational levels of corporate greed.";
        scoreVerdictEl.textContent = verdict;

        summaryEl.textContent = data.summary || "Couldn’t summarise — too much evil.";

        redFlagsList.innerHTML = '';
        (data.red_flags || []).forEach(flag => {
            const li = document.createElement('li');
            li.textContent = '• ' + flag;
            redFlagsList.appendChild(li);
        });

        honestTranslationEl.textContent = data.honest_translation || "Nothing honest to say. That’s suspicious.";

        privacyRiskEl.textContent = data.privacy_risk || 'UNKNOWN';
        subTrapEl.textContent = data.subscription_trap_difficulty || 'NOT APPLICABLE';

        realMeaningsList.innerHTML = '';
        const meanings = data.what_they_really_mean || {};
        Object.entries(meanings).forEach(([phrase, trans]) => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>“${phrase}”</strong> → ${trans}`;
            realMeaningsList.appendChild(li);
        });

        resultsSection.hidden = false;
        resultsSection.classList.add('visible');
    }

    // submit handler
    async function submit() {
        const text = textarea.value.trim();
        if (!text && !selectedFile) {
            showStatus('Paste some legal garbage or drop a file first.', true);
            return;
        }

        setLoading(true);
        showStatus(randomLoadingMsg());
        resultsSection.hidden = true;
        resultsSection.classList.remove('visible');

        try {
            let response;
            if (selectedFile) {
                const formData = new FormData();
                formData.append('file', selectedFile);
                response = await fetch('/api/upload', { method:'POST', body: formData });
            } else {
                response = await fetch('/api/analyze', {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({ text })
                });
            }
            if (!response.ok) {
                const err = await response.json();
                showStatus(err.detail || 'Something went wrong.', true);
                return;
            }
            const data = await response.json();
            render(data);
            const src = selectedFile ? `Extracted from ${data.extracted_from}` : '';
            showStatus(src);
        } catch (e) {
            showStatus('Network error. Try again later. The corporate overlords are winning.', true);
        } finally {
            setLoading(false);
        }
    }

    analyzeBtn.addEventListener('click', submit);
    // optional: submit on Ctrl+Enter
    textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) submit();
    });
});
