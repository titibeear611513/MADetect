/**
 * 專案管理 JavaScript 模組
 */

// 全域變數：當前專案 ID
let currentProjectId = null;

/**
 * 獲取 JWT Token
 */
function getToken() {
    return localStorage.getItem('jwt_token') || 
           document.cookie.split('; ').find(row => row.startsWith('access_token='))?.split('=')[1] || '';
}

/**
 * 顯示預設頁面
 */
function showDefaultPage() {
    const rSide = document.getElementById('r_side');
    if (!rSide) return;
    
    // 清除當前專案 ID
    currentProjectId = null;
    
    // 更新 URL
    window.history.pushState({}, '', '/home');
    
    // 清除側邊欄的 active 狀態
    document.querySelectorAll('.l_middle .title.active').forEach(el => {
        el.classList.remove('active');
    });
    
    // 顯示預設頁面
    rSide.innerHTML = `
        <div class="r_container default-page">
            <div class="title">歡迎使用 MADetect</div>
            <div class="input-block">
                <div class="default-content">
                    <h2>開始使用</h2>
                    <p>MADetect 是一個醫療廣告法規檢測工具，幫助您確保醫療廣告符合台灣醫療法規。</p>
                    
                    <h3>操作建議：</h3>
                    <ul>
                        <li>點擊左側「新增專案」按鈕創建新專案</li>
                        <li>選擇或創建專案後，即可開始檢測醫療廣告</li>
                        <li>輸入您的醫療廣告詞，系統會自動分析是否符合法規</li>
                        <li>系統會提供專業醫療建議和修改建議</li>
                    </ul>
                    
                    <h3>功能說明：</h3>
                    <ul>
                        <li><strong>專業醫療建議：</strong>分析廣告是否違法，並提供相關法條說明</li>
                        <li><strong>修改建議：</strong>提供符合法規的廣告詞修改方案</li>
                        <li><strong>專案管理：</strong>可以創建多個專案，分別管理不同的廣告檢測記錄</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
    
    // 清除專案內容
    clearProjectContent();
}

/**
 * 載入專案列表
 */
async function loadProjects() {
    try {
        const token = getToken();
        const response = await fetch('/api/project/list', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        if (!response.ok) {
            console.error('載入專案列表失敗:', response.status);
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            renderProjects(data.projects);
            
            // 如果有專案且沒有當前專案，選擇第一個（最近更新的）
            if (data.projects.length > 0 && !currentProjectId) {
                const firstProjectId = data.projects[0]._id;
                currentProjectId = firstProjectId;
                // 更新 URL
                window.history.pushState({}, '', `/home?project_id=${firstProjectId}`);
                // 載入專案資料
                await loadProjectData(firstProjectId);
            } else if (data.projects.length === 0 && !currentProjectId) {
                // 如果沒有專案，顯示預設頁面
                showDefaultPage();
            }
        } else {
            console.error('載入專案失敗:', data.message);
        }
    } catch (error) {
        console.error('載入專案錯誤:', error);
    }
}

/**
 * 渲染專案列表
 */
function renderProjects(projects) {
    const projectList = document.querySelector('.l_middle');
    if (!projectList) return;
    
    projectList.innerHTML = '';
    
    if (projects.length === 0) {
        projectList.innerHTML = '<div class="title"><div class="text">尚無專案</div></div>';
        return;
    }
    
    projects.forEach(project => {
        const projectDiv = document.createElement('div');
        projectDiv.className = 'title';
        projectDiv.dataset.projectId = project._id;
        
        if (currentProjectId === project._id) {
            projectDiv.classList.add('active');
        }
        
        projectDiv.innerHTML = `
            <div class="text" onclick="switchProject('${project._id}')">${escapeHtml(project.project_name)}</div>
            <div class="icon">
                <a href="#" type="button" data-bs-toggle="modal" data-bs-target="#edit" onclick="setEditProject('${project._id}', '${escapeHtml(project.project_name)}')">
                    <i class="fa-solid fa-pen-to-square"></i>
                </a>
            </div>
            <div class="icon">
                <a href="#" type="button" data-bs-toggle="modal" data-bs-target="#delete" onclick="setDeleteProject('${project._id}', '${escapeHtml(project.project_name)}')">
                    <i class="fa-solid fa-trash-can"></i>
                </a>
            </div>
        `;
        
        projectDiv.addEventListener('click', function(e) {
            if (e.target.closest('.icon')) {
                e.stopPropagation();
            } else if (e.target.closest('.text')) {
                switchProject(project._id);
            }
        });
        
        projectList.appendChild(projectDiv);
    });
}

/**
 * 切換專案
 */
async function switchProject(projectId) {
    currentProjectId = projectId;
    
    // 更新 URL
    window.history.pushState({}, '', `/home?project_id=${projectId}`);
    
    // 更新側邊欄高亮
    document.querySelectorAll('.l_middle .title').forEach(el => {
        el.classList.remove('active');
        if (el.dataset.projectId === projectId) {
            el.classList.add('active');
        }
    });
    
    // 載入專案資料
    await loadProjectData(projectId);
}

/**
 * 載入專案資料和記錄
 */
async function loadProjectData(projectId) {
    if (!projectId) {
        console.error('專案 ID 不能為空');
        showInitialInput();
        return;
    }
    
    try {
        const token = getToken();
        const response = await fetch(`/api/project/${projectId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        // 檢查 HTTP 狀態碼
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.message || `HTTP ${response.status}: ${response.statusText}`;
            console.error('載入專案資料失敗:', errorMessage);
            
            // 如果是 404 或 403，顯示錯誤並返回
            if (response.status === 404 || response.status === 403) {
                alert(errorMessage);
                showInitialInput();
                return;
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // 清空現有內容
            clearProjectContent();
            
            // 載入記錄
            if (data.records && data.records.length > 0) {
                renderProjectRecords(data.records);
            } else {
                // 顯示初始輸入框
                showInitialInput();
            }
        } else {
            console.error('載入專案資料失敗:', data.message);
            alert(data.message || '載入專案資料失敗');
            showInitialInput();
        }
    } catch (error) {
        console.error('載入專案資料錯誤:', error);
        alert('載入專案資料時發生錯誤: ' + error.message);
        showInitialInput();
    }
}

