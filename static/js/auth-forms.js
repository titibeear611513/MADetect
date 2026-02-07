/**
 * 認證表單處理 JavaScript
 */

/**
 * 初始化認證表單
 */
function initAuthForm(formType, isAdmin = false) {
    // 防止重複初始化
    if (window.authFormInitialized) {
        return;
    }
    window.authFormInitialized = true;
    
    // 移除自動檢查認證和重定向的邏輯
    // 因為後端路由已經處理了重定向邏輯
    // 前端不需要再次檢查，避免造成循環重定向
    
    const form = document.getElementById('auth-form');
    if (!form) return;
    
    // 根據表單類型設定處理函數
    switch(formType) {
        case 'login':
            initLoginForm(form, false);
            break;
        case 'signup':
            initSignupForm(form);
            break;
        case 'forget':
            initForgetForm(form);
            break;
        case 'reset':
            initResetForm(form);
            break;
    }
}

/**
 * 初始化登入表單
 */
function initLoginForm(form, isAdmin) {
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorElement = document.getElementById('login-error');
        
        if (errorElement) errorElement.textContent = '';
        
        const result = await login(email, password);
        
        if (result.success) {
            window.location.href = "/home";
        } else {
            if (errorElement) {
                errorElement.textContent = result.message || 'Invalid email or password';
            }
        }
    });
}

/**
 * 初始化註冊表單
 */
function initSignupForm(form) {
    // Email 檢查
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', async function() {
            const email = this.value;
            if (!email) return;
            
            const exists = await checkEmail(email);
            const errorElement = document.getElementById('email-error');
            const submitButton = form.querySelector('button[type="submit"]');
            
            if (exists) {
                if (errorElement) errorElement.textContent = 'Email already exists';
                if (submitButton) submitButton.disabled = true;
            } else {
                if (errorElement) errorElement.textContent = '';
                if (submitButton) submitButton.disabled = false;
            }
        });
    }
    
    // 表單提交
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('password-confirm').value;
        
        // 清除錯誤訊息
        const emailError = document.getElementById('email-error');
        const confirmError = document.getElementById('confirm_password-error');
        if (emailError) emailError.textContent = '';
        if (confirmError) confirmError.textContent = '';
        
        // 驗證密碼
        if (password !== confirmPassword) {
            if (confirmError) confirmError.textContent = 'Passwords do not match';
            return;
        }
        
        // 註冊
        const result = await register(name, email, password);
        
        if (result.success) {
            alert('註冊成功！請登入');
            window.location.href = "/login";
        } else {
            if (emailError) emailError.textContent = result.message || '註冊失敗';
        }
    });
}

/**
 * 初始化忘記密碼表單
 */
function initForgetForm(form) {
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const errorElement = document.getElementById('forget-error-message');
        
        // 使用舊的 API（向後兼容）
        try {
            const response = await fetch('/forgetpsw_function', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    user_name: name,
                    user_email: email
                })
            });
            
            const data = await response.json();
            
            if (data.exists) {
                if (errorElement) errorElement.textContent = '';
                window.location.href = "/reset";
            } else {
                if (errorElement) errorElement.textContent = 'Invalid name or email';
            }
        } catch (error) {
            console.error('錯誤:', error);
            if (errorElement) errorElement.textContent = '發生錯誤，請稍後再試';
        }
    });
}

/**
 * 初始化重設密碼表單
 */
function initResetForm(form) {
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('password-confirm').value;
        const errorElement = document.getElementById('reset_password-error');
        
        if (errorElement) errorElement.textContent = '';
        
        // 驗證密碼
        if (password !== confirmPassword) {
            if (errorElement) errorElement.textContent = 'Passwords do not match';
            return;
        }
        
        // 使用舊的 API（向後兼容）
        try {
            const response = await fetch('/reset_function', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    user_password: password
                })
            });
            
            if (response.ok) {
                window.location.href = "/login";
            } else {
                if (errorElement) errorElement.textContent = '重設密碼失敗';
            }
        } catch (error) {
            console.error('錯誤:', error);
            if (errorElement) errorElement.textContent = '發生錯誤，請稍後再試';
        }
    });
}
