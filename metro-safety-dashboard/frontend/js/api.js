async function fetchAPI(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (options.body && typeof options.body === 'string' && options.body.includes('grant_type')) {
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        localStorage.removeItem('token');
        if (!window.location.pathname.endsWith('/login.html')) {
            window.location.href = '/login.html';
        }
        return null;
    }

    if (!response.ok) {
        throw new Error(await response.text());
    }

    if (options.responseType === 'blob') {
        return response.blob();
    }

    return response.json();
}
