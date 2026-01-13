/**
 * 工程管理ページスクリプト
 */

// 状態管理
const state = {
    frontOperations: [],
    backOperations: [],
    fileName: null
};

// DOM要素
const elements = {
    dropZone: null,
    fileInput: null,
    fileName: null,
    messageArea: null,
    messageContent: null,
    operationsContainer: null,
    emptyState: null,
    frontBody: null,
    backBody: null,
    btnSave: null,
    btnReload: null,
    loadingOverlay: null
};

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    // DOM要素の取得
    elements.dropZone = document.getElementById('drop-zone');
    elements.fileInput = document.getElementById('file-input');
    elements.fileName = document.getElementById('file-name');
    elements.messageArea = document.getElementById('message-area');
    elements.messageContent = document.getElementById('message-content');
    elements.operationsContainer = document.getElementById('operations-container');
    elements.emptyState = document.getElementById('empty-state');
    elements.frontBody = document.getElementById('front-operations-body');
    elements.backBody = document.getElementById('back-operations-body');
    elements.btnSave = document.getElementById('btn-save');
    elements.btnReload = document.getElementById('btn-reload');
    elements.loadingOverlay = document.getElementById('loading-overlay');

    // イベントリスナー設定
    setupDropZone();
    setupButtons();

    // 初期データ読み込み
    loadProcessData();
});

/**
 * ドロップゾーンの設定
 */
