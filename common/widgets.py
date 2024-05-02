class WidgetAttributes:
    """フォームの属性集"""
    # メールアドレス
    # ラジオボタン
    radio = {
        "class": "form-check-input",
    }
    # チェックボックス
    checkbox = {
        "class": "form-check-input cb",
    }
    # セレクト
    select = {
        "class": "form-select text-center cursor-pointer rounded-end"
    }
    # 隠しinput
    hidden_input = {
        "class": "hidden"
    }
    email = {
        'class': 'form-control rounded-end',
        'autocomplete': 'on',
        "placeholder": "弊社からの回答を受け取るメールアドレス",
    }
    # 問い合わせ内容
    inquiry_content = {
        'class': 'form-control rounded-end',
        "placeholder": "300文字まで",
        "style":"resize:none;"
    }
    # 評価額
    price = {
        "placeholder": "数字のみで入力（コンマ不要）",
        "class": "form-control text-center rounded-end",
        "maxlength": "16",
    }
    # 請求額
    charge = {
        "placeholder": "",
        "class": "form-control text-center rounded-end fw-bold",
        "maxlength": "7",
        "disabled": "true"
    }
    # 氏名（登記用）
    name = {
        "class": "form-control rounded-end",
        "placeholder": "姓名の間にスペースなし",
        "maxlength": "30",
    }
    # 氏名（通常）
    name_normal = {
        "class": "form-control rounded-end",
        "placeholder": "",
        "maxlength": "30",
    }
    # 振込名義人
    payer = {
        "class": "form-control rounded-end",
        "placeholder": "ひらがな又はカタカナで入力",
        "maxlength": "30"
    }
    # カウントする入力欄
    count = {
        "class": "form-control text-center no-spin",
    }
    # 本籍の町域・番地
    domicile_address = {
        "class": "form-control rounded-end",
        "placeholder": "中央区天神１丁目１番",
        "maxlength": "100",
    }
    # 住所の町域・番地
    address = {
        "class": "form-control rounded-end",
        "placeholder": "中央区天神１丁目１番１号",
        "maxlength": "100",
    }
    # 住所の建物
    bldg = {
        "class": "form-control rounded-end",
        "placeholder": "登記マンション１０１号室",
        "maxlength": "100",
    }
    # 不動産番号
    rs_number = {
        "class": "form-control rounded-end",
        "placeholder": "謄本右上にある１３桁の数字",
        "maxlength": "13",
    }
    # 土地の所在地
    land_address = {
        "class": "form-control rounded-end",
        "placeholder": "福岡県福岡市中央区天神１丁目",
        "maxlength": "100",
    }
    # 建物の所在地
    house_address = {
        "class": "form-control rounded-end",
        "placeholder": "福岡県福岡市中央区天神１丁目１番地１",
        "maxlength": "100",
    }
    # 一棟の建物の所在
    bldg_address = {
        "class": "form-control rounded-end",
        "placeholder": "一棟の建物の表示にある所在",
        "maxlength": "100",        
    }
    # 区分建物の家屋番号
    bldg_number = {
        "class": "form-control rounded-end",
        "placeholder": "専有部分の建物の表示にある家屋番号",
        "maxlength": "100",        
    }
    # 敷地権の所在及び地番
    site_address_and_number = {
        "class": "form-control rounded-end",
        "placeholder": "地番の表記は「番地」ではなく「番」です",
        "maxlength": "100",
    }
    # 敷地権の土地の符号
    site_order_number = {
        "class": "form-control rounded-end text-center",
        "maxlength": "3",
    }
    # 分子または分母の入力欄
    fraction = {
        "class": "mx-1 p-0 fraction form-control text-center",
        "maxlength": "10",        
    }
    # 法務局
    office = {
        "class": "form-control rounded-end text-center",
        "placeholder": "不動産番号を入力すると自動で表示されます",
        "maxlength": "30",
        "disabled": "true",
    }
    # 一括住所
    full_address = {
        "class": "form-control rounded-end",
        "placeholder": "福岡県福岡市中央区天神１丁目１番１号",
        "maxlength": "100",        
    }
    full_address_2 = {
        "class": "form-control rounded-end",
        "placeholder": "書類が届く宛先",
        "maxlength": "100"
    }
    # 電話番号（ハイフンあり）
    phone_number = {
        "class": "form-control rounded-end",
        "placeholder": "ハイフンあり",
        "maxlength": "13",
    }
    # 電話番号（ハイフンなし）
    phone_number_no_hyphen = {
        "class": "form-control rounded-end",
        "placeholder": "ハイフンなし",
        "maxlength": "11",
    }