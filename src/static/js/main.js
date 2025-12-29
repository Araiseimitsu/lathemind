/**
 * LatheMind - メインJavaScript
 */

// HTMX設定
document.addEventListener('DOMContentLoaded', function() {
    resetOverlays();

    // HTMXエラーハンドリング
    document.body.addEventListener('htmx:responseError', function(event) {
        console.error('HTMX Error:', event.detail);
        alert('エラーが発生しました: ' + event.detail.xhr.statusText);
        resetOverlays();
    });

    // HTMXリクエスト完了時
    document.body.addEventListener('htmx:afterRequest', function(event) {
        // 成功時の処理
        if (event.detail.successful) {
            console.log('Request successful:', event.detail.pathInfo.requestPath);
        }
        resetOverlays();
    });
});

// ページ再表示(BFCache)や遷移直後にオーバーレイが残るのを防止
window.addEventListener('pageshow', function() {
    resetOverlays();
});

function resetOverlays() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) loadingOverlay.classList.add('hidden');

    const addModal = document.getElementById('add-modal');
    if (addModal) addModal.classList.add('hidden');
}

/**
 * NCプログラムをダウンロード
 */
function downloadNCProgram() {
    const ncCode = document.getElementById('nc-code-content');
    if (!ncCode) {
        alert('ダウンロードするプログラムがありません');
        return;
    }

    const content = ncCode.textContent || ncCode.innerText;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'program.nc';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * クリップボードにコピー
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('コピーしました');
    }, function(err) {
        console.error('コピーエラー:', err);
        alert('コピーに失敗しました');
    });
}

/**
 * トースト通知を表示
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-4 py-2 rounded-lg text-white z-50 fade-in ${
        type === 'success' ? 'bg-green-600' :
        type === 'error' ? 'bg-red-600' : 'bg-blue-600'
    }`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

/**
 * 確認ダイアログ
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * フォームデータをJSONに変換
 */
function formToJson(formId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const json = {};

    formData.forEach((value, key) => {
        if (key !== 'drawing') {
            json[key] = value;
        }
    });

    return json;
}