function setupDropZone() {
    const dz = elements.dropZone;

    dz.addEventListener('click', () => {
        elements.fileInput.click();
    });

    dz.addEventListener('dragover', (e) => {
        e.preventDefault();
        dz.classList.add('dragover');
    });

    dz.addEventListener('dragleave', () => {
        dz.classList.remove('dragover');
    });

    dz.addEventListener('drop', (e) => {
        e.preventDefault();
        dz.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    elements.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

/**
 * ボタンの設定
 */
function setupButtons() {
    elements.btnSave.addEventListener('click', () => {
        saveProcessData();
    });

    elements.btnReload.addEventListener('click', () => {
        loadProcessData();
    });
}

/**
 * ファイルアップロード処理
 */
async function handleFileUpload(file) {
    // ファイル形式チェック
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        showMessage('XLSXファイルのみアップロード可能です', 'error');
        return;
    }

    // ファイル名表示
    state.fileName = file.name;
    elements.fileName.textContent = file.name;
    elements.fileName.classList.remove('hidden');
    elements.dropZone.classList.add('has-file');

    // ローディング表示
    showLoading(true);

    // ファイルアップロード
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/process/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            state.frontOperations = result.data.front_operations;
            state.backOperations = result.data.back_operations;
            renderOperations();
            showMessage(result.message, 'success');
        } else {
            showMessage(result.message, 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showMessage('アップロードに失敗しました', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * 工程データの読み込み
 */
async function loadProcessData() {
    showLoading(true);

    try {
        const response = await fetch('/api/process');
        const data = await response.json();

        state.frontOperations = data.front_operations;
        state.backOperations = data.back_operations;

        renderOperations();
    } catch (error) {
        console.error('Load error:', error);
        showMessage('データの読み込みに失敗しました', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * 工程データの保存
 */
async function saveProcessData() {
    // 入力値を収集
    collectInputValues();

    showLoading(true);

    try {
        const response = await fetch('/api/process', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                front_operations: state.frontOperations,
                back_operations: state.backOperations
            })
        });

        const data = await response.json();
        showMessage('保存しました', 'success');
    } catch (error) {
        console.error('Save error:', error);
        showMessage('保存に失敗しました', 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * 入力値を収集してstateに反映
 */
function collectInputValues() {
    // 正面側
    state.frontOperations = [];
    const frontRows = elements.frontBody.querySelectorAll('tr');
    frontRows.forEach((row, index) => {
        const correction = row.querySelector('.input-correction').value.trim();
        const tool = row.querySelector('.input-tool').value.trim();
        const name = row.querySelector('.input-name').value.trim();
        state.frontOperations.push({ correction, tool, name });
    });

    // 背面側
    state.backOperations = [];
    const backRows = elements.backBody.querySelectorAll('tr');
    backRows.forEach((row, index) => {
        const correction = row.querySelector('.input-correction').value.trim();
        const tool = row.querySelector('.input-tool').value.trim();
        const name = row.querySelector('.input-name').value.trim();
        state.backOperations.push({ correction, tool, name });
    });
}

/**
 * 工程データの描画
 */
function renderOperations() {
    const hasData = state.frontOperations.length > 0 || state.backOperations.length > 0;

    if (hasData) {
        elements.operationsContainer.classList.remove('hidden');
        elements.emptyState.classList.add('hidden');
        renderOperationTable(elements.frontBody, state.frontOperations);
        renderOperationTable(elements.backBody, state.backOperations);
    } else {
        elements.operationsContainer.classList.add('hidden');
        elements.emptyState.classList.remove('hidden');
    }
}

/**
 * 工程テーブルの描画
 */
function renderOperationTable(tbody, operations) {
    tbody.innerHTML = '';

    operations.forEach((op, index) => {
        const row = document.createElement('tr');
        row.className = 'operation-row border-b border-white/10';
        row.innerHTML = `
            <td class="py-2 px-3 text-gray-500">${index + 1}</td>
            <td class="py-2 px-3">
                <input type="text" class="operation-input input-correction" value="${escapeHtml(op.correction)}" placeholder="A12">
            </td>
            <td class="py-2 px-3">
                <input type="text" class="operation-input input-tool" value="${escapeHtml(op.tool)}" placeholder="T1">
            </td>
            <td class="py-2 px-3">
                <input type="text" class="operation-input input-name" value="${escapeHtml(op.name)}" placeholder="工程名">
            </td>
            <td class="py-2 px-3">
                <button class="text-red-400 hover:text-red-300 delete-btn" data-index="${index}">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                </button>
            </td>
        `;

        // 削除ボタンイベント
        const deleteBtn = row.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', () => {
            deleteOperation(tbody, index);
        });

        tbody.appendChild(row);
    });

    // 追加ボタン行
    const addRow = document.createElement('tr');
    addRow.innerHTML = `
        <td class="py-2 px-3" colspan="5">
            <button class="text-blue-400 hover:text-blue-300 text-sm add-btn">
                + 工程を追加
            </button>
        </td>
    `;
    addRow.querySelector('.add-btn').addEventListener('click', () => {
        addOperation(tbody);
    });
    tbody.appendChild(addRow);
}

/**
 * 工程の削除
 */
function deleteOperation(tbody, index) {
    const isFront = tbody === elements.frontBody;
    const operations = isFront ? state.frontOperations : state.backOperations;

    operations.splice(index, 1);
    renderOperations();
}

/**
 * 工程の追加
 */
function addOperation(tbody) {
    const isFront = tbody === elements.frontBody;
    const operations = isFront ? state.frontOperations : state.backOperations;

    operations.push({ correction: '', tool: '', name: '' });
    renderOperations();
}

/**
 * メッセージ表示
 */
function showMessage(message, type = 'info') {
    elements.messageArea.classList.remove('hidden');
    elements.messageContent.textContent = message;

    // スタイル設定
    elements.messageContent.className = 'p-4 rounded-lg';
    if (type === 'success') {
        elements.messageContent.classList.add('bg-green-500/20', 'text-green-400', 'border', 'border-green-500/30');
    } else if (type === 'error') {
        elements.messageContent.classList.add('bg-red-500/20', 'text-red-400', 'border', 'border-red-500/30');
    } else {
        elements.messageContent.classList.add('bg-blue-500/20', 'text-blue-400', 'border', 'border-blue-500/30');
    }

    // 3秒後に非表示
    setTimeout(() => {
        elements.messageArea.classList.add('hidden');
    }, 3000);
}

/**
 * ローディング表示
 */
function showLoading(show) {
    if (show) {
        elements.loadingOverlay.classList.remove('hidden');
    } else {
        elements.loadingOverlay.classList.add('hidden');
    }
}

/**
 * HTMLエスケープ
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
