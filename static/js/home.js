/**
 * 主頁 JavaScript 模組
 */

// 載入認證模組（如果尚未載入）
if (typeof getToken === 'undefined') {
    // 簡單的 token 獲取函數（如果 auth.js 未載入）
    function getToken() {
        return localStorage.getItem('access_token') || 
               document.cookie.split('; ').find(row => row.startsWith('access_token='))?.split('=')[1];
    }
}

// 全域變數：追蹤是否正在處理請求
let isProcessing = false;

/**
 * 處理貼上事件，清除格式只保留純文字
 */
function handlePaste(e) {
    e.preventDefault();
    
    // 獲取剪貼板中的純文字內容
    const text = (e.clipboardData || window.clipboardData).getData('text/plain');
    
    // 清除當前選取內容並插入純文字
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        range.deleteContents();
        
        // 創建文字節點並插入
        const textNode = document.createTextNode(text);
        range.insertNode(textNode);
        
        // 移動游標到插入文字的末尾
        range.setStartAfter(textNode);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);
    } else {
        // 如果沒有選取，直接插入到當前位置
        const textNode = document.createTextNode(text);
        e.target.appendChild(textNode);
    }
}

/**
 * 為輸入框添加貼上事件處理器
 */
function setupPasteHandler(element) {
    if (element && element.contentEditable === 'true') {
        element.addEventListener('paste', handlePaste);
    }
}

/**
 * 為所有可編輯的輸入框設置貼上處理器
 */
function setupAllPasteHandlers() {
    // 為現有的輸入框設置
    const inputAD = document.getElementById('inputAD');
    if (inputAD) {
        setupPasteHandler(inputAD);
    }
    
    // 為所有可編輯的內容設置
    document.querySelectorAll('.editable-content[contenteditable="true"]').forEach(element => {
        setupPasteHandler(element);
    });
}

/**
 * 主要檢測函數（第一次使用）
 */
function madetect() {
    // 檢查是否正在處理中
    if (isProcessing) {
        return;
    }

    const inputAD = document.getElementById("inputAD").textContent.trim();
    
    // 檢查輸入是否為空
    if (!inputAD) {
        alert('請輸入廣告詞');
        return;
    }

    // 設置處理中狀態
    setProcessingState(true);

    // 立即顯示結果框（帶 loading 狀態）
    showLoadingResults();

    // 發送請求
    sendDetectionRequest(inputAD)
        .then((response) => {
            // 更新結果框內容
            updateResults(response.result_law, response.result_advice);
            // 添加新的輸入框
            addNewElements(response.result_law, response.result_advice);
            // 重置處理狀態
            setProcessingState(false);
        })
        .catch((error) => {
            console.error('請求失敗:', error);
            alert('請求失敗，請回報相關問題');
            // 移除 loading 結果框
            removeLoadingResults();
            // 重新啟用輸入
            setProcessingState(false);
        });
}

/**
 * 主要檢測函數（後續使用）
 */
function madetects(container) {
    // 檢查是否正在處理中
    if (isProcessing) {
        return;
    }

    // 從傳入的 container 中獲取當前輸入框的內容
    const editableContent = container.querySelector('.editable-content');
    if (!editableContent) {
        alert('找不到輸入框');
        return;
    }
    
    const inputAD = editableContent.textContent.trim();
    
    // 檢查輸入是否為空
    if (!inputAD) {
        alert('請輸入廣告詞');
        return;
    }

    // 設置處理中狀態
    setProcessingState(true, container);

    // 立即顯示結果框（帶 loading 狀態）
    showLoadingResultsForContainer(container);

    // 發送請求
    sendDetectionRequest(inputAD)
        .then((response) => {
            // 更新結果框內容
            updateResultsForContainer(container, response.result_law, response.result_advice);
            // 添加新的輸入框
            addNewElementsD(container, response.result_law, response.result_advice);
            // 重置處理狀態
            setProcessingState(false);
        })
        .catch((error) => {
            console.error('請求失敗:', error);
            alert('請求失敗，請回報相關問題');
            // 移除 loading 結果框
            removeLoadingResults();
            // 重新啟用輸入
            setProcessingState(false, container);
        });
}

/**
 * 發送檢測請求
 */
