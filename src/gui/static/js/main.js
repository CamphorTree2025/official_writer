// 公文写作助手 - 前端交互逻辑

// 高亮当前导航
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            link.classList.add('active');
        }
    });

    // 初始化 Toast 容器
    if (!document.querySelector('.toast-container')) {
        const tc = document.createElement('div');
        tc.className = 'toast-container';
        document.body.appendChild(tc);
    }
});

// ===== Toast 提示 =====
function showToast(message, type = 'info', duration = 3000) {
    const container = document.querySelector('.toast-container');
    if (!container) return;
    
    const icons = { success: '✓', error: '✗', info: 'ℹ', warning: '⚠' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type] || ''}</span><span>${message}</span>`;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ===== 通用 API 请求 =====
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || '请求失败');
        }
        return data;
    } catch (error) {
        throw error;
    }
}

// ===== 显示提示消息 =====
function showMessage(elementId, message, type = 'info') {
    const el = document.getElementById(elementId);
    if (el) {
        el.className = `result-message ${type}`;
        el.innerHTML = message;
        el.style.display = 'block';
        if (type !== 'error') {
            setTimeout(() => { el.style.display = 'none'; }, 5000);
        }
    }
}

// ===== 格式化文件大小 =====
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ===== URL 参数解析 =====
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const result = {};
    for (const [key, value] of params) {
        result[key] = value;
    }
    return result;
}

// ===== 确认对话框 =====
function confirmAction(message) {
    return new Promise(resolve => {
        resolve(confirm(message));
    });
}

// ===== 日期格式化 =====
function formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleString('zh-CN', {
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit'
    });
}
