function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token && !window.location.pathname.endsWith('/login.html')) {
        window.location.href = '/login.html';
    } else if (token && (window.location.pathname.endsWith('/login.html') || window.location.pathname.endsWith('index.html') || window.location.pathname === '/')) {
        window.location.href = 'dashboard.html';
    }
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login.html';
}

document.addEventListener('DOMContentLoaded', checkAuth);