/**
 * 清空專案內容
 */
function clearProjectContent() {
    const rSide = document.querySelector('.r_side');
    if (!rSide) return;
    
    // 保留第一個容器（初始輸入框）
    const firstContainer = rSide.querySelector('.r_container:first-of-type');
    if (firstContainer) {
        rSide.innerHTML = '';
        rSide.appendChild(firstContainer);
        // 清空輸入框內容
        const inputAD = firstContainer.querySelector('#inputAD');
        if (inputAD) {
            inputAD.textContent = '';
            inputAD.setAttribute('contenteditable', 'true');
        }
    } else {
        // 如果沒有初始容器，創建一個
        showInitialInput();
    }
}

/**
 * 顯示初始輸入框
 */
function showInitialInput() {
    const rSide = document.querySelector('.r_side');
    if (!rSide) return;
    
    rSide.innerHTML = `
        <div class="r_container">
            <div class="title">請輸入廣告詞</div>
            <div class="input-block">
                <div id="inputAD" class="editable-content" contenteditable="true" name="input_ad"></div>
            </div>
            <div class="button-container">
                <button title='送出' id="inputADbutton" class="custom-button" onclick="madetect()">
                    <img src="/static/pic/send4.png" width="24px" height="24px" alt="送出">
                </button>
            </div>
        </div>
    `;
}

/**
 * 創建新 div 元素（用於專案記錄渲染）
 */
