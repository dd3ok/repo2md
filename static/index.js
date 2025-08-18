
let API_BASE_URL = null;   
const sessionId = crypto.randomUUID(); // ✅ 세션 단위 repo 관리
let ws = null; // ✅ WebSocket 객체

// 서버에서 환경설정 불러오기
async function loadConfig() {
    try {
        const res = await fetch("/config");
        if (!res.ok) throw new Error("Config fetch failed");
        const cfg = await res.json();
        API_BASE_URL = cfg.API_URL;
        console.log("✅ Loaded API BASE URL:", API_BASE_URL);
    } catch (e) {
        console.error("❌ Failed to load config:", e);
        API_BASE_URL = "http://127.0.0.1:8000"; // fallback
    }
}

// 웹소켓 연결
function connectWebSocket() {
    const wsProtocol = (window.location.protocol === "https:") ? "wss://" : "ws://";
    ws = new WebSocket(`${wsProtocol}${window.location.host}/ws/${sessionId}`);

    ws.onopen = () => { console.log("🔌 WebSocket 연결됨:", sessionId); };
    ws.onmessage = (event) => {
        if (event.data === "pong") console.log("서버 pong 수신");
    };
    ws.onclose = () => { console.log("❌ WebSocket 닫힘"); };

    // 30초마다 ping
    setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send("ping");
        }
    }, 30000);
}


// ✅ 탭 닫을 때 disconnect 알림
window.addEventListener("beforeunload", () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send("disconnect");
        ws.close();
    }
});

