// 公文写作助手 - 前端交互逻辑

// 高亮当前导航
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// 通用AJAX请求封装
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

// 显示提示消息
function showMessage(elementId, message, type = 'info') {
    const el = document.getElementById(elementId);
    if (el) {
        el.className = `result-message ${type}`;
        el.textContent = message;
        el.style.display = 'block';

        if (type !== 'error') {
            setTimeout(() => {
                el.style.display = 'none';
            }, 5000);
        }
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// URL参数解析
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const result = {};
    for (const [key, value] of params) {
        result[key] = value;
    }
    return result;
}
