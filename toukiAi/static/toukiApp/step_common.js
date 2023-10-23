"use strict";

/*
    変数
*/
let resizeFlg;

const rootPath = "/toukiapp/";
const steps = {
    step1: "service-stepOne",
    step2: "service-stepTwo",
    step3: "service-stepThree",
    step4: "service-stepFour",
    step5: "service-stepFive",
    step6: "service-stepSix",
    step7: "service-inquiry",
};
const stepNumbers = ["One", "Two", "Three", "Four", "Five", "Six"];
const username = document.getElementById("linkToAccount").innerHTML;

/**
 * サイドバーを更新する
 */
function updateSideBar(){
    setSideBarTop();
    setSidebarHeight();
}

/**s
 * 各進捗ボタンのアイコン、リンク、ボタンを設定する
 * @param {number} stepNumber 
 */
function updateStep(stepNumber){

    for(let i = 0; i < stepNumber; i++){
        const arrow = document.getElementById(`step${stepNumbers[i]}Arrow`);
        const done = document.getElementById(`step${stepNumbers[i]}Done`);
        const btn = document.getElementById(`btnStep${stepNumbers[i]}`);
        const link = document.getElementById(`step${stepNumbers[i]}Link`);

        i === stepNumber - 1 ? arrow.style.display = "block": done.style.display = "block";

        btn.disabled = false;
        link.href = `${rootPath}service-step${stepNumbers[i]}`;
        btn.classList.add("fw-bold");
    }
}

/**
 *  サイドバーの高さを設定
 */
function setSidebarHeight(){

    if (resizeFlg !== false) {
        clearTimeout(resizeFlg);
    }

    resizeFlg = setTimeout(function(){
    let headerHeight = header.clientHeight;
    let pageHeight = document.documentElement.clientHeight;
    // let mainHeight = document.getElementById("main").clientHeight;
    // let gap = mainHeight - pageHeight;
    let vh = pageHeight - headerHeight - 32;
    
    document.documentElement.style.setProperty('--vh', `${vh}px`);
    }, 300);
}

/*
    サイドバーの高さの位置を設定
*/
function setSideBarTop(){
    let gap = 16
    let top = header.clientHeight + gap;
    document.documentElement.style.setProperty('--top', `${top}px`);
}

function hiddenSidebar(){
    let width = document.documentElement.clientWidth;
    if(width < 975){
        linkToProgressArea.style.display = "block";
        sidebar.classList.remove("d-flex");
        sidebar.style.display = "none";
    }else{
        linkToProgressArea.style.display = "none";
        sidebar.classList.add("d-flex");
        sidebar.style.display = "";
    }
}

function setNavTogglerStyle(){
    let width = document.documentElement.clientWidth;

    //ハンバーガーメニューが表示されたとき
    if(width < 558){
        //ロゴの要素を修正
        logoArea.classList.remove("navbar-brand");
        logoArea.classList.add("mt-3", "fw-bold", "fs-5");
        logo.innerHTML = "トップページ";

        //ユーザー名の要素を修正
        linkToAccountArea.classList.add("mt-2", "fs-5");
        linkToAccount.innerHTML = "登録情報確認"

        //進捗状況の要素を修正
        linkToProgressArea.classList.add("mt-2", "fs-5");
        linkToProgressArea.classList.remove("ms-3");
        linkToProgress.classList.add("text-decoration-none", "text-dark", "cursor-pointer")
        linkToProgress.classList.remove("btn", "btn-outline-primary", "p-2");

        linkToProgress.addEventListener("mouseover", ()=>{
            linkToProgress.classList.remove("text-dark");
            emphasizeText(linkToProgress);
        })
        linkToProgress.addEventListener("mouseout", ()=>{
            linkToProgress.classList.add("text-dark");
            removeEmphasizeText(linkToProgress);
        })

        //ログアウトの要素を修正
        logoutArea.classList.add("mt-2", "fs-5");
        logoutArea.classList.remove("my-0", "ms-auto", "me-0");
        logout.classList.add("text-dark")
        logout.classList.remove("btn", "btn-outline-primary", "p-2");

        logout.addEventListener("mouseover", ()=>{
            logout.classList.remove("text-dark");
            emphasizeText(logout);
        })
        logout.addEventListener("mouseout", ()=>{
            logout.classList.add("text-dark");
            removeEmphasizeText(logout);
        })

    }else{
        //ロゴ要素を元に戻す
        logoArea.classList.add("navbar-brand");
        logoArea.classList.remove("mt-3", "fw-bold", "fs-5");
        logo.innerHTML = "（ロゴ）";

        //ユーザー名の要素を修正
        linkToAccountArea.classList.remove("mt-2", "fs-5");
        linkToAccount.innerHTML = username;

        //進捗状況の要素を修正
        linkToProgressArea.classList.remove("mt-2", "fs-5");
        linkToProgressArea.classList.add("ms-3");
        linkToProgress.classList.remove("text-decoration-none", "text-dark", "cursor-pointer")
        linkToProgress.classList.add("btn", "btn-outline-primary", "p-2");

        
        linkToProgress.removeEventListener("mouseover", ()=>{
            linkToProgress.classList.remove("text-dark");
            emphasizeText(linkToProgress);
        })
        linkToProgress.removeEventListener("mouseout", ()=>{
            linkToProgress.classList.add("text-dark");
            removeEmphasizeText(linkToProgress);

        })
        
        //ログアウトの要素を修正
        logoutArea.classList.remove("mt-2", "fs-5");
        logoutArea.classList.add("my-0", "ms-auto", "me-0");
        logout.classList.remove("text-dark")
        logout.classList.add("btn", "btn-outline-primary", "p-2");

        
        logout.removeEventListener("mouseover", ()=>{
            logout.classList.remove("text-dark");
            emphasizeText(logout);
        })
        logout.removeEventListener("mouseout", ()=>{
            logout.classList.add("text-dark");
            removeEmphasizeText(logout);
        })
    }
}

