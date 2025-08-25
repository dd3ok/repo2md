// static/index.js

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

// 웹소켓 연결 함수 수정
function connectWebSocket() {
    const wsProtocol = (window.location.protocol === "https:") ? "wss://" : "ws://";
    ws = new WebSocket(`${wsProtocol}${window.location.host}/ws/${sessionId}`);

    ws.onopen = () => { 
        console.log("🔌 WebSocket 연결됨:", sessionId); 
    };
    
    ws.onmessage = (event) => {
        if (event.data === "pong") console.log("서버 pong 수신");
    };
    
    ws.onclose = () => { 
        console.log("❌ WebSocket 닫힘"); 
        // 연결이 끊어지면 재연결 시도하지 않음 (세션 종료로 간주)
    };
    
    ws.onerror = (error) => {
        console.error("WebSocket 에러:", error);
    };

    // 30초마다 ping (연결 유지 확인)
    const pingInterval = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send("ping");
        } else {
            clearInterval(pingInterval);
        }
    }, 30000);
}

window.addEventListener("pagehide", (event) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send("disconnect");
        ws.close();
    }
});

// ✅ 초기화 실행
loadConfig().then(() => {
    connectWebSocket();

    // DOM 캐시
    const dom = {
        // 공통
        errorMessage: document.getElementById('error-message'),
        analysisResult: document.getElementById('analysis-result'),
        repoNameDisplay: document.getElementById('repo-name-display'),
        extsContainer: document.getElementById('exts-container'),
        extsSelectAll: document.getElementById('exts-select-all'),
        treeContainer: document.getElementById('tree-container'),
        exportTextBtn: document.getElementById('export-text-btn'),
        exportFileBtn: document.getElementById('export-file-btn'),
        modalOverlay: document.getElementById('modal-overlay'),
        modalClose: document.getElementById('modal-close'),
        markdownPreview: document.getElementById('markdown-preview'),
        copyButton: document.getElementById('copy-button'),

        // Git URL 분석
        analyzeForm: document.getElementById('analyze-form'),
        analyzeBtn: document.getElementById('analyze-btn'),
        repoUrlInput: document.getElementById('repo-url-input'),

        // ZIP 업로드 분석
        analyzeZipForm: document.getElementById('analyze-zip-form'),
        analyzeZipBtn: document.getElementById('analyze-zip-btn'),
        repoZipInput: document.getElementById('repo-zip-input'),
        zipProgress: document.getElementById('zip-progress'),
        fileNameDisplay: document.getElementById('file-name-display'),
    };

    if (dom.analyzeZipBtn) {
        dom.analyzeZipBtn.disabled = true;
    }

    let analysisData = {};

    // 유틸
    function setLoading(button, isLoading) {
        if (!button) return;
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

    function renderAnalysis(data) {
        analysisData = data;
        dom.repoNameDisplay.textContent = analysisData.repo_name || '';

        // 확장자 렌더
        dom.extsContainer.innerHTML = '';
        (analysisData.extensions || []).forEach((ext, i) => {
            dom.extsContainer.appendChild(createExtCheckbox(`ext-${i}`, ext));
        });
        dom.extsSelectAll.checked = true;

        // 트리 렌더
        dom.treeContainer.innerHTML = '';
        if (analysisData.dirs_tree) {
            const rootUl = document.createElement('ul');
            renderInteractiveTree(analysisData.dirs_tree, rootUl);
            dom.treeContainer.appendChild(rootUl);
        }

        dom.analysisResult.style.display = 'flex';
    }

    async function handleExport(type) {
        const selectedExts = Array.from(dom.extsContainer.querySelectorAll('.ext-checkbox:checked')).map(el => el.value);
        const selectedDirs = Array.from(dom.treeContainer.querySelectorAll('input[data-type="directory"]:checked')).map(el => el.value);
        const exportBtn = (type === 'text') ? dom.exportTextBtn : dom.exportFileBtn;
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
                let filename = `${analysisData.repo_name || 'repo'}_export.md`;
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

    // ZIP 파일 선택 및 업로드 분석 폼 제출 (통합)
    if (dom.repoZipInput && dom.fileNameDisplay && dom.analyzeZipBtn && dom.analyzeZipForm) {
        // 파일 선택 인풋 변경 이벤트
        dom.repoZipInput.addEventListener('change', function() {
            const fileInput = this;
            const fileNameDisplay = dom.fileNameDisplay;
            const analyzeBtn = dom.analyzeZipBtn;
            
            if (fileInput.files && fileInput.files.length > 0) {
                const selectedFile = fileInput.files[0];
                
                // 파일명을 표시 인풋에 설정
                fileNameDisplay.value = selectedFile.name;
                
                // ZIP 파일인지 검증
                if (selectedFile.name.toLowerCase().endsWith('.zip')) {
                    // 업로드 후 분석 버튼 활성화
                    analyzeBtn.disabled = false;
                    hideError();
                } else {
                    // ZIP이 아닌 경우 에러 표시 및 버튼 비활성화
                    showError('ZIP 확장자(.zip) 파일만 업로드 가능합니다.');
                    analyzeBtn.disabled = true;
                }
            } else {
                // 파일이 선택되지 않은 경우
                fileNameDisplay.value = '';
                fileNameDisplay.placeholder = 'ZIP 파일을 선택해주세요';
                analyzeBtn.disabled = true;
            }
        });

        // 파일명 표시 인풋 클릭시 파일 선택 다이얼로그 열기
        dom.fileNameDisplay.addEventListener('click', function() {
            dom.repoZipInput.click();
        });
        
        // ZIP 업로드 분석 폼 제출 이벤트
        dom.analyzeZipForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            hideError();
            
            const file = dom.repoZipInput.files[0];
            if (!file) {
                showError('파일을 선택해주세요.');
                return;
            }
            
            setLoading(dom.analyzeZipBtn, true);
            dom.analysisResult.style.display = 'none';
            dom.zipProgress.style.display = 'block';

            try {
                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch(`${API_BASE_URL}/analyze_zip`, {
                    method: 'POST',
                    headers: { 'X-Session-Id': sessionId },
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'ZIP 분석에 실패했습니다.');
                }
                
                const data = await response.json();
                renderAnalysis(data);
                
                // 분석 완료 후 폼 리셋
                dom.fileNameDisplay.value = '';
                dom.fileNameDisplay.placeholder = 'ZIP 파일을 선택해주세요';
                dom.analyzeZipBtn.disabled = true;
                dom.repoZipInput.value = '';
                
            } catch (error) {
                showError(`오류: ${error.message}`);
            } finally {
                dom.zipProgress.style.display = 'none';
                setLoading(dom.analyzeZipBtn, false);
            }
        });
    }
    
    // 기존: Git URL 분석
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
            const data = await response.json();
            renderAnalysis(data);
        } catch (error) {
            showError(`오류: ${error.message}`);
        } finally {
            setLoading(dom.analyzeBtn, false);
        }
    });

    // 트리 → 확장자 sync
    dom.treeContainer.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox') {
            const li = e.target.closest('li');
            const childCheckboxes = li.querySelectorAll('ul input[type="checkbox"]');
            childCheckboxes.forEach(child => { child.checked = e.target.checked; });
            syncExtensionsFromTree();
        }
    });

    // 확장자 → 트리 sync
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

    // 전체 선택
    dom.extsSelectAll.addEventListener('change', () => {
        const isChecked = dom.extsSelectAll.checked;
        dom.extsContainer.querySelectorAll('.ext-checkbox').forEach(cb => { cb.checked = isChecked; });
        dom.treeContainer.querySelectorAll('input[data-type="file"]').forEach(cb => { cb.checked = isChecked; });
        dom.treeContainer.querySelectorAll('input[data-type="directory"]').forEach(cb => { cb.checked = isChecked; });
    });

    // Export 버튼들
    dom.exportTextBtn.addEventListener('click', () => handleExport('text'));
    dom.exportFileBtn.addEventListener('click', () => handleExport('file'));

    // 모달/클립보드
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
