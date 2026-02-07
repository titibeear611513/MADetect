/**
 * 模態框處理函數
 */

/**
 * 初始化密碼顯示/隱藏功能
 */
function initPasswordToggle() {
    for (let i = 1; i <= 3; i++) {
        const checkEye = document.getElementById(`checkEye${i}`);
        const floatingPassword = document.getElementById(`floatingPassword${i}`);
        
        if (checkEye && floatingPassword) {
            checkEye.addEventListener("click", function(e) {
                if (e.target.classList.contains('fa-eye')) {
                    e.target.classList.remove('fa-eye');
                    e.target.classList.add('fa-eye-slash');
                    floatingPassword.setAttribute('type', 'text');
                } else {
                    floatingPassword.setAttribute('type', 'password');
                    e.target.classList.remove('fa-eye-slash');
                    e.target.classList.add('fa-eye');
                }
            });
        }
    }
}

/**
 * 初始化問題回報表單
 */
function initReportForm() {
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            const reportText = document.getElementById('report-message-text').value;
            
            if (!reportText.trim()) {
                alert('請輸入回報內容');
                return;
            }

            // 使用 authenticatedFetch 發送請求
            const token = typeof getToken !== 'undefined' ? getToken() : 
                         localStorage.getItem('access_token');
            
            try {
                const response = await fetch('/report', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': token ? `Bearer ${token}` : ''
                    },
                    body: JSON.stringify({ report: reportText }),
                    credentials: 'include'
                });

                const data = await response.json();
                
                if (response.ok && data.success) {
                    alert('問題回報成功');
                    document.getElementById('report-message-text').value = '';
                    // 關閉模態框
                    const modal = bootstrap.Modal.getInstance(document.getElementById('report'));
                    if (modal) {
                        modal.hide();
                    }
                } else {
                    alert(data.message || '問題回報失敗，請稍後再試！');
                }
            } catch (error) {
                console.error('錯誤:', error);
                alert('問題回報失敗，請稍後再試！');
            }
        });
    }
}

/**
 * 顯示使用者 email
 * 注意：此函數需要在模板中通過 Flask 傳遞 user_email 變數
 */
function displayUserEmail() {
    // 從 data 屬性獲取 email（需要在模板中設置）
    const emailInput = document.querySelector('.account');
    if (emailInput) {
        const userEmail = emailInput.getAttribute('data-email') || '';
        if (userEmail) {
            emailInput.value = userEmail;
        }
    }
}

// addProject 函數已移至 project.js

// 頁面載入時初始化
document.addEventListener("DOMContentLoaded", function() {
    initPasswordToggle();
    initReportForm();
    displayUserEmail();
});