/**
 * 次へのボタンのトグル
 * @param {boolean} isValid チェック結果
 * @param {element} el チェック対象の要素
 * @param {number} index ボタン要素のインデックス
 */
function toggleNextBtn(isValid, el, index){
    //入力値が適切なとき
    if(isValid){
        //配列に取得
        if(invalidEls.indexOf(el) !== -1) invalidEls.push(el);
        //次へのボタンを無効化
        nextBtns[index].disabled = true;
    }else{
        //配列から削除
        invalidEls = invalidEls.filter(x => x !== el);
        //次へボタンを有効化判別
        if(invalidEls.length === 0) nextBtns[index].disabled = false;
    }
}

/**
 * 入力値チェック後の処理
 * @param {boolean} isValid 入力値のチェック結果
 * @param {element} messageEl エラーメッセージを表示する要素
 * @param {string} message エラーメッセージ
 * @param {element} el チェック対象の要素
 * @param {element} nextBtn 次へボタン
 */
function afterValidation(isValid, messageEl, message, el, nextBtn){
    //入力値が適切なとき
    if(isValid){
        //エラーメッセージを隠す
        messageEl.style.display = "none";
        //次へボタンを有効化判別
        if(invalidEls.length === 0) nextBtn.disabled = false;        
    }else{
        //エラーメッセージを表示する
        messageEl.innerHTML = message;
        messageEl.style.display = "block";
        //配列に取得
        invalidEls.push(el);
        //次へのボタンを無効化
        nextBtn.disabled = true;
        el.value = "";
    }
}

/**
 * 引数に渡された１つ又は配列に入った要素の子要素として存在するinput要素を全て初期化する
 * @param {HTMLElement[]|HTMLElement} els 初期化したいinput要素が属する親要素（配列形式じゃなくてもOK）
 */
function iniAllInputs(els){
    if(!Array.isArray(els)) els = [els];

    for (let i = 0; i < els.length; i++) {
        const inputs = els[i].getElementsByTagName('input');
        for (let j = 0; j < inputs.length; j++) {
            inputs[j].disabled = false;
            if (inputs[j].type === 'text') inputs[j].value = '';
            else if (inputs[j].type === 'radio') inputs[j].checked = false;
            else if (inputs[j].type === 'number') inputs[j].value = "0";
        }
    }
}

/**
 * 最初の要素以外全て削除する
 * @param {array} els 
 */
function removeAll(els){
    els.forEach((el) => {
        el.parentNode.removeChild(el);
    });
}

/**
 * 最初の要素以外全て削除する
 * @param {HTMLElement[]|HTMLCollection} els 
 */
function removeAllExceptFirst(els){
    for (let i = els.length - 1; i > 0; i--) {
        els[i].parentNode.removeChild(els[i]);
    }
}

/**
 * ボタン要素のチェックを全てfalseにする
 * @param {element array} els 配列に格納されたボタン要素
 * @param {num} idxs 初期化するボタン要素のインデックス
 */
function uncheckTargetElements(els, idxs){
    idxs.forEach(idx => {
        els[idx].checked = false;
    });
}

/**
 * 要素を入れ替える（イベントをまとめて削除したいときに使用）
 * @param {element} field 対象の要素の親要素
 * @param {string} tagName 対象の要素
 */
function replaceElements(field, tagName){
    let els = field.getElementsByTagName(tagName);
    for (let i = 0; i < els.length; i++) {
        let oldEl = els[i];
        let newEl = oldEl.cloneNode(true);
        oldEl.parentNode.replaceChild(newEl, oldEl);
    }
}

/**
 * 引数で渡された要素より前にある一番近い特定のタグの要素を返す
 * @param {HTMLElement} el 基準となる要素
 * @param {string} tagName 取得したい要素のタグ名
 * @return 引数で渡された要素より前にある一番近い特定のタグの要素
 */
function getPreElByTag(el, tagName){
    let i = 0;
    while (el && i < 10) {
        el = el.previousElementSibling;
        i++;
        if (el && el.matches(`${tagName}`)) {
            return el;
        }
    }
}

/**
 * 引数で渡された要素より後ろにある特定のタグの一番最初の要素を返す
 * @param {HTMLElement} el 基準となる要素
 * @param {string} tagName 取得したい要素のタグ名
 * @return 引数で渡された要素の後ろにある特定のタグの一番最初の要素
 */
function getNextElByTag(el, tagName){
    let i = 0;
    while (el && i < 10) {
        el = el.nextElementSibling;
        i++;
        if (el && el.matches(`${tagName}`)) {
            return el;
        }
    }
}

/**
 * 特定の形式のクラス名を削除する
 * @param {HTMLElement} el 
 * @param {RegExp} pattern 
 * @returns クラスを削除した後の要素
 */
function removeSpecificPatternClass(el, pattern){
    el.classList.forEach(className => {
        if(pattern.test(className))
            el.classList.remove(className);
    });
    return el;
}


/*
    イベント
*/
window.addEventListener("load", ()=>{
    setSidebarHeight();
    setSideBarTop();
    hiddenSidebar();
    setNavTogglerStyle();
})

//画面サイズが変更されたとき
window.addEventListener('resize', () => {
    hiddenSidebar();
    setNavTogglerStyle();
});