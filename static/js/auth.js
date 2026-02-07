/**
 * 認證相關 JavaScript 函數
 */

/**
 * 儲存 token 到 localStorage 和 Cookie
 */
function saveToken(token) {
    localStorage.setItem('access_token', token);
    // Cookie 由後端設置
}

/**
 * 獲取 token
 */
function getToken() {
    return localStorage.getItem('access_token') || getCookie('access_token');
}

/**
 * 清除 token
 */
function clearToken() {
    localStorage.removeItem('access_token');
    // 清除 Cookie
    document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}

/**
 * 獲取 Cookie
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

/**
 * 檢查是否已登入
 */
async function checkAuth() {
    const token = getToken();
    if (!token) {
        return false;
    }
    
    try {
        const response = await fetch('/api/auth/verify', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            credentials: 'include'
        });
        
        const data = await response.json();
        return data.valid === true;
    } catch (error) {
        console.error('驗證 token 失敗:', error);
        return false;
    }
}

/**
 * 用戶登入
 */
async function login(email, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 儲存 token
            saveToken(data.token);
            return {
                success: true,
                user: data.user
            };
        } else {
            return {
                success: false,
                message: data.message || '登入失敗'
            };
        }
    } catch (error) {
        console.error('登入錯誤:', error);
        return {
            success: false,
            message: '登入時發生錯誤'
        };
    }
}

/**
 * 管理員登入
 */
async function adminLogin(email, password) {
    try {
        const response = await fetch('/api/auth/admin/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 儲存 token
            saveToken(data.token);
            return {
                success: true,
                user: data.user
            };
        } else {
            return {
                success: false,
                message: data.message || '登入失敗'
            };
        }
    } catch (error) {
        console.error('登入錯誤:', error);
        return {
            success: false,
            message: '登入時發生錯誤'
        };
    }
}

/**
 * 用戶註冊
 */
async function register(name, email, password) {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            return {
                success: true,
                message: data.message
            };
        } else {
            return {
                success: false,
                message: data.message || '註冊失敗'
            };
        }
    } catch (error) {
        console.error('註冊錯誤:', error);
        return {
            success: false,
            message: '註冊時發生錯誤'
        };
    }
}

/**
 * 檢查 email 是否已存在
 */
async function checkEmail(email) {
    try {
        const response = await fetch('/api/auth/check-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email
            }),
            credentials: 'include'
        });
        
        const data = await response.json();
        return data.exists;
    } catch (error) {
        console.error('檢查 email 錯誤:', error);
        return false;
    }
}

/**
 * 登出
 */
async function logout() {
    try {
        await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.error('登出錯誤:', error);
    } finally {
        clearToken();
        window.location.href = '/';
    }
}

/**
 * 發送帶有認證的請求
 */
async function authenticatedFetch(url, options = {}) {
    const token = getToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return fetch(url, {
        ...options,
        headers: headers,
        credentials: 'include'
    });
}