// ✅ 초기화 실행
loadConfig().then(() => {
    connectWebSocket();

    // 이후 모든 form submit, export 버튼 처리 로직 → 기존 그대로
    const dom = {
        analyzeForm: document.getElementById('analyze-form'),
        analyzeBtn: document.getElementById('analyze-btn'),
        repoUrlInput: document.getElementById('repo-url-input'),
        errorMessage: document.getElementById('error-message'),
        analysisResult: document.getElementById('analysis-result'),
        repoNameDisplay: document.getElementById('repo-name-display'),
        extsContainer: document.getElementById('exts-container'),
        extsSelectAll: document.getElementById('exts-select-all'),
        treeContainer: document.getElementById('tree-container'),
        exportJsonBtn: document.getElementById('export-json-btn'),
        exportFileBtn: document.getElementById('export-file-btn'),
        modalOverlay: document.getElementById('modal-overlay'),
        modalClose: document.getElementById('modal-close'),
        markdownPreview: document.getElementById('markdown-preview'),
        copyButton: document.getElementById('copy-button'),
    };

    let analysisData = {};

    function setLoading(button, isLoading) {
        const buttonText = button.querySelector('span');
        if (isLoading) {
            button.disabled = true;
            if (buttonText) buttonText.style.display = 'none';
            const loader = document.createElement('div');
            loader.className = 'loader';
            button.prepend(loader);
        } else {
            button.disabled = false;
            const loader = button.querySelector('.loader');
            if (loader) loader.remove();
            if (buttonText) buttonText.style.display = 'inline';
        }
    }

    function showError(message) {
        dom.errorMessage.textContent = message;
        dom.errorMessage.style.display = 'block';
    }
    function hideError() { dom.errorMessage.style.display = 'none'; }

    function createExtCheckbox(id, value, checked = true) {
        const wrapper = document.createElement('div');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'ext-checkbox';
        checkbox.id = id;
        checkbox.value = value;
        checkbox.checked = checked;
        const labelEl = document.createElement('label');
        labelEl.htmlFor = id;
        labelEl.textContent = value;
        wrapper.appendChild(checkbox);
        wrapper.appendChild(labelEl);
        return wrapper;
    }

    function renderInteractiveTree(node, container) {
        const li = document.createElement('li');
        const label = document.createElement('label');
        label.className = 'tree-item-label';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = node.path;
        checkbox.checked = true;
        checkbox.dataset.type = node.type;
        const span = document.createElement('span');
        span.className = node.type === 'directory' ? 'dir-item' : 'file-item';
        span.textContent = node.name;
        label.appendChild(checkbox); label.appendChild(span);
        li.appendChild(label);
        if (node.type === 'directory' && node.children?.length > 0) {
            const ul = document.createElement('ul');
            node.children.forEach(child => renderInteractiveTree(child, ul));
            li.appendChild(ul);
        }
        container.appendChild(li);
    }

    function syncExtensionsFromTree() {
        const checkedFiles = dom.treeContainer.querySelectorAll('input[data-type="file"]:checked');
        const activeExtensions = new Set();
        checkedFiles.forEach(fileCheckbox => {
            const ext = fileCheckbox.value.split('.').pop();
            if (ext && fileCheckbox.value.includes('.')) {
                activeExtensions.add(`.${ext}`);
            }
        });
        const allExtCheckboxes = dom.extsContainer.querySelectorAll('.ext-checkbox');
        allExtCheckboxes.forEach(extCheckbox => {
            extCheckbox.checked = activeExtensions.has(extCheckbox.value);
        });
        const allChecked = Array.from(allExtCheckboxes).every(cb => cb.checked);
        dom.extsSelectAll.checked = allChecked;
    }

    async function handleExport(type) {
        const selectedExts = Array.from(dom.extsContainer.querySelectorAll('.ext-checkbox:checked')).map(el => el.value);
        const selectedDirs = Array.from(dom.treeContainer.querySelectorAll('input[data-type="directory"]:checked')).map(el => el.value);
        const exportBtn = (type === 'json') ? dom.exportJsonBtn : dom.exportFileBtn;
        setLoading(exportBtn, true);
        try {
            const response = await fetch(`${API_BASE_URL}/export/${type}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Session-Id': sessionId },
                body: JSON.stringify({
                    repo_name: analysisData.repo_name,
                    exts: selectedExts,
                    dirs: selectedDirs,
                })
            });
            if (!response.ok) throw new Error((await response.json()).detail || '내보내기에 실패했습니다.');
            if (type === 'file') {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none'; a.href = url;
                const contentDisposition = response.headers.get('content-disposition');
                let filename = `${analysisData.repo_name}_export.md`;
                if (contentDisposition) {
                    const match = contentDisposition.match(/filename="?([^"]+)"?/);
                    if (match && match.length > 1) filename = match[1];
                }
                a.download = filename;
                document.body.appendChild(a); a.click();
                window.URL.revokeObjectURL(url); a.remove();
            } else {
                const data = await response.json();
                dom.markdownPreview.textContent = data.content;
                dom.modalOverlay.style.display = 'flex';
            }
        } catch (error) {
            showError(`내보내기 오류: ${error.message}`);
        } finally {
            setLoading(exportBtn, false);
        }
    }

    dom.analyzeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();
        setLoading(dom.analyzeBtn, true);
        dom.analysisResult.style.display = 'none';
        try {
            const response = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-Session-Id': sessionId },
                body: JSON.stringify({ repo_url: dom.repoUrlInput.value })
            });
            if (!response.ok) throw new Error((await response.json()).detail || '분석에 실패했습니다.');
            analysisData = await response.json();
            dom.repoNameDisplay.textContent = analysisData.repo_name;
            dom.extsContainer.innerHTML = '';
            analysisData.extensions.forEach((ext, i) => {
                dom.extsContainer.appendChild(createExtCheckbox(`ext-${i}`, ext));
            });
            dom.extsSelectAll.checked = true;
            dom.treeContainer.innerHTML = '';
            if (analysisData.dirs_tree) {
                const rootUl = document.createElement('ul');
                renderInteractiveTree(analysisData.dirs_tree, rootUl);
                dom.treeContainer.appendChild(rootUl);
            }
            dom.analysisResult.style.display = 'flex';
        } catch (error) {
            showError(`오류: ${error.message}`);
        } finally {
            setLoading(dom.analyzeBtn, false);
        }
    });

    dom.treeContainer.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox') {
            const li = e.target.closest('li');
            const childCheckboxes = li.querySelectorAll('ul input[type="checkbox"]');
            childCheckboxes.forEach(child => { child.checked = e.target.checked; });
            syncExtensionsFromTree();
        }
    });

    dom.extsContainer.addEventListener('change', (e) => {
        if (e.target.classList.contains('ext-checkbox')) {
            const extCheckbox = e.target;
            const extension = extCheckbox.value;
            const isChecked = extCheckbox.checked;
            const allFileCheckboxes = dom.treeContainer.querySelectorAll('input[data-type="file"]');
            allFileCheckboxes.forEach(fileCheckbox => {
                if (fileCheckbox.value.endsWith(extension)) {
                    fileCheckbox.checked = isChecked;
                }
            });
            const allExts = dom.extsContainer.querySelectorAll('.ext-checkbox');
            const allChecked = Array.from(allExts).every(cb => cb.checked);
            dom.extsSelectAll.checked = allChecked;
        }
    });

    dom.extsSelectAll.addEventListener('change', () => {
        const isChecked = dom.extsSelectAll.checked;
        dom.extsContainer.querySelectorAll('.ext-checkbox').forEach(cb => { cb.checked = isChecked; });
        dom.treeContainer.querySelectorAll('input[data-type="file"]').forEach(cb => { cb.checked = isChecked; });
        dom.treeContainer.querySelectorAll('input[data-type="directory"]').forEach(cb => { cb.checked = isChecked; });
    });

    dom.exportJsonBtn.addEventListener('click', () => handleExport('json'));
    dom.exportFileBtn.addEventListener('click', () => handleExport('file'));
    dom.modalClose.addEventListener('click', () => { dom.modalOverlay.style.display = 'none'; });
    dom.copyButton.addEventListener('click', () => {
        navigator.clipboard.writeText(dom.markdownPreview.textContent).then(() => {
            dom.copyButton.textContent = '복사 완료!';
            setTimeout(() => { dom.copyButton.textContent = '클립보드에 복사'; }, 2000);
        }, () => {
            dom.copyButton.textContent = '복사 실패';
            setTimeout(() => { dom.copyButton.textContent = '클립보드에 복사'; }, 2000);
        });
    });
    dom.modalOverlay.addEventListener('click', (e) => {
        if (e.target === dom.modalOverlay) dom.modalOverlay.style.display = 'none';
    });
});