function createProjectDiv(titleText, bgColorClass, editable, content) {
    const newDiv = document.createElement('div');
    newDiv.classList.add('r_container', 'new-container', bgColorClass);

    const newTitle = document.createElement('div');
    newTitle.classList.add('title');
    newTitle.innerText = titleText;

    const newInputBlock = document.createElement('div');
    newInputBlock.classList.add('input-block');

    const newEditableContent = document.createElement('div');
    newEditableContent.classList.add('editable-content');
    newEditableContent.setAttribute('contenteditable', editable ? 'true' : 'false');

    if (bgColorClass == 'pink-bg') {
        newEditableContent.innerHTML = content || '';
    } else if (bgColorClass == 'Lgreen-bg') {
        newEditableContent.innerHTML = content || '';
    } else {
        newEditableContent.setAttribute('id', 'inputAD');
        newEditableContent.setAttribute('name', 'input_ad');
        newEditableContent.innerHTML = '';
    }

    newInputBlock.appendChild(newEditableContent);
    newDiv.appendChild(newTitle);
    newDiv.appendChild(newInputBlock);

    return newDiv;
}

/**
 * 創建黑色分隔線
 */
function createProjectBlackLine() {
    const newDivBlackLine = document.createElement('div');
    newDivBlackLine.classList.add('black-line');
    return newDivBlackLine;
}

/**
 * 渲染專案記錄
 */
function renderProjectRecords(records) {
    const rSide = document.querySelector('.r_side');
    if (!rSide) return;
    
    // 清空現有內容
    rSide.innerHTML = '';
    
    records.forEach((record, index) => {
        // 輸入框
        const inputDiv = createProjectDiv('請輸入廣告詞', 'Dgreen-bg', true, '');
        inputDiv.querySelector('.editable-content').textContent = record.input_ad;
        inputDiv.querySelector('.editable-content').setAttribute('contenteditable', 'false');
        
        // 專業醫療建議
        const lawDiv = createProjectDiv('專業醫療建議：', 'pink-bg', false, record.result_law);
        
        // 修改建議
        const adviceDiv = createProjectDiv('以下是修改後的廣告詞：', 'Lgreen-bg', false, record.result_advice);
        
        // 分隔線
        const blackLine = createProjectBlackLine();
        
        // 新的輸入框（最後一個記錄後）
        let newInputDiv = null;
        if (index === records.length - 1) {
            newInputDiv = createProjectDiv('請輸入廣告詞', 'Dgreen-bg', true, '');
            const buttonContainer = document.createElement('div');
            buttonContainer.classList.add('button-container');
            newInputDiv.appendChild(buttonContainer);
            
            const newButton = document.createElement('button');
            newButton.classList.add('custom-button');
            newButton.innerHTML = '<img src="/static/pic/send4.png" width="24px" height="24px" alt="送出">';
            newButton.onclick = function() {
                if (typeof madetects !== 'undefined') {
                    madetects(newInputDiv);
                } else {
                    alert('請先載入 home.js');
                }
            };
            buttonContainer.appendChild(newButton);
        }
        
        // 添加到頁面
        rSide.appendChild(inputDiv);
        rSide.appendChild(lawDiv);
        rSide.appendChild(adviceDiv);
        if (index < records.length - 1) {
            rSide.appendChild(blackLine);
        }
        if (newInputDiv) {
            rSide.appendChild(blackLine);
            rSide.appendChild(newInputDiv);
        }
    });
    
    // 設置邊框顏色
    document.querySelectorAll('.pink-bg, .Lgreen-bg, .Dgreen-bg').forEach(div => {
        const title = div.querySelector('.title');
        if (title) {
            div.style.borderColor = window.getComputedStyle(title).backgroundColor;
        }
    });
}

/**
 * 新增專案
 */
