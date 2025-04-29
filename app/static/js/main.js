// 通用函数：显示提示消息
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
    
    // 5秒后自动关闭
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// 通用函数：确认对话框
function confirmAction(message) {
    return confirm(message);
}

// 通用函数：刷新页面
function refreshPage() {
    window.location.reload();
}

// 通用函数：处理API错误
function handleApiError(error) {
    console.error('API Error:', error);
    showAlert('操作失败，请稍后重试', 'danger');
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}); 