function sendDetectionRequest(inputAd) {
    return new Promise((resolve, reject) => {
        // 獲取當前專案 ID
        const projectId = typeof currentProjectId !== 'undefined' ? currentProjectId : 
                         new URLSearchParams(window.location.search).get('project_id');
        
        if (!projectId) {
            alert('請先選擇或建立一個專案');
            reject(new Error('No project selected'));
            return;
        }
        
        // 使用 authenticatedFetch 或直接使用 fetch with token
        const token = getToken();
        
        $.ajax({
            url: '/madetect',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : ''
            },
            data: JSON.stringify({ 
                input_ad: inputAd,
                project_id: projectId
            }),
            success: function(response) {
                // 檢查 response 是否包含 success 欄位
                if (response && response.success === false) {
                    reject(new Error(response.message || '請求失敗'));
                } else {
                    resolve(response);
                }
            },
            error: function(error) {
                const errorData = error.responseJSON || {};
                const errorMessage = errorData.message || '請求失敗';
                
                // 如果是 401，可能需要重新登入
                if (error.status === 401) {
                    alert('登入已過期，請重新登入');
                    window.location.href = '/login';
                } else if (error.status === 429) {
                    // API 配額限制
                    alert(errorMessage + '\n\n免費層每日限制為 20 次請求，請稍後再試。');
                } else if (error.status === 400) {
                    alert(errorMessage || '請求失敗，請檢查是否已選擇專案');
                } else if (error.status === 500) {
                    alert(errorMessage || '伺服器錯誤，請稍後再試');
                } else if (error.status === 200) {
                    // 如果狀態碼是 200 但進入 error，可能是 JSON 解析問題
                    try {
                        const response = typeof error.responseJSON !== 'undefined' ? error.responseJSON : JSON.parse(error.responseText);
                        if (response && response.success === false) {
                            alert(response.message || '請求失敗');
                        } else {
                            resolve(response);
                            return;
                        }
                    } catch (e) {
                        console.error('解析回應錯誤:', e);
                    }
                } else {
                    alert(errorMessage || '請求失敗，請稍後再試');
                }
                reject(error);
            }
        });
    });
}

/**
 * 設置處理中狀態
 */
function setProcessingState(processing, container = null) {
    isProcessing = processing;
    
    let editableContent;
    let submitButton;
    
    if (container) {
        // 從 container 中獲取輸入框和按鈕
        editableContent = container.querySelector('.editable-content');
        submitButton = container.querySelector('.custom-button');
    } else {
        // 使用第一個輸入框（初始輸入框）
        editableContent = document.getElementById("inputAD");
        submitButton = document.getElementById("inputADbutton");
    }
    
    if (processing) {
        if (editableContent) {
            editableContent.setAttribute('contenteditable', 'false');
        }
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.style.opacity = '0.5';
            submitButton.style.cursor = 'not-allowed';
        }
    } else {
        if (editableContent) {
            editableContent.setAttribute('contenteditable', 'true');
        }
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.style.opacity = '1';
            submitButton.style.cursor = 'pointer';
        }
    }
}

/**
 * 顯示 loading 結果框（第一次使用）
 */
function showLoadingResults() {
    const container = document.querySelector('.r_side .r_container');
    
    // 移除現有的 loading 結果框（如果存在）
    removeLoadingResults();

    // 創建 loading 結果框
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-results';
    
    const newDivPink = createNewDiv(
        '專業醫療建議：', 
        'pink-bg', 
        false, 
        '<div style="text-align: center; padding: 20px; color: #666;"><i class="fas fa-spinner fa-spin"></i> 正在分析中，請稍候...</div>'
    );
    const newDivLgreen = createNewDiv(
        '以下是修改後的廣告詞：', 
        'Lgreen-bg', 
        false, 
        '<div style="text-align: center; padding: 20px; color: #666;"><i class="fas fa-spinner fa-spin"></i> 正在生成建議，請稍候...</div>'
    );
    const newDivBlackLine = createNewBlackLine();
    
    loadingDiv.appendChild(newDivPink);
    loadingDiv.appendChild(newDivLgreen);
    loadingDiv.appendChild(newDivBlackLine);
    
    container.insertAdjacentElement('afterend', loadingDiv);
    
    // 設置樣式
    setBorderColors(newDivPink, newDivLgreen);
}

/**
 * 顯示 loading 結果框（後續使用）
 */