async function addProject() {
    const projectName = document.getElementById('create-project-name').value.trim();
    
    if (!projectName) {
        alert('請輸入專案名稱');
        return;
    }
    
    try {
        const token = getToken();
        const response = await fetch('/api/project/create', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ project_name: projectName }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 關閉模態框
            const modal = bootstrap.Modal.getInstance(document.getElementById('create'));
            if (modal) {
                modal.hide();
            }
            
            // 清空輸入框
            document.getElementById('create-project-name').value = '';
            
            // 重新載入專案列表
            await loadProjects();
            
            // 切換到新專案
            if (data.project) {
                await switchProject(data.project._id);
            }
        } else {
            alert(data.message || '新增專案失敗');
        }
    } catch (error) {
        console.error('新增專案錯誤:', error);
        alert('新增專案時發生錯誤');
    }
}

/**
 * 設置要編輯的專案
 */
let editProjectId = null;
function setEditProject(projectId, projectName) {
    editProjectId = projectId;
    document.getElementById('edit-project-name').value = projectName;
}

/**
 * 更新專案名稱
 */
async function updateProject() {
    const newName = document.getElementById('edit-project-name').value.trim();
    
    if (!newName) {
        alert('請輸入專案名稱');
        return;
    }
    
    if (!editProjectId) {
        alert('請選擇要編輯的專案');
        return;
    }
    
    try {
        const token = getToken();
        const response = await fetch(`/api/project/${editProjectId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ project_name: newName }),
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 關閉模態框
            const modal = bootstrap.Modal.getInstance(document.getElementById('edit'));
            if (modal) {
                modal.hide();
            }
            
            // 重新載入專案列表
            await loadProjects();
        } else {
            alert(data.message || '更新專案名稱失敗');
        }
    } catch (error) {
        console.error('更新專案錯誤:', error);
        alert('更新專案時發生錯誤');
    }
}

/**
 * 設置要刪除的專案
 */
let deleteProjectId = null;
function setDeleteProject(projectId, projectName) {
    deleteProjectId = projectId;
    // 可以在模態框中顯示專案名稱
    const deleteModal = document.getElementById('delete');
    if (deleteModal) {
        const modalBody = deleteModal.querySelector('.modal-body');
        if (modalBody) {
            modalBody.innerHTML = `
                <p>確定要刪除專案「${escapeHtml(projectName)}」嗎？</p>
                <p class="text-danger">此操作無法復原，將刪除專案內所有記錄。</p>
            `;
        }
    }
}

/**
 * 刪除專案
 */
async function deleteProject() {
    if (!deleteProjectId) {
        alert('請選擇要刪除的專案');
        return;
    }
    
    try {
        const token = getToken();
        const response = await fetch(`/api/project/${deleteProjectId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 關閉模態框
            const modal = bootstrap.Modal.getInstance(document.getElementById('delete'));
            if (modal) {
                modal.hide();
            }
            
            // 如果刪除的是當前專案，清空內容
            if (deleteProjectId === currentProjectId) {
                currentProjectId = null;
                clearProjectContent();
            }
            
            // 重新載入專案列表
            await loadProjects();
        } else {
            alert(data.message || '刪除專案失敗');
        }
    } catch (error) {
        console.error('刪除專案錯誤:', error);
        alert('刪除專案時發生錯誤');
    }
}

/**
 * HTML 轉義
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 從 URL 獲取專案 ID
 */
function getProjectIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('project_id');
}

// 頁面載入時初始化
document.addEventListener('DOMContentLoaded', async function() {
    // 從 URL 獲取專案 ID
    const projectId = getProjectIdFromURL();
    
    if (projectId) {
        // 如果有 project_id 參數，直接載入該專案資料（使用 /api/project/{project_id}）
        currentProjectId = projectId;
        await loadProjectData(projectId);
        // 然後載入專案列表（用於側邊欄顯示）
        await loadProjects();
    } else {
        // 如果沒有 project_id，先載入專案列表
        await loadProjects();
        // loadProjects 會自動選擇第一個專案（最近更新的）並載入其資料
    }
});
