/**
 * LatheMind - ファイルアップロード処理
 */

let selectedFile = null;

/**
 * ファイル選択時の処理
 */
function handleFileSelect(input) {
    const file = input.files[0];
    if (!file) return;

    // ファイルタイプ検証
    if (!file.type.startsWith('image/')) {
        alert('画像ファイルを選択してください');
        input.value = '';
        return;
    }

    // ファイルサイズ検証 (10MB)
    if (file.size > 10 * 1024 * 1024) {
        alert('ファイルサイズが大きすぎます（最大10MB）');
        input.value = '';
        return;
    }

    selectedFile = file;

    // プレビュー表示
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('drawing-preview');
        const placeholder = document.getElementById('upload-placeholder');
        const previewContainer = document.getElementById('preview-container');
        const fileName = document.getElementById('file-name');

        if (preview) preview.src = e.target.result;
        if (fileName) fileName.textContent = file.name;

        if (placeholder) placeholder.classList.add('hidden');
        if (previewContainer) previewContainer.classList.remove('hidden');
    };
    reader.readAsDataURL(file);

    // ボタンを有効化
    const analyzeBtn = document.getElementById('analyze-btn');
    const generateBtn = document.getElementById('generate-btn');
    if (analyzeBtn) analyzeBtn.disabled = false;
    if (generateBtn) generateBtn.disabled = false;

    console.log('ファイル選択:', file.name, file.size, 'bytes');
}

/**
 * ローディング表示
 */
function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.remove('hidden');
}

/**
 * ローディング非表示
 */
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.classList.add('hidden');
}

/**
 * 図面解析を実行
 */
async function analyzeDrawing() {
    if (!selectedFile) {
        alert('図面ファイルを選択してください');
        return;
    }

    showLoading();

    try {
        const formData = new FormData();
        formData.append('drawing', selectedFile);

        const response = await fetch('/api/analyze-drawing', {
            method: 'POST',
            body: formData
        });

        const html = await response.text();
        const resultDiv = document.getElementById('analysis-result');
        if (resultDiv) {
            resultDiv.innerHTML = html;
        }
    } catch (error) {
        console.error('図面解析エラー:', error);
        const resultDiv = document.getElementById('analysis-result');
        if (resultDiv) {
            resultDiv.innerHTML = `<div class="text-red-500 p-4">エラー: ${error.message}</div>`;
        }
    } finally {
        hideLoading();
    }
}

/**
 * NCプログラム生成を実行
 */
async function generateNCProgram() {
    if (!selectedFile) {
        alert('図面ファイルを選択してください');
        return;
    }

    showLoading();

    try {
        const formData = new FormData();
        formData.append('drawing', selectedFile);

        // 行程情報をJSON化
        const processInfo = {
            process_name: document.getElementById('process_name').value,
            process_type: document.getElementById('process_type').value,
            sequence: 1,
            notes: ''
        };
        formData.append('process_info', JSON.stringify(processInfo));

        // 加工条件をJSON化
        const machiningConditions = {
            material: document.getElementById('material').value,
            spindle_speed: parseInt(document.getElementById('spindle_speed').value),
            feed_rate: parseFloat(document.getElementById('feed_rate').value),
            depth_of_cut: parseFloat(document.getElementById('depth_of_cut').value),
            coolant: document.getElementById('coolant').checked,
            tool_number: document.getElementById('tool_number').value,
            coordinate_system: document.getElementById('coordinate_system').value
        };
        formData.append('machining_conditions', JSON.stringify(machiningConditions));

        console.log('生成リクエスト:', processInfo, machiningConditions);

        const response = await fetch('/api/generate', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        console.log('生成結果:', data);

        updateResultPanel(data);

    } catch (error) {
        console.error('NCプログラム生成エラー:', error);
        const resultPanel = document.getElementById('result-panel');
        if (resultPanel) {
            resultPanel.innerHTML = `
                <div class="alert alert-error">
                    <strong>エラー:</strong> ${error.message}
                </div>
            `;
        }
    } finally {
        hideLoading();
    }
}

/**
 * ドラッグ&ドロップ対応
 */
document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('upload-area');
    const input = document.getElementById('drawing-input');
    const analyzeBtn = document.getElementById('analyze-btn');
    const generateBtn = document.getElementById('generate-btn');

    if (uploadArea && input) {
        uploadArea.addEventListener('click', function() {
            input.click();
        });

        input.addEventListener('change', function() {
            handleFileSelect(input);
        });

        // ドラッグオーバー
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('upload-area-active');
        });

        // ドラッグリーブ
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('upload-area-active');
        });

        // ドロップ
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('upload-area-active');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                // DataTransferからFileListを設定
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(files[0]);
                input.files = dataTransfer.files;
                handleFileSelect(input);
            }
        });
    }

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            analyzeDrawing();
        });
    }

    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            generateNCProgram();
        });
    }
});

/**
 * ファイル選択をリセット
 */
function resetFileSelection() {
    selectedFile = null;
    const input = document.getElementById('drawing-input');
    if (input) input.value = '';

    const placeholder = document.getElementById('upload-placeholder');
    const previewContainer = document.getElementById('preview-container');

    if (placeholder) placeholder.classList.remove('hidden');
    if (previewContainer) previewContainer.classList.add('hidden');

    const analyzeBtn = document.getElementById('analyze-btn');
    const generateBtn = document.getElementById('generate-btn');
    if (analyzeBtn) analyzeBtn.disabled = true;
    if (generateBtn) generateBtn.disabled = true;
}