function showLoadingResultsForContainer(container) {
    // 移除現有的 loading 結果框（如果存在）
    removeLoadingResults();

    // 創建 loading 結果框
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-results';
    
    const newDivPink = createNewDiv(
        '專業醫療建議：', 
        'pink-bg', 
        false, 
        '<div style="text-align: center; padding: 20px; color: #666;"><i class="fas fa-spinner fa-spin"></i> 正在分析中，請稍候...</div>'
    );
    const newDivLgreen = createNewDiv(
        '以下是修改後的廣告詞：', 
        'Lgreen-bg', 
        false, 
        '<div style="text-align: center; padding: 20px; color: #666;"><i class="fas fa-spinner fa-spin"></i> 正在生成建議，請稍候...</div>'
    );
    const newDivBlackLine = createNewBlackLine();
    
    loadingDiv.appendChild(newDivPink);
    loadingDiv.appendChild(newDivLgreen);
    loadingDiv.appendChild(newDivBlackLine);
    
    container.insertAdjacentElement('afterend', loadingDiv);
    
    // 設置樣式
    setBorderColors(newDivPink, newDivLgreen);
}

/**
 * 更新結果框內容（第一次使用）
 */
function updateResults(result_law, result_advice) {
    const loadingDiv = document.getElementById('loading-results');
    if (loadingDiv) {
        const pinkDiv = loadingDiv.querySelector('.pink-bg .editable-content');
        const greenDiv = loadingDiv.querySelector('.Lgreen-bg .editable-content');
        if (pinkDiv) pinkDiv.innerHTML = result_law;
        if (greenDiv) greenDiv.innerHTML = result_advice;
    }
}

/**
 * 更新結果框內容（後續使用）
 */
function updateResultsForContainer(container, result_law, result_advice) {
    const loadingDiv = document.getElementById('loading-results');
    if (loadingDiv) {
        const pinkDiv = loadingDiv.querySelector('.pink-bg .editable-content');
        const greenDiv = loadingDiv.querySelector('.Lgreen-bg .editable-content');
        if (pinkDiv) pinkDiv.innerHTML = result_law;
        if (greenDiv) greenDiv.innerHTML = result_advice;
    }
}

/**
 * 移除 loading 結果框
 */
