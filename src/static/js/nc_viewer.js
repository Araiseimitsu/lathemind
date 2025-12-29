/**
 * LatheMind - NCコードビューア
 */

/**
 * NCコードをハイライト表示
 */
function highlightNCCode(code) {
    if (!code) return '';

    const lines = code.split('\n');
    let html = '';

    lines.forEach((line, index) => {
        const lineNum = index + 1;
        const highlightedLine = highlightLine(line);
        html += `<div class="nc-line"><span class="line-number">${lineNum}</span>${highlightedLine}</div>`;
    });

    return html;
}

/**
 * 1行をハイライト
 */
function highlightLine(line) {
    // コメント
    if (line.trim().startsWith('(') || line.trim().startsWith(';')) {
        return `<span class="comment">${escapeHtml(line)}</span>`;
    }

    // プログラム番号
    if (line.trim().startsWith('O')) {
        return `<span class="program-number">${escapeHtml(line)}</span>`;
    }

    let result = escapeHtml(line);

    // Gコードをハイライト
    result = result.replace(/\b(G\d+\.?\d*)\b/g, '<span class="g-code">$1</span>');

    // Mコードをハイライト
    result = result.replace(/\b(M\d+)\b/g, '<span class="m-code">$1</span>');

    return result;
}

/**
 * HTMLエスケープ
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 結果パネルを更新
 */
function updateResultPanel(response) {
    const panel = document.getElementById('result-panel');
    if (!panel) return;

    if (!response.success) {
        panel.innerHTML = `
            <div class="alert alert-error">
                <strong>エラー:</strong> ${escapeHtml(response.error || '不明なエラー')}
            </div>
        `;
        return;
    }

    // 警告表示
    let warningsHtml = '';
    if (response.warnings && response.warnings.length > 0) {
        const warningItems = response.warnings.map(w => `<li>${escapeHtml(w)}</li>`).join('');
        warningsHtml = `
            <div class="alert alert-warning mb-4">
                <strong>警告:</strong>
                <ul class="list-disc list-inside mt-1">${warningItems}</ul>
            </div>
        `;
    }

    // 解析結果表示
    let analysisHtml = '';
    if (response.analysis) {
        const features = response.analysis.features || [];
        const featuresHtml = features.map(f =>
            `<span class="tag tag-blue">${escapeHtml(f)}</span>`
        ).join('');

        analysisHtml = `
            <div class="mb-4 p-3 bg-gray-50 rounded-lg">
                <h4 class="text-sm font-medium text-gray-700 mb-2">解析結果</h4>
                <div class="text-sm text-gray-600">
                    <p><strong>加工タイプ:</strong> ${escapeHtml(response.analysis.process_type || '不明')}</p>
                    <p class="mt-1"><strong>検出特徴:</strong> ${featuresHtml || 'なし'}</p>
                </div>
            </div>
        `;
    }

    // 参照サンプル表示
    let samplesHtml = '';
    if (response.referenced_samples && response.referenced_samples.length > 0) {
        const sampleItems = response.referenced_samples.map(s =>
            `<span class="tag tag-green">${escapeHtml(s)}</span>`
        ).join('');
        samplesHtml = `
            <div class="mb-4 text-sm">
                <strong class="text-gray-700">参照サンプル:</strong> ${sampleItems}
            </div>
        `;
    }

    // NCコード表示
    const ncCodeHtml = highlightNCCode(response.nc_program);

    panel.innerHTML = `
        ${warningsHtml}
        ${analysisHtml}
        ${samplesHtml}
        <div class="nc-code-viewer" id="nc-code-content">${ncCodeHtml}</div>
        <div class="mt-4 flex justify-end space-x-2">
            <button onclick="copyToClipboard(document.getElementById('nc-code-content').textContent)"
                    class="btn-secondary text-sm">
                コピー
            </button>
            <button onclick="downloadNCProgram()"
                    class="btn-primary text-sm">
                ダウンロード
            </button>
        </div>
    `;

    // ダウンロードボタンを表示
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.classList.remove('hidden');
    }
}

/**
 * HTMXレスポンス処理
 */
document.addEventListener('DOMContentLoaded', function() {
    // /api/generate のレスポンスを処理
    document.body.addEventListener('htmx:afterRequest', function(event) {
        if (event.detail.pathInfo.requestPath === '/api/generate') {
            try {
                const response = JSON.parse(event.detail.xhr.responseText);
                updateResultPanel(response);
            } catch (e) {
                // JSONでない場合はそのまま表示（HTMXがHTMLを処理）
            }
        }
    });
});
