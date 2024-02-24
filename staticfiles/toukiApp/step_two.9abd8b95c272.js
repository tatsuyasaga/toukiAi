"use strict";

/*
    変数
*/
const registryUploader = document.getElementById("registryUploader");
const registryUploaderInput = document.getElementById("registryUploaderInput");
const trash = document.getElementById("trash");
const registryList = document.getElementById("registryList");
const registryFiles = [];
const displayNextEls = document.getElementsByClassName("displayNextEl");
const certificateRbs = document.getElementsByName("certificate");
const reqDocCbs = document.getElementsByClassName("reqDocCb");
const preBtn = document.getElementById("preBtn");

/**
 * 初期値を入力する
 */
function inputInitData(){

    // 不動産登記簿があるとき、反映させる
    if(app_server_file_name_and_file_path.length > 0){
        app_server_file_name_and_file_path.forEach(file_name_and_file_path => {
            fetch(file_name_and_file_path.path)
                .then(response => response.blob())
                .then(blob => {
                    // BlobをFileオブジェクトに変換
                    let file = new File([blob], file_name_and_file_path.name);
                    
                    // FileオブジェクトをDataTransferオブジェクトに追加
                    let dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    // FileオブジェクトをregistryFilesに追加
                    Array.from(dataTransfer.files).forEach(file => {
                        registryFiles.push(file);
                    });
                    addFileName(file);
                    
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    }

    //ステップ３以上に進んでいるとき
    if(progress >= 3){
        //必要書類全てにチェックを入れる
        Array.from(reqDocCbs).forEach(cb => cb.checked = true);
        submitBtn.disabled = false;
    }
}

/**
 * 初期化
 */
function initialize(){
    //進捗の表示を更新する
    updateSideBar();
    inputInitData();
}

/**
 * 弟要素を表示する
 * @param {HTMLElement} el 
 */
function displayNextEl(el){
    const sibling = el.nextElementSibling;
    if(sibling.style.display === "none"){
        el.classList.remove("arrow-right");
        el.classList.add("arrow-down");
        slideDown(sibling);
    }else{
        slideUp(sibling);
        el.classList.remove("arrow-down");
        el.classList.add("arrow-right");
    }
}

/**
 * 必要書類を全て取得したか判別する
 */
function isComp(){
    submitBtn.disabled = Array.from(reqDocCbs).every(cb => cb.checked) ? false: true;
}

/**
 * アップロード済みの登記情報リストにファイル名を追加する
 */
function addFileName(file){
    //１つ目のアップロードファイルのとき
    if(registryFiles.length === 1){
        const cb = registryList.querySelector("input");
        cb.disabled = false;
        cb.addEventListener("change", (e)=>{
            const cbs = registryList.querySelectorAll("input");
            trash.disabled = !Array.from(cbs).some(cb => cb.checked);
        })        
        registryList.querySelector("label").textContent = file.name;
    }else if(registryFiles.length > 1){
        //最後のliをコピペしてinputのidとlabelのforを変更してlabelのテキストにファイル名を代入する
        const copyFrom = getLastElByAttribute("li", "tag", registryList)
        const clone = copyFrom.cloneNode(true); 
        copyFrom.insertAdjacentElement('afterend', clone);
        const newAttName = `registry${registryFiles.length}`
        clone.querySelector("input").id = newAttName;
        clone.querySelector("label").htmlFor = newAttName;
        clone.querySelector("label").textContent = file.name;
        const cb = clone.querySelector("input");
        cb.disabled = false;
        cb.addEventListener("change", (e)=>{
            const cbs = registryList.querySelectorAll("input");
            trash.disabled = !Array.from(cbs).some(cb => cb.checked);
        })        
    }
}

/*
    イベント
*/
window.addEventListener("load", ()=>{
    //初期処理
    initialize();

    //displayNextElクラスを持つボタン要素にイベントを設定
    Array.from(displayNextEls).forEach(el => {
        el.addEventListener("click", () => displayNextEl(el));
    });

    //権利証の有無のラジオボタンにイベントを設定
    for(let i = 0, len = certificateRbs.length; i < len; i++){
        if(i === 0){
            certificateRbs[i].addEventListener("change", (e)=>{
                if(e.target.checked){
                    document.getElementById("CbdecedentResidentCard").checked = true;
                    slideUp(document.getElementById("DivAltCertificate"));
                }
            })
        }else{
            certificateRbs[i].addEventListener("change", (e)=>{
                if(e.target.checked){
                    document.getElementById("CbdecedentResidentCard").checked = false;
                    slideDown(document.getElementById("DivAltCertificate"));
                }
            })
        }
    }

    //必要書類のチェックボックスにイベントを設定
    Array.from(reqDocCbs).forEach(el => {
        el.addEventListener("click", () => isComp());
    });
})

//表示画面のサイズが変わったとき
window.addEventListener('resize', () => {
    //進捗欄の高さを変更する
    setSidebarHeight();
});

//登記情報アップロードのエリアをクリックしたとき
registryUploader.addEventListener('click', function() {
    //アップロードinputをクリックする
    document.getElementById('registryUploaderInput').click();
});

//ファイルがアップロードされたとき
registryUploaderInput.addEventListener("change", (e)=>{
    const newFiles = Array.from(e.target.files).filter(file => 
        !registryFiles.some(regFile => regFile.name === file.name)
      );

    //アップロードされたファイル全てに対する処理
    for(let i = 0, len = newFiles.length; i < len ; i++){
        const file = newFiles[i];
        //5Mbを超えるときはエラーを返す
        const size = file.size;
        if(size / (1024*1024) > 5){
            alert("５MBを超えるファイルはアップロードできません。\n５MBを超えるファイルをアップロードする場合は、サポートまでお問い合わせをお願いします。")
            return;
        }

        //ファイルを変数に保存する
        registryFiles.push(file);

        //リストにファイル名を追加する
        addFileName(file);
    }
    //次に同じファイルが選択されてもchangeイベントが発生するようにする
    e.target.value = '';
})

// ドラッグオーバーイベントのデフォルト処理をキャンセル
registryUploader.addEventListener('dragover', function(e) {
    e.preventDefault();
});

// ドロップイベントのデフォルト処理をキャンセルし、選択されたファイルをinput要素に設定
registryUploader.addEventListener('drop', function(e) {
    e.preventDefault();
    registryUploaderInput.files = e.dataTransfer.files;
    const event = new Event("change");
    registryUploaderInput.dispatchEvent(event);
});

//ゴミ箱がクリックされたとき
trash.addEventListener("click", (e)=>{
    //チェックされた（削除対象の）ボタンのみを取得する
    const cbs = registryList.querySelectorAll("input");
    const checkedCbs = Array.from(cbs).filter(cb => cb.checked);

    //チェックされたファイルのファイルとファイル名を削除する
    for(let i = checkedCbs.length - 1; i >= 0; i--) {
        const cb = checkedCbs[i];
        const index = Array.from(cbs).indexOf(cb);
        //アップロードファイルを格納している配列からファイルを削除する
        if (index > -1) {
            registryFiles.splice(index, 1);
        }

        //全て削除されたとき
        if(registryFiles.length === 0){
            //最初のリスト以外を削除する
            registryList.querySelector("label").textContent = "";
            const cb = registryList.querySelector("input");
            cb.checked = false;
            cb.disabled = true;
            const lists = registryList.querySelectorAll("li");
            for (let i = 1; i < lists.length; i++) {
                registryList.removeChild(lists[i]);
            }
        }else if(registryFiles.length > 0){
            //１つ以上ファイルが残っているとき、チェックされたリストを削除する
            const listItem = cb.closest('li');
            registryList.removeChild(listItem);
        }
    }

    //残っているファイルのinputとlabelの属性を更新する
    const inputs = registryList.querySelectorAll("input");
    const labels = registryList.querySelectorAll("label");
    for(let i = 0, len = inputs.length; i < len; i++){
        const newAttName = `registry${i+1}`
        inputs[i].id = newAttName;
        labels[i].htmlFor = newAttName;
    }

    trash.disabled = true;
})

form.addEventListener("submit", function(e){
    e.preventDefault();  // フォームのデフォルトの送信動作をキャンセル
    
    let formData = new FormData(this);  // 既存のフォームデータを取得
    registryFiles.forEach((pdfFile, index) => {
        formData.append('pdf' + index, pdfFile);  // 各PDFファイルを追加
    });
    // ローディングメッセージを表示
    document.getElementById("spinner").style.display = "";
    submitBtn.disabled = true;

    fetch('step_two', {  // PythonビューのURL
        method: 'POST',
        body: formData
    })
    .then(response => {
        return response.json();
    }).then(data => {
        if (data.status === 'success'){
            window.location.href = 'step_three';
        }else if(data.status === "error"){
            window.location.href = 'step_two';
        }
    })
    .catch(error => {
        window.location.href = 'step_two';
        console.error('Error:', error);
    });
})

preBtn.addEventListener("click", ()=>{
    document.getElementById("spinner").style.display = "";
    preBtn.disabled = true;
    const data = { "progress" : 1.5 };
    fetch('step_back', {  // PythonビューのURL
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        mode: "same-origin"
    }).then(response => {
        return response.json();
    }).then(response => {
        if (response.status === 'success'){
            window.location.href = 'step_one';
        }else if(response.status === "error"){
            window.location.href = 'step_two';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        window.location.href = 'step_two';

    });
})