function removeLoadingResults() {
    const loadingDiv = document.getElementById('loading-results');
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

/**
 * 添加新元素（第一次使用）
 */
function addNewElements(result_law, result_advice) {
    const editableContent = document.querySelector('.editable-content');
    const container = document.querySelector('.r_side .r_container');
    const content = editableContent.innerHTML;

    // 移除 loading 結果框
    removeLoadingResults();

    const newDivPink = createNewDiv('專業醫療建議：', 'pink-bg', false, result_law);
    const newDivLgreen = createNewDiv('以下是修改後的廣告詞：', 'Lgreen-bg', false, result_advice);
    const newDivBlackLine = createNewBlackLine();
    const newDivDgreen = createNewDiv('請輸入廣告詞', 'Dgreen-bg', true, '');

    container.insertAdjacentElement('afterend', newDivDgreen);
    newDivDgreen.insertAdjacentElement('beforebegin', newDivBlackLine);
    newDivBlackLine.insertAdjacentElement('beforebegin', newDivLgreen);
    newDivLgreen.insertAdjacentElement('beforebegin', newDivPink);

    const buttonContainer = document.createElement('div');
    buttonContainer.classList.add('button-container');
    newDivDgreen.appendChild(buttonContainer);

    const newButton = document.createElement('button');
    newButton.classList.add('custom-button');
    newButton.innerHTML = '<img src="/static/pic/send4.png" width="24px" height="24px" alt="送出">';
    newButton.onclick = function() {
        madetects(newDivDgreen);
    };

    buttonContainer.appendChild(newButton);

    setBorderColors(newDivPink, newDivLgreen, newDivDgreen);

    editableContent.innerHTML = content;
    editableContent.setAttribute('contenteditable', 'false');

    const customButton = document.querySelector('.custom-button');
    if (customButton) {
        newButton.style.width = customButton.offsetWidth + 'px';
        newButton.style.height = customButton.offsetHeight + 'px';
    }
}

/**
 * 添加新元素（後續使用）
 */
function addNewElementsD(container, result_law, result_advice) {
    // 移除 loading 結果框
    removeLoadingResults();

    const newDivPink = createNewDiv('專業醫療建議：', 'pink-bg', false, result_law);
    const newDivLgreen = createNewDiv('以下是修改後的廣告詞：', 'Lgreen-bg', false, result_advice);
    const newDivBlackLine = createNewBlackLine();
    const newDivDgreen = createNewDiv('請輸入廣告詞', 'Dgreen-bg', true, '');

    container.insertAdjacentElement('afterend', newDivDgreen);
    newDivDgreen.insertAdjacentElement('beforebegin', newDivBlackLine);
    newDivBlackLine.insertAdjacentElement('beforebegin', newDivLgreen);
    newDivLgreen.insertAdjacentElement('beforebegin', newDivPink);

    const buttonContainer = document.createElement('div');
    buttonContainer.classList.add('button-container');
    newDivDgreen.appendChild(buttonContainer);

    const newButton = document.createElement('button');
    newButton.classList.add('custom-button');
    newButton.innerHTML = '<img src="/static/pic/send4.png" width="24px" height="24px" alt="送出">';
    newButton.onclick = function() {
        madetects(newDivDgreen);
    };

    buttonContainer.appendChild(newButton);

    setBorderColors(newDivPink, newDivLgreen, newDivDgreen);

    const oldButton = container.querySelector('.custom-button');
    if (oldButton) {
        newButton.style.width = oldButton.offsetWidth + 'px';
        newButton.style.height = oldButton.offsetHeight + 'px';
    }

    const buttonContainerWidth = buttonContainer.offsetWidth;
    newButton.style.marginLeft = buttonContainerWidth - newButton.offsetWidth + 'px';

    const newEditableContentPink = newDivPink.querySelector('.editable-content');
    const newEditableContentLgreen = newDivLgreen.querySelector('.editable-content');
    newEditableContentPink.setAttribute('contenteditable', 'false');
    newEditableContentLgreen.setAttribute('contenteditable', 'false');
    
    // 為新的輸入框設置貼上處理器
    const newInputAD = newDivDgreen.querySelector('#inputAD');
    if (newInputAD && typeof setupPasteHandler !== 'undefined') {
        setupPasteHandler(newInputAD);
    }
}

/**
 * 創建新 div 元素
 */
function createNewDiv(titleText, bgColorClass, editable, backendresult) {
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

    // 違反法條
    if (bgColorClass == 'pink-bg') {
        newEditableContent.innerHTML = backendresult;
    }
    // 修改後廣告
    else if (bgColorClass == 'Lgreen-bg') {
        newEditableContent.innerHTML = backendresult;
    }
    // 新輸入框
    else {
        const oldInputAD = document.getElementById("inputAD");
        if (oldInputAD) {
            oldInputAD.removeAttribute("id");
        }
        newEditableContent.setAttribute('id', 'inputAD');
        newEditableContent.setAttribute('name', 'input_ad');
        newEditableContent.innerHTML = '';
        
        // 為新的輸入框設置貼上處理器
        if (typeof setupPasteHandler !== 'undefined') {
            setupPasteHandler(newEditableContent);
        }
    }

    newInputBlock.appendChild(newEditableContent);
    newDiv.appendChild(newTitle);
    newDiv.appendChild(newInputBlock);

    return newDiv;
}

/**
 * 創建黑色分隔線
 */
function createNewBlackLine() {
    const newDivBlackLine = document.createElement('div');
    newDivBlackLine.classList.add('black-line');
    return newDivBlackLine;
}

/**
 * 設置邊框顏色
 */
function setBorderColors(pinkDiv, greenDiv, darkGreenDiv = null) {
    if (pinkDiv) {
        const title = pinkDiv.querySelector('.title');
        if (title) {
            pinkDiv.style.borderColor = window.getComputedStyle(title).backgroundColor;
        }
    }
    if (greenDiv) {
        const title = greenDiv.querySelector('.title');
        if (title) {
            greenDiv.style.borderColor = window.getComputedStyle(title).backgroundColor;
        }
    }
    if (darkGreenDiv) {
        const title = darkGreenDiv.querySelector('.title');
        if (title) {
            darkGreenDiv.style.borderColor = window.getComputedStyle(title).backgroundColor;
        }
    }
}

// 頁面載入完成後設置所有輸入框的貼上處理器
document.addEventListener('DOMContentLoaded', function() {
    if (typeof setupAllPasteHandlers !== 'undefined') {
        setupAllPasteHandlers();
    }
});
