from django.shortcuts import render, redirect, get_object_or_404
from .prefectures import PREFECTURES
from .landCategorys import LANDCATEGORYS
from .customDate import *
from .sections import *
from .company_data import *
from .forms import *
from django.forms import formset_factory
from .models import *
from accounts.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import datetime
import json
from django.http import JsonResponse
import requests
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
import textwrap
from django.core.mail import BadHeaderError, EmailMessage
from django.http import HttpResponse
from django.db import transaction, DatabaseError, OperationalError
from smtplib import SMTPException
import socket
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.db.models import Q, F
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import googleapiclient.errors 
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import gdown
from django.core.files.storage import default_storage
import os
from django.conf import settings
from urllib.parse import urlparse, parse_qs
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from bs4 import BeautifulSoup
import logging
import inspect
from requests.exceptions import HTTPError, ConnectionError, Timeout
import traceback
from django.db.models.query import QuerySet
from collections import defaultdict

logger = logging.getLogger(__name__)

def index(request):
    is_inquiry = False
    
    if "post_success" in request.session and request.session["post_success"]:
        is_inquiry = True
        del request.session["post_success"]
    
    if request.method == "POST":
        form = OpenInquiryForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                function_name = get_current_function_name()
                try:
                    form.save()
                    subject = CompanyData.APP_NAME + "：お問い合わせありがとうございます"
                    content = textwrap.dedent('''
                        このメールはシステムからの自動返信です。
                        送信専用のメールアドレスのため、こちらにメールいただいても対応できません。

                        以下の内容でお問い合わせを受け付けました。
                        
                        原則２４時間以内にご回答いたしますので、恐れ入りますが今少しお時間をください。
                        ※金土日祝日にお問い合わせいただいた場合は、翌月曜日になることもあります。
                        
                        ----------------------------------

                        件名
                        {subject}

                        お問い合わせ内容
                        {content}
                        
                        -----------------------------------
                        {company_sub_name}
                        {company_name}
                        {company_post_number}
                        {company_address}
                        受信専用電話番号 {company_receiving_phone_number}
                        発信専用電話番号 {company_calling_phone_number}
                        営業時間 {company_opening_hours}
                        ホームページ {company_url}
                    ''').format(
                        subject=form.cleaned_data["subject"],
                        content=form.cleaned_data["content"],
                        company_name=CompanyData.NAME,
                        company_post_number=CompanyData.POST_NUMBER,
                        company_address=CompanyData.ADDRESS,
                        company_receiving_phone_number=CompanyData.RECEIVING_PHONE_NUMBER,
                        company_calling_phone_number=CompanyData.CALLING_PHONE_NUMBER,
                        company_opening_hours=CompanyData.OPENING_HOURS,
                        company_url=CompanyData.URL,
                    )
                    to_list = [form.cleaned_data["created_by"]]
                    bcc_list = ["toukiaidev@gmail.com"]
                    message = EmailMessage(subject=subject, body=content, from_email="toukiaidev@gmail.com", to=to_list, bcc=bcc_list)
                    message.send()
                    request.session["post_success"] = True
                    
                except BadHeaderError as e:
                    basic_log(function_name, e, None, "無効なヘッダ")
                    messages.error(request, f'無効なヘッダが検出されました {e}')
                except SMTPException as e:
                    basic_log(function_name, e, None, "SMTPエラー")
                    messages.error(request, f'SMTPエラーが発生しました {e}')
                except socket.error as e:
                    basic_log(function_name, e, None, "ネットワークエラー")
                    messages.error(request, f'ネットワークエラーが発生しました {e}')
                except ValidationError as e:
                    basic_log(function_name, e, None)
                    messages.error(request, "データの保存に失敗しました。入力内容を確認してください。")
                except Exception as e:
                    basic_log(function_name, e, None)
                    messages.error(request, f'予期しないエラーが発生しました {e}')
            
        else:
            basic_log(function_name, None, None, "入力内容に誤り")
            messages.warning(request, "入力内容に誤りがあったため受付できませんでした")
            
        return redirect("/toukiApp/index")
            
    else:
        forms = OpenInquiryForm()
        
    update_articles = UpdateArticle.objects.order_by("-updated_by")[:2]
    
    context = {
        "title" : "トップページ",
        "update_articles": update_articles,
        "forms": forms,
        "company_app_name": CompanyData.APP_NAME,
        "company_mail_address": CompanyData.MAIL_ADDRESS,
        "company_service": Service,
        "is_inquiry": is_inquiry,
    }
    
    return render(request, "toukiApp/index.html", context)

# ステップ１のデータ登録処理
def save_step_one_datas(user, forms, form_sets):
    # すべてのデータを削除する
    
    decedent = forms[0].save(commit=False)
    Decedent.objects.filter(user=user).delete()
    decedent.progress = 2
    decedent.user = user
    decedent.created_by = user
    decedent.updated_by = user
    decedent.save()
    
    # 配偶者
    spouse = forms[1].save(commit=False)
    spouse.decedent = decedent
    spouse.content_type = ContentType.objects.get_for_model(Decedent)
    spouse.object_id = decedent.id
    spouse.is_heir = forms[1].cleaned_data.get("is_live") and forms[1].cleaned_data.get("is_refuse") == False
    spouse.created_by = user
    spouse.updated_by = user
    spouse.save()
    
    # 子共通
    child_common = forms[2].save(commit=False)
    child_common.decedent = decedent
    child_common.created_by = user
    child_common.updated_by = user
    child_common.save()
    
    # 子
    child_dict = {}
    for form in form_sets[0]:
        if form.cleaned_data.get("name"):
            child = form.save(commit=False)
            child.decedent = decedent
            child.content_type1 = ContentType.objects.get_for_model(Decedent)
            child.object_id1 = decedent.id
            if(form.cleaned_data.get("target2") != ""):
                child.content_type2 = ContentType.objects.get_for_model(Spouse)
                child.object_id2 = spouse.id
            child.is_heir = form.cleaned_data.get("is_live") and form.cleaned_data.get("is_refuse") == False
            child.created_by = user
            child.updated_by = user
            child.save()
            child_dict[form.cleaned_data.get("index")] = child
            
    # 子の配偶者
    child_spouse_dict = {}
    for form in form_sets[1]:
        if form.cleaned_data.get("name"):
            child_spouse = form.save(commit=False)
            child_spouse.decedent = decedent
            if form.cleaned_data.get("target") in child_dict:
                child_spouse.content_type = ContentType.objects.get_for_model(Descendant)
                child_spouse.object_id = child_dict[form.cleaned_data.get("target")].id
            child_spouse.is_heir = form.cleaned_data.get("is_live") and form.cleaned_data.get("is_refuse") == False
            child_spouse.created_by = user
            child_spouse.updated_by = user
            child_spouse.save()
            child_spouse_dict[form.cleaned_data.get("index")] = child_spouse

            
    # 孫
    for form in form_sets[2]:
        if form.cleaned_data.get("name"):
            grand_child = form.save(commit=False)
            grand_child.decedent = decedent
            if form.cleaned_data.get("target1") in child_dict:
                grand_child.content_type1 = ContentType.objects.get_for_model(Descendant)
                grand_child.object_id1 = child_dict[form.cleaned_data.get("target1")].id
            if form.cleaned_data.get("target2") in child_spouse_dict:
                grand_child.content_type2 = ContentType.objects.get_for_model(Spouse)
                grand_child.object_id2 = child_spouse_dict[form.cleaned_data.get("target2")].id
            grand_child.is_heir = form.cleaned_data.get("is_live") and form.cleaned_data.get("is_refuse") == False
            grand_child.created_by = user
            grand_child.updated_by = user
            grand_child.save()
            
    # 尊属
    ascendant_dict = {}
    for idx, form in enumerate(form_sets[3]):
        
        if form.cleaned_data.get("name"):
            ascendant = form.save(commit=False)
            ascendant.decedent = decedent
            ascendant.is_heir = form.cleaned_data.get("is_live") and form.cleaned_data.get("is_refuse") == False
            
            if idx < 2:
                ascendant.content_type = ContentType.objects.get_for_model(Decedent)
                ascendant.object_id = decedent.id
            else:
                target = form.cleaned_data.get("target")
                if target in ascendant_dict:
                    ascendant.content_type = ContentType.objects.get_for_model(Ascendant)
                    ascendant.object_id = ascendant_dict[target].id
            ascendant.created_by = user
            ascendant.updated_by = user
            ascendant.save()
            ascendant_dict[form.cleaned_data.get("index")] = ascendant
            
    # 兄弟姉妹共通
    if forms[3].cleaned_data.get("is_exist") is not None:
        collateral_common = forms[3].save(commit=False)
        collateral_common.decedent = decedent
        collateral_common.created_by = user
        collateral_common.updated_by = user
        collateral_common.save()
        
    # 兄弟姉妹
    for form in form_sets[4]:
        if form.cleaned_data.get("name"):
            collateral = form.save(commit=False)
            collateral.decedent = decedent
            if form.cleaned_data.get("target1") != "":
                collateral.content_type1 = ContentType.objects.get_for_model(Ascendant)
                collateral.object_id1 = ascendant_dict[form.cleaned_data.get("target1")].id
            if form.cleaned_data.get("target2") != "":
                collateral.content_type2 = ContentType.objects.get_for_model(Ascendant)
                collateral.object_id2 = ascendant_dict[form.cleaned_data.get("target2")].id
            collateral.is_heir = form.cleaned_data.get("is_live") and form.cleaned_data.get("is_refuse") ==  False
            collateral.created_by = user
            collateral.updated_by = user
            collateral.save()

# ステップ１
# 被相続人情報と相続人情報の入力
def step_one(request):
    if not request.user.is_authenticated:
        return redirect(to='/account/login/')
    
    function_name = get_current_function_name()
    user = User.objects.get(email = request.user)
    child_form_set = formset_factory(form=StepOneDescendantForm, extra=1, max_num=15)
    grand_child_form_set = formset_factory(form=StepOneDescendantForm, extra=1, max_num=15)
    ascendant_form_set = formset_factory(form=StepOneAscendantForm, extra=6, max_num=6)
    child_spouse_form_set = formset_factory(form=StepOneSpouseForm, extra=1, max_num=15)
    collateral_form_set = formset_factory(form=StepOneCollateralForm, extra=1, max_num=15)
    if request.method == "POST":
        forms = [
            StepOneDecedentForm(request.POST, prefix="decedent"),
            StepOneSpouseForm(request.POST, prefix="spouse"),
            StepOneDescendantCommonForm(request.POST, prefix="child_common"),
            StepOneCollateralCommonForm(request.POST, prefix="collateral_common"),
        ]
        form_sets = [
            child_form_set(request.POST, prefix="child"),
            child_spouse_form_set(request.POST or None, prefix="child_spouse"),
            grand_child_form_set(request.POST or None, prefix="grand_child"), 
            ascendant_form_set(request.POST or None, prefix="ascendant"),
            collateral_form_set(request.POST or None, prefix="collateral")
        ]

        # if not all(form.is_valid() for form in forms) or not all(form_set.is_valid() for form_set in form_sets):
        #     for form in forms:
        #         if not form.is_valid():
        #             print(f"Form {form} errors: {form.errors}")
        #     for form_set in form_sets:
        #         if not form_set.is_valid():
        #             print(f"Formset {form_set} errors: {form_set.errors}")
        #     return redirect('/toukiApp/step_one')
        if all(form.is_valid() for form in forms) and all(form_set.is_valid() for form_set in form_sets):
            try:
                with transaction.atomic():
                    save_step_one_datas(user, forms, form_sets)
            except DatabaseError as e:
                basic_log(function_name, e, user)
                messages.error(request, 'データベース処理でエラーが発生しました。\nお問い合わせからご連絡をお願いします。')
                return redirect('/toukiApp/step_one')
            except Exception as e:
                basic_log(function_name, e, user)
                messages.error(request, 'データの保存中にエラーが発生しました。\nお問い合わせからご連絡をお願いします。')
                return redirect('/toukiApp/step_one')
            else:
                return redirect('/toukiApp/step_two')
        else:
            for form in forms:
                if not form.is_valid():
                    basic_log(function_name, None, user, f"form {form} errors: {form.errors}")
            for form_set in form_sets:
                if not form_set.is_valid():
                    basic_log(function_name, None, user, f"formset {form_set} errors: {form_set.errors}")
            return redirect('/toukiApp/step_one')
    
    userDataScope = []
    spouse_data = {}
    childs_data = []
    child_heirs_data = []
    ascendant_data = []
    collateral_data = []
    progress = 1
    
    if user.decedent.first():
        decedent = user.decedent.first()
        progress = decedent.progress
        decedent_form = StepOneDecedentForm(prefix="decedent", instance=decedent)
        userDataScope.append("decedent")
        
        spouse_form = StepOneSpouseForm(prefix="spouse")
        spouse = Spouse.objects.filter(decedent=decedent, object_id=decedent.id).first()
        if spouse:
            spouse_data = model_to_dict(spouse)
            userDataScope.append("spouse")

            child_common = DescendantCommon.objects.filter(decedent=decedent).first()
            if child_common:
                child_common_form = StepOneDescendantCommonForm(prefix="child_common", instance=child_common)
                userDataScope.append("child_common")
                
                childs = Descendant.objects.filter(object_id1=decedent.id)
                if childs.exists():
                    childs_data = [
                        {
                            **{'id': child.id},
                            **{'count': Descendant.objects.filter(object_id1=child.id).count()},
                            **{'is_spouse': Spouse.objects.filter(decedent=decedent, object_id=child.id).count()},
                            **{f: model_to_dict(child).get(f) for f in StepOneDescendantForm().fields if f in model_to_dict(child)}
                        }
                        for child in childs
                    ]
                    userDataScope.append("child")
                    
                    child_spouses = Spouse.objects.filter(decedent=decedent).exclude(object_id=decedent.id)
                    if child_spouses.exists():
                        child_spouses_data = [
                            {
                                **{"child_id":child_spouse.object_id},
                                **{f: model_to_dict(child_spouse).get(f) for f in StepOneSpouseForm().fields if f in model_to_dict(child_spouse)}
                            }
                            for child_spouse in child_spouses
                        ]
                    else:
                        child_spouses_data = []
                        
                    grand_childs = Descendant.objects.filter(decedent=decedent).exclude(object_id1=decedent.id)
                    if grand_childs.exists():
                        grand_childs_data = [
                            {
                                **{"child_id":grand_child.object_id1},
                                **{f: model_to_dict(grand_child).get(f) for f in StepOneDescendantForm().fields if f in model_to_dict(grand_child)}
                            }
                            for grand_child in grand_childs
                        ]
                    else:
                        grand_childs_data = []
                        
                    if child_spouses_data or grand_childs_data:
                        userDataScope.append("child_heirs")
                        child_heirs_data = child_spouses_data + grand_childs_data
                        child_heirs_data.sort(key=lambda x: (x['child_id'], not (x in child_spouses_data)))

                ascendants = Ascendant.objects.filter(decedent=decedent)
                if ascendants.exists():
                    ascendant_data = [
                        {
                            **{'id': ascendant.id},
                            **{f: model_to_dict(ascendant).get(f) for f in StepOneAscendantForm().fields if f in model_to_dict(ascendant)}
                        }
                        for ascendant in ascendants
                    ]
                    ascendant_data = sorted(ascendant_data, key=lambda x: x['id'])
                    userDataScope.append("ascendant")

                collateral_common = CollateralCommon.objects.filter(decedent=decedent).first()
                if collateral_common:
                    collateral_common_form = StepOneCollateralCommonForm(prefix="collateral_common", instance=collateral_common)
                    userDataScope.append("collateral_common")
                    
                    collaterals = Collateral.objects.filter(decedent=decedent)
                    if collaterals.exists():
                        collateral_data = [
                            {
                                **{'id': collateral.id},
                                **{f: model_to_dict(collateral).get(f) for f in StepOneCollateralForm().fields if f in model_to_dict(collateral)}
                            }
                            for collateral in collaterals
                        ]
                        userDataScope.append("collateral")
                else:
                    collateral_common_form = StepOneCollateralCommonForm(prefix="collateral_common")
            else:
                child_common_form = StepOneDescendantCommonForm(prefix="child_common")
    else:
        decedent_form = StepOneDecedentForm(prefix="decedent")
        spouse_form = StepOneSpouseForm(prefix="spouse")
        child_common_form = StepOneDescendantCommonForm(prefix="child_common")
        collateral_common_form = StepOneCollateralCommonForm(prefix="collateral_common") 
    
    decedent_form_internal_field_name = ["user", "progress"]
    spouse_form_internal_field_name = ["decedent", "content_type", "object_id", "is_heir"]
    common_form_internal_field_name = ["decedent"]
    child_form_internal_field_name = ["decedent", "content_type1", "object_id1", "content_type2", "object_id2", "is_heir"]
    ascendant_form_internal_field_name = ["decedent", "content_type", "object_id", "is_heir"]
    ascendants_relation = ["父", "母", "父方の祖父", "父方の祖母", "母方の祖父", "母方の祖母"]
    collateral_form_internal_field_name = ["decedent", "content_type1", "object_id1", "content_type2", "object_id2", "is_heir"]
    
    context = {
        "title" : "１．" + Sections.STEP1,
        "user" : user,
        "progress": progress,
        "decedent_form": decedent_form,
        "decedent_form_internal_field_name": decedent_form_internal_field_name,
        "spouse_form": spouse_form,
        "spouse_form_internal_field_name": spouse_form_internal_field_name,
        "child_common_form" : child_common_form,
        "collateral_common_form" : collateral_common_form,
        "common_form_internal_field_name" : common_form_internal_field_name,
        "sections" : Sections.SECTIONS[Sections.STEP1],
        "service_content" : Sections.SERVICE_CONTENT,
        "child_form_set" : child_form_set(prefix="child"),
        "child_spouse_form_set" : child_spouse_form_set(prefix="child_spouse"),
        "grand_child_form_set" : grand_child_form_set(prefix="grand_child"),
        "ascendant_form_set" : ascendant_form_set(prefix="ascendant"),
        "child_form_internal_field_name" : child_form_internal_field_name,
        "ascendant_form_internal_field_name": ascendant_form_internal_field_name,
        "ascendants_relation" : ascendants_relation,
        "collateral_form_set" : collateral_form_set(prefix="collateral"),
        "collateral_form_internal_field_name" : collateral_form_internal_field_name,
        "userDataScope" : json.dumps(userDataScope),
        "spouse_data" : json.dumps(spouse_data),
        "childs_data" : json.dumps(childs_data),
        "child_heirs_data" : json.dumps(child_heirs_data),
        "ascendant_data" : json.dumps(ascendant_data),
        "collateral_data" : json.dumps(collateral_data),
    }
    
    return render(request, "toukiApp/step_one.html", context)

# 死亡している相続人候補を取得する
def get_deceased_persons(decedent):
    deceased_persons = []
    
    spouse = Spouse.objects.filter(decedent=decedent).first()
    if spouse and spouse.is_live is False:
        deceased_persons.append(spouse)
    
    childs = Descendant.objects.filter(object_id1=decedent.id)
    if childs.exists() and any(child for child in childs if child.is_live is False):
        deceased_persons += [child for child in childs if child.is_live is False]
        child_spouses = [spouse for spouse in Spouse.objects.filter(decedent=decedent)[1:] if spouse.is_live is False]
        grand_childs = [descendant for descendant in Descendant.objects.filter(decedent=decedent).exclude(object_id1=decedent.id) if descendant.is_live is False]
        child_heirs = child_spouses + grand_childs

        if child_heirs:
            # object_idまたはobject_id1を取得する関数
            def get_id(obj):
                return obj.object_id if isinstance(obj, Spouse) else obj.object_id1

            # 同じIDがある場合に、child_spousesの要素が先に来るようにする関数
            def compare(obj):
                return (get_id(obj), isinstance(obj, Descendant))

            # 比較関数に基づいてソート
            child_heirs = sorted(child_heirs, key=compare)
            deceased_persons += [child_heir for child_heir in child_heirs]
            
    ascendants = Ascendant.objects.filter(decedent=decedent)
    if ascendants.exists():
        deceased_persons += [ascendant for ascendant in ascendants if ascendant.is_live is False]
        
    collaterals = Collateral.objects.filter(decedent=decedent)
    if collaterals.exists():
        deceased_persons += [collateral for collateral in collaterals if collateral.is_live is False]
    
    return deceased_persons

def get_heirs(decedent):
    heirs = []
    
    spouse = Spouse.objects.filter(decedent=decedent).first()
    if spouse and spouse.is_heir:
        heirs.append(spouse)
    
    childs = Descendant.objects.filter(object_id1=decedent.id)
    if childs.exists() and any(child for child in childs if child.is_heir):
        heirs += [child for child in childs if child.is_heir]
    
    if childs.exists() and any(child for child in childs if child.is_live is False):
        child_spouses = [spouse for spouse in Spouse.objects.filter(decedent=decedent).exclude(object_id=decedent.id) if spouse.is_heir]
        grand_childs = [descendant for descendant in Descendant.objects.filter(decedent=decedent).exclude(object_id1=decedent.id) if descendant.is_heir]
        child_heirs = child_spouses + grand_childs

        if child_heirs:
            # object_idまたはobject_id1を取得する関数
            def get_id(obj):
                return obj.object_id if isinstance(obj, Spouse) else obj.object_id1

            # 同じIDがある場合に、child_spousesの要素が先に来るようにする関数
            def compare(obj):
                return (get_id(obj), isinstance(obj, Descendant))

            # 比較関数に基づいてソート
            child_heirs = sorted(child_heirs, key=compare)
            heirs += [child_heir for child_heir in child_heirs]
            
    ascendants = Ascendant.objects.filter(decedent=decedent)
    if ascendants.exists():
        heirs += [ascendant for ascendant in ascendants if ascendant.is_heir]
        
    collaterals = Collateral.objects.filter(decedent=decedent)
    if collaterals.exists():
        heirs += [collateral for collateral in collaterals if collateral.is_heir]
    
    return heirs

def get_prefecture_name(prefecture_code):
    for code, name in PREFECTURES:
        if code == prefecture_code:
            return name
    return '該当の都道府県番号がありません'  # キーが見つからない場合のデフォルト値

#ステップ２のデータを登録する
def save_step_two_datas(request):
    pass

# GoogleドライブのダウンロードリンクからファイルIDを抽出
def extract_file_id_from_url(url):
    query = urlparse(url).query
    params = parse_qs(query)
    return params['id'][0]

#ステップ２
#必要書類リスト
def step_two(request):
    if not request.user.is_authenticated:
        return redirect(to='/account/login/')

    function_name = get_current_function_name()
    
    user = User.objects.get(email = request.user)
    decedent = user.decedent.first()
    registry_files = Register.objects.filter(decedent=decedent)
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                decedent.progress = 3
                decedent.save()

                # if os.getenv('DJANGO_SETTINGS_MODULE') == 'toukiAi.settings.development':
                    
                # サービスアカウントの認証情報ファイルのパス
                SERVICE_ACCOUNT_FILE = 'toukiai-development-7bf1692a5215.json'
                
                # サービスアカウント認証情報をロード
                credentials = service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE,
                    scopes=['https://www.googleapis.com/auth/drive'])
                
                # GoogleAuth オブジェクトの初期化
                gauth = GoogleAuth()
                gauth.credentials = credentials
                service = build('drive', 'v3', credentials=credentials)
                    
                #不動産登記簿は常に全削除と全登録を行う
                if registry_files.exists():
                    for file in registry_files:
                        # Googleドライブからファイルを削除
                        file_id = extract_file_id_from_url(file.path)
                        service.files().delete(fileId=file_id).execute()
                    registry_files.delete()
                    
                for i in range(len(request.FILES)):
                    pdf = request.FILES['pdf' + str(i)]
                    if not pdf:
                        continue
                    relative_path = default_storage.save(os.path.join('tmp/', pdf.name), pdf)
                    absolute_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                    # ファイルのメタデータ
                    file_metadata = {
                        'name': pdf.name,
                        'parents': ['1iEOCvgmg8tzYyWMV_LFGvbVsJK8_wxRl']  # 親フォルダのID
                    }
                    # ファイルのアップロードを実行
                    media = MediaFileUpload(absolute_path, mimetype='application/pdf')
                    file_drive = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                    # ファイルのアクセス権限を設定
                    service.permissions().create(
                                fileId=file_drive['id'],
                                body={'type': 'anyone', 'role': 'reader'},
                                fields='id'
                            ).execute()
                    # 新しいRegisterオブジェクトを作成し、属性に値を設定
                    register = Register(
                        decedent=decedent,
                        title=pdf.name,
                        path=f'https://drive.google.com/uc?export=download&id={file_drive["id"]}',  # Gドライブ上のファイルへのダウンロードリンク
                        file_size=os.path.getsize(absolute_path),
                        extension=os.path.splitext(pdf.name)[1][1:],  # 拡張子を取得
                        created_by=user,
                        updated_by=user
                    )
                    register.save()  # データベースに保存
        except googleapiclient.errors.HttpError as e:
            basic_log(function_name, e, user, "googleapiclientエラー")
            messages.error(request, 'データの保存中にエラーが発生しました。')
            return JsonResponse({'status': 'error'})
        except Exception as e:
            basic_log(function_name, e, user)
            messages.error(request, 'データの保存中にエラーが発生しました。')
            return JsonResponse({'status': 'error'})
        else:
            return JsonResponse({'status': 'success'})
    
    # 不動産登記簿があるとき
    file_server_file_name_and_file_path = []
    if registry_files.exists():
        for file in registry_files:
            # ファイルの保存先のパスを追加
            file_server_file_name_and_file_path.append({"name": file.title, "path": file.path})
            
    app_server_file_name_and_file_path = []
    for file_name_and_file_path in file_server_file_name_and_file_path:
        # ダウンロード先のパス
        output = os.path.join(settings.MEDIA_ROOT, 'download_tmp', file_name_and_file_path["name"])

        # ファイルをダウンロード
        gdown.download(file_name_and_file_path["path"], output, quiet=True)

        # ダウンロードしたファイルの名前とパスを配列に追加
        app_server_file_name_and_file_path.append({"name": file_name_and_file_path["name"], "path": settings.MEDIA_URL + 'download_tmp/' + file_name_and_file_path["name"]})

    # 配列をJSON形式に変換
    app_server_file_name_and_file_path = json.dumps(app_server_file_name_and_file_path)
    
    progress = decedent.progress
    deceased_persons = get_deceased_persons(decedent)
    heirs = get_heirs(decedent)
    minors = [heir for heir in heirs if hasattr(heir, 'is_adult') and heir.is_adult is False]
    overseas = [heir for heir in heirs if hasattr(heir, 'is_japan') and heir.is_japan is False]
    family_registry_search_word = "戸籍 郵送請求"
    family_registry_query = f"{decedent.domicile_prefecture}{decedent.domicile_city} {family_registry_search_word}"
    response = requests.get(f"https://www.googleapis.com/customsearch/v1?key=AIzaSyAmeV3HS-AshtCAHWit7eAEEudyEkwtnxE&cx=9242f933284cb4535&q={family_registry_query}")
    data = response.json()
    top_link = data["items"][0]["link"]
    context = {
        "title" : "２．必要書類一覧",
        "user" : user,
        "progress": progress,
        "prefectures": PREFECTURES,
        "decedent": decedent,
        "app_server_file_name_and_file_path": app_server_file_name_and_file_path,
        "file_server_file_name_and_file_path": file_server_file_name_and_file_path,
        "top_link": top_link,
        "deceased_persons": deceased_persons,
        "heirs": heirs,
        "minors": minors,
        "overseas": overseas,
        "sections" : Sections.SECTIONS[Sections.STEP2],
        "service_content" : Sections.SERVICE_CONTENT,
    }
    return render(request, "toukiApp/step_two.html", context)

"""

    ステップ３関連

"""

def check_type_of_division_conditions(data):
    """登録されている遺産分割方法のデータが入力完了しているものか判別する
    
    Args:
        data (TypeOfDivision): 遺産分割方法のデータ

    Returns:
        bool: 入力完了であればtrue、未完了はfalse
    """
    # data.property_allocationの値が存在するかどうか
    condition1 = bool(data.property_allocation)
    
    # data.content_type1 と data.object_id1 の両方の値が存在するかどうか
    condition2 = bool(data.content_type1) and bool(data.object_id1)
    
    # data.cash_allocationの値が存在するかどうか
    condition3 = bool(data.cash_allocation)
    
    # data.content_type2 と data.object_id2 の両方の値が存在するかどうか
    condition4 = bool(data.content_type2) and bool(data.object_id2)
    
    # data.type_of_divisionが存在するかどうか
    condition5 = bool(data.type_of_division)

    # 組み合わせた条件
    # data.property_allocationが存在する または data.content_type1 と data.object_id1 の両方が存在する
    combined_condition1 = condition1 or condition2

    # data.cash_allocationが存在する または data.content_type2 と data.object_id2 の両方が存在する
    combined_condition2 = condition3 or condition4

    # 最終的な条件：上記の条件とdata.type_of_divisionが存在する
    final_condition = combined_condition1 and combined_condition2 and condition5

    return final_condition

def check_heirs_conditions(data):
    #ループ処理できるようにdataを配列形式に変える
    if not isinstance(data, list):
        data = [data]
    flg = True
    for d in data:
        attr = [
            d.name,
            d.birth_year, d.birth_month, d.birth_date
        ]
        #卑属又は兄弟姉妹のとき前配偶者又は異父母データを追加する
        if d.__class__ in [Descendant, Collateral]:
            attr.append(d.object_id2)
        #死亡して相続放棄してない又は空欄とき、死亡年月日を追加
        if d.is_live is False and not d.is_refuse:
            attr.extend([d.death_year, d.death_month, d.death_date])
        #不動産を取得するとき、都道府県、市区町村、町域・番地を追加
        if d.is_acquire is True:
            attr.extend([d.prefecture, d.city, d.address])
        #全項目をチェック
        if not all(attr):
            flg = False
            break
    return flg    

def step_three_input_status(data):
    """登録されているステップ３のデータをチェックしてどこまで入力が完了しているか判別する
    
    Args:
        data (Model): ステップ３で使用するデータ

    Returns:
        bool: 入力完了はtrue、未完了はfalse
    """
    function_name = get_current_function_name()
    try:
        #被相続人データのとき
        if data.__class__ == Decedent:
            #チェック対象の属性リスト
            attr = [
                data.name,
                data.death_year, data.death_month, data.death_date, 
                data.birth_year, data.birth_month, data.birth_date, 
                data.prefecture, data.city, data.address, 
                data.domicile_prefecture, data.domicile_city, data.domicile_address
            ]
            #チェック対象が全て値を持つときTrueを返す
            return all(attr)
        elif data.__class__ == RegistryNameAndAddress:
            return all([all([d.name, d.prefecture, d.city, d.address]) for d in data])
        elif data.__class__ in [Spouse, Ascendant, Descendant, Collateral]:
            return check_heirs_conditions(data)
        elif data.__class__ == TypeOfDivision:
            return check_type_of_division_conditions(data)
        elif data.__class__ == NumberOfProperties:
            attr = [data.land, data.house, data.bldg]
            return any(x > 0 for x in attr)
        elif data.__class__ in [Land, House, Bldg]:
            attr = [data.number, data.address, data.purparty, data.price, data.is_exchange, data.office]
            return all(attr)
        elif data.__class__ == Site:
            attr = [data.bldg, data.number, data.address_and_land_number, data.type, 
                    data.purparty_bottom, data.purparty_top, data.price,]
            return all(attr)
        elif data.__class__ in [PropertyAcquirer, CashAcquirer]:
            attr = [data.content_type1, data.object_id1, data.content_object1, 
                    data.content_type2, data.object_id2, data.content_object2,
                    data.percentage]
            return all(attr)
        elif data.__class__ == Application:
            if data.is_agent is not None:
                attr = []
                if data.is_agent == True:
                    attr = [data.content_type, data.object_id,
                            data.agent_name, data.agent_address, data.agent_phone_number,
                            data.is_return, data.is_mail]
                else:
                    attr = [data.content_type, data.object_id, data.phone_number,
                            data.is_return, data.is_mail]
                return all(attr)        
                
        return False
    except Exception as e:
        basic_log(function_name, e, None)
        raise e
        
def get_registry_name_and_address_initial_data(data):
    """登記簿上の氏名住所の初期データ生成処理。

    Args:
        data (RegistryNameAndAddress): データセットまたはモデルのインスタンス。

    Returns:
        list of dict: 初期データのリスト。
    """
    initial_data = []
    for d in data:
        data_dict = {
            "id": d.id,
            "name": d.name,
            "prefecture": d.prefecture,
            "city": d.city,
            "address": d.address,
            "bldg": d.bldg,
            "decedent": d.decedent,
        }
        
        initial_data.append(data_dict)

    return initial_data

def get_spouse_or_ascendant_initial_data(data):
    """配偶者又は直系尊属の初期データ生成処理。

    Args:
        data (Spouse or Ascendant): データセットまたはモデルのインスタンス。

    Returns:
        list of dict: 初期データのリスト。
    """
    initial_data = []
    for d in data:
        data_dict = {
            "id": d.id,
            "decedent": d.decedent,
            "name": d.name,
            "death_year": getattr(d, 'death_year', None),
            "death_month": getattr(d, 'death_month', None),
            "death_date": getattr(d, 'death_date', None),
            "birth_year": getattr(d, 'birth_year', None),
            "birth_month": getattr(d, 'birth_month', None),
            "birth_date": getattr(d, 'birth_date', None),
            "is_acquire": getattr(d, 'is_acquire', None),
            "prefecture": getattr(d, 'prefecture', None),
            "city": getattr(d, 'city', None),
            "address": getattr(d, 'address', None),
            "bldg": getattr(d, 'bldg', None),
            "is_live": getattr(d, 'is_live', None),
            "is_heir": getattr(d, 'is_heir', None),
            "is_refuse": getattr(d, 'is_refuse', None),
            "is_exist": getattr(d, 'is_exist', None),
            "is_japan": getattr(d, 'is_japan', None),
            "content_type": getattr(d, 'content_type', None),
            "object_id": getattr(d, 'object_id', None),       
        }
        if hasattr(d, 'id') and hasattr(d, 'content_type'):
            data_dict["id_and_content_type"] = f"{d.id}_{ContentType.objects.get_for_model(d).id}"
        
        initial_data.append(data_dict)

    return initial_data

def get_descendant_or_collateral_initial_data(data, content_type_model):
    """_summary_
    初期表示する直系卑属又は傍系データを返す

    Args:
        data (Descendant or Collateral): 直系卑属又は傍系のデータ

    Returns:
        dict: 辞書型に格納したデータ
    """
    content_type = ContentType.objects.get_for_model(content_type_model)
    related_individual_content_type = ContentType.objects.get_for_model(RelatedIndividual)

    initial_data = []
    for d in data:
        other_parent_name = None
        if d.content_type2 == related_individual_content_type:
            related_individual = RelatedIndividual.objects.filter(
                id=d.object_id2,
                object_id=d.id,
                content_type=content_type
            ).first()
            other_parent_name = related_individual.name if related_individual else None

        # 辞書データを生成
        data_dict = {
            "id": d.id,
            "decedent": d.decedent,
            "name": d.name,
            "death_year": d.death_year,
            "death_month": d.death_month,
            "death_date": d.death_date,
            "birth_year": d.birth_year,
            "birth_month": d.birth_month,
            "birth_date": d.birth_date,
            "is_acquire": d.is_acquire,
            "prefecture": d.prefecture,
            "city": d.city,
            "address": d.address,
            "bldg": d.bldg,
            "content_type1": d.content_type1,
            "object_id1": d.object_id1,
            "content_type2": d.content_type2,
            "object_id2": d.object_id2,
            "other_parent_name": other_parent_name,
            "is_live": d.is_live,
            "is_heir": d.is_heir,
            "is_refuse": d.is_refuse,
            "is_exist": d.is_exist,
            "is_japan": d.is_japan,
            "is_adult": d.is_adult,
            "id_and_content_type": f"{d.id}_{content_type.id}",
        }

        initial_data.append(data_dict)

    return initial_data     

def get_property_initial_data(data):
    """不動産の初期データ生成処理。

    Args:
        data (Land or House or Bldg or Site): データセットまたはモデルのインスタンス。

    Returns:
        list of dict: 初期データのリスト。
    """
    initial_data = []
    for d in data:
        data_dict = {
            "land_id": d.id,
            "house_id": d.id,
            "bldg_id": d.id,
            "decedent": d.decedent,
            "bldg": getattr(d, "bldg", None),
            "register": getattr(d, "register", None),
            "number": d.number,
            "address": getattr(d, "address", None),
            "address_and_land_number": getattr(d, "address_and_land_number", None),
            "land_number": getattr(d, "land_number", None),
            "house_number": getattr(d, "house_number", None),
            "bldg_number": getattr(d, "bldg_number", None),
            "type": getattr(d, "type", None),
            "purparty": getattr(d, "purparty", None),
            "purparty_bottom": getattr(d, "purparty_bottom", None),
            "purparty_top": getattr(d, "purparty_top", None),
            "office": getattr(d, "office", None),
            "price": d.price,
            "is_exchange": getattr(d, "is_exchange", None),
        }
        
        initial_data.append(data_dict)

    return initial_data

def get_acquirer_initial_data(data):
    """取得者の初期データ生成処理。

    Args:
        data (PropertyAcquirer or CashAcquirer): データセットまたはモデルのインスタンス。

    Returns:
        list of dict: 初期データのリスト。
    """
    initial_data = []
    for d in data:
        data_dict = {
            "id": d.id,
            "decedent": d.decedent,
            "content_type1": d.content_type1,
            "object_id1": d.object_id1,
            "content_type2": d.content_type2,
            "object_id2": d.object_id2,
            "percentage": d.percentage,
        }
        
        initial_data.append(data_dict)

    return initial_data

def add_required_for_data(instance, user, decedent):
    """データに必須の項目を追加する
    ・更新者は常に必須
    ・被相続人と作成者は新規登録のときに必須

    Args:
        instance (_type_): モデルに登録するインスタンス
        user (_type_): _description_
        decedent (_type_): _description_
    """
    instance.updated_by = user
    if not instance.id:
        instance.decedent = decedent
        instance.created_by = user
def form_and_data_not_match_http_response():
    return HttpResponse("入力内容と登録データに齟齬があります。\n解決方法をご案内いたしますので、お手数ですがお問い合わせをお願いします", status=400)
    
def save_step_three_registry_name_and_address(decedent, user, form_set):
    """登記簿上の氏名住所のデータ操作
    
    被相続人に紐づくデータを全削除してすべて新規登録にする
    
    Args:
        user (_type_): _description_
        form_set (_type_): _description_
    """
    if is_form_set(form_set):
        function_name = get_current_function_name()
        form_class_name = get_form_set_class_name(form_set)
        try:
            RegistryNameAndAddress.objects.filter(decedent=decedent).delete()
            for form in form_set:
                instance = form.save(commit=False)
                add_required_for_data(instance, user, decedent)
                instance.save()
        except DatabaseError as e:
            basic_log(function_name, e, user, form_class_name)
            raise e
        except Exception as e:
            basic_log(function_name, e, user, form_class_name)
            raise e
    else:
        basic_log(get_current_function_name(), e, user, "フォームが存在しません")
        raise ValidationError("登記簿上の氏名住所のフォームが存在しません")

def update_form_set_validation(data, form_set, user):
    """フォームセットを更新する際のバリデーション
    
    ・データが１つ以上ある
    ・データ数とフォームセットの数が一致する
    ・データとフォームセットのidが一致する

    Args:
        data (_type_): _description_
        form_set (_type_): _description_
        user (_type_): _description_
        form_class_name (_type_): _description_
        update_target_ids (_type_): _description_
        data_keys (_type_): _description_

    Returns:
        _type_: _description_
    """
    if is_data(data) == False:
        return False
    function_name = get_current_function_name()
    form_class_name = get_form_set_class_name(form_set)
    update_target_ids = [form.cleaned_data.get("id") for form in form_set if form.cleaned_data.get('id')]
    data_dict = {d.id: d for d in data}
    data_keys = data_dict.keys()
    if not is_form_set_count_equal_to_data_count(form_set, data):
        basic_log(function_name, None, user, f"{form_class_name}のフォームセットの数とデータの数が一致しません")
        raise ValidationError("データとフォームの数が一致ません")
        
    if not is_all_id_match(update_target_ids, data_keys, user, form_class_name):
        basic_log(function_name, None, user, f"{form_class_name}のフォームセットのidとデータのidが一致しません")
        raise ValidationError(id_not_match_message("データ", "フォーム"))

def update_form_set(data, form_set, user, decedent, content_type = None, relationship = None):
    """フォームセットの更新処理

    バリデーション後に更新処理を行う
    
    Args:
        data (_type_): _description_
        form_set (_type_): _description_
        user (_type_): _description_
        decedent (_type_): _description_
        content_type (_type_, optional): _description_. Defaults to None.
        relationship (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    try:
        function_name = get_current_function_name()
        if update_form_set_validation(data, form_set, user) == False:
            return
        
        form_class_name = get_form_set_class_name(form_set)
        if form_class_name in ["StepThreeDescendantForm", "StepThreeCollateralForm"]:
            save_step_three_descendant_or_collateral(decedent, user, data, form_set, content_type, relationship)
        elif form_class_name in ["StepThreeSpouseForm", "StepThreeAscendantForm"]:
            save_step_three_child_spouse_or_ascendant(user, form_set, data)
        else:
            basic_log(get_current_function_name(), None, user, form_class_name)
            raise ValidationError("想定しない形式のフォームが使用されてます")
    except (DatabaseError, ValidationError) as e:
        basic_log(function_name, e, user)
        raise e
    except Exception as e:
        basic_log(function_name, e, user)
        raise e

def is_all_id_match(target_ids, data_ids, user, form_class_name):
    """フォームセットのidとデータのidを比較する

    Args:
        target_ids (_type_): _description_
        data_ids (_type_): _description_
        user (_type_): _description_
        form_class_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    #idを比較してフォームセットから送られたデータが全て更新対象のものか確認する
    target_ids_set = set(int(id_str) for id_str in target_ids if id_str.isdigit())
    # data_dict のキーからセットを作成
    data_ids_set = set(data_ids)
    # 両方のセットが完全に一致するか確認
    if target_ids_set != data_ids_set:
        missing_in_target_ids = data_ids_set - target_ids_set
        missing_in_data_ids = target_ids_set - data_ids_set
        message = f"{form_class_name}のid比較時にエラー発生\n\
            フォームセットに含まれていないID：{missing_in_target_ids}\n\
            データに含まれていないID：{missing_in_data_ids}"
        basic_log(get_current_function_name(), None, user, message)
        raise ValidationError(id_not_match_message("データ", "フォーム"))

    return True
    
def save_step_three_child_spouse_or_ascendant(user, form_set, data):
    """ステップ３の子の配偶者又は尊属の更新処理

    Args:
        user (_type_): _description_
        form_set (_type_): _description_
        data (_type_): _description_
    """
    try:
        function_name = get_current_function_name()
        form_class_name = get_form_set_class_name(form_set)  # formのクラス名を取得
        data_dict = {d.id: d for d in data}
        update_fields = get_update_fields_for_form_set(data)
        for form in form_set:
            form_data = form.cleaned_data
            update_target_data = data_dict.get(int(form_data.get("id")))
            form_data['updated_by'] = user
            for key, value in form_data.items():
                if key in update_fields:
                    setattr(update_target_data, key, value)
                update_target_data.save()
    except DatabaseError as e:
        basic_log(function_name, e, user, form_class_name)
        raise e
    except Exception as e:
        basic_log(function_name, e, user, form_class_name)
        raise e
    
def get_update_fields_for_form_set(data):
    """フォームセットの更新処理をする際の更新対象のフィールドを取得する
    
    モデルのクラス名に応じて更新から除外するフィールドを判別して更新対象のフィールドを確定する

    Args:
        data (_type_): _description_

    Raises:
        ValidationError: _description_

    Returns:
        _type_: _description_
    """
    d = data[0]
    model_name = d._meta.model_name
    model_fields = model_to_dict(d).keys()
    exclude_fields = []
    
    if model_name in "descendant" or "collateral":
        exclude_fields = ['is_heir', "is_exist", "is_live", 'created_at', 'created_by']
    elif model_name in "spouse" or "ascendant":
        exclude_fields = ['is_heir', "is_exist", "is_live", 'created_at', 'created_by']
    else:
        basic_log(get_current_function_name(), None, None, "想定しないデータが渡されました")
        raise ValidationError("想定しない形式のデータが参照されました")
    
    return [field for field in model_fields if field not in exclude_fields]

def save_step_three_descendant_or_collateral(decedent, user, data, form_set, content_type, relationship):
    """ステップ３の卑属又は傍系のデータ更新処理

    Args:
        decedent (_type_): _description_
        user (_type_): _description_
        form_set (_type_): _description_
        content_type (_type_): _description_
        relationship (_type_): _description_
        data (_type_): _description_

    Raises:
        ValueError: _description_
    """
    function_name = get_current_function_name()
    try:
        form_class_name = get_form_set_class_name(form_set)  # formのクラス名を取得
        data_dict = {d.id: d for d in data}
        related_indivisual_content_type = ContentType.objects.get_for_model(RelatedIndividual)
        update_fields = get_update_fields_for_form_set(data)
        for form in form_set:
            form_data = form.cleaned_data
            #関係者の登録（関係者は削除と新規のため、子のcontent_type2object_id2は常に更新する必要あり）
            if form_data.get("other_parent_name") != "":
                related_indivisual = RelatedIndividual(
                    decedent = decedent,
                    content_type = content_type,
                    object_id = form_data.get("id"),
                    name = form_data.get("other_parent_name"),
                    relationship = relationship,
                    created_by = user,
                    updated_by = user,
                )
                related_indivisual.save()
                form_data["content_type2"] = related_indivisual_content_type
                form_data["object_id2"] = related_indivisual.id
            update_target_data = data_dict.get(int(form_data.get("id")))
            form_data['updated_by'] = user
            for key, value in form_data.items():
                if key in update_fields:
                    setattr(update_target_data, key, value)
                update_target_data.save()
    except DatabaseError as e:
        basic_log(function_name, e, user, form_class_name)
        raise e
    except Exception as e:
        basic_log(function_name, e, user, form_class_name)
        raise e

def save_step_three_step_property(decedent, user, form_set):
    """土地、建物、区分建物のデータ新規登録処理

    Args:
        decedent (_type_): _description_
        user (_type_): _description_
        form_set (_type_): _description_

    Returns:
        _type_: 不動産のフォームのindexとinstance（取得者、敷地権の登録処理で使用するため）
    """
    try:
        form_class_name = get_form_set_class_name(form_set)
        function_name = get_current_function_name()
        index_and_instance = []
        for form in form_set:
            instance = form.save(commit=False)
            add_required_for_data(instance, user, decedent)
            instance.save()
            index_and_instance.append((form.cleaned_data.get("index"), instance))
        return index_and_instance
    except DatabaseError as e:
        basic_log(function_name, e, user, form_class_name)
        raise e
    except Exception as e:
        basic_log(function_name, e, user, form_class_name)
        raise e   

def save_step_three_acquirer(decedent, user, form_set, property_content_type, index_and_properties):
    """不動産取得者、金銭取得者の新規登録処理

    ・金銭取得者の場合は、targetがNoneのフォームをスキップする
    Args:
        decedent (_type_): _description_
        user (_type_): _description_
        form_set (_type_): _description_
        property_content_type (_type_): _description_
        index_and_properties (_type_): _description_

    Raises:
        ValidationError: _description_
    """
    function_name = get_current_function_name()
    form_class_name = get_form_set_class_name(form_set)
    try:
        for form in form_set:
            instance = form.save(commit=False)
            add_required_for_data(instance, user, decedent)
            instance.content_type1 = property_content_type
            matched = False
            target_val = form.cleaned_data.get("target")
            
            cash_acquirer_forms = ["StepThreeLandCashAcquirerForm", "StepThreeHouseCashAcquirerForm", "StepThreeBldgCashAcquirerForm"]
            content_type_val = form.cleaned_data.get("content_type2")
            if form_class_name in cash_acquirer_forms and not content_type_val:
                continue
            
            for idx, property in index_and_properties:
                if target_val == idx:
                    matched = True
                    instance.object_id1 = property.id
                    instance.save()
                    break
            if not matched:
                basic_log(
                    function_name,
                    None,
                    user,
                    f"content_type：{property_content_type}\n\
                        フォームクラス：{form_class_name}\n\
                        target：{target_val}に一致する不動産のindexがありません")
                raise ValidationError("取得者と不動産の関連付けに失敗しました")
    except DatabaseError as e:
        basic_log(function_name, e, user, form_class_name)
        raise e
    except Exception as e:
        basic_log(function_name, e, user, form_class_name)
        raise e     

def save_step_three_site(decedent, user, form_set, index_and_instance):
    """ステップ３の敷地権のデータ登録処理

    Args:
        decedent (_type_): _description_
        user (_type_): _description_
        form_set (_type_): _description_
        index_and_instance (_type_): _description_

    Raises:
        ValidationError: _description_
    """
    function_name = get_current_function_name()
    form_class_name = get_form_set_class_name(form_set)
    try:
        for i, form in enumerate(form_set):
            site = form.save(commit=False)
            add_required_for_data(site, user, decedent)
            matched = False
            target_val = form.cleaned_data.get("target")
            for idx, property in index_and_instance:
                if target_val == idx:
                    matched = True
                    site.bldg = property
                    site.save()
                    break
            if not matched:
                raise ValidationError(f"form_num:{i + 1}\ntarget：{target_val}に一致する不動産のindexがありません")
    except DatabaseError as e:
        basic_log(function_name, e, user, form_class_name)
        raise e
    except Exception as e:
        basic_log(function_name, e, user, form_class_name)
        raise e

def save_step_three_form(decedent, user, form):
    """ステップ３のモデルフォームのデータ保存処理

    フォームセットは対象外
    Args:
        decedent (_type_): _description_
        user (_type_): _description_
        form (_type_): _description_
    """
    try:
        form_class_name = form.__class__.__name__
        instance = form.save(commit=False)
        add_required_for_data(instance, user, decedent)
        instance.save()
    except DatabaseError as e:
        basic_log(get_current_function_name(), e, user, form_class_name)
        raise e
    except Exception as e:
        basic_log(get_current_function_name(), e, user, form_class_name)
        raise e

def get_form_set_class_name(form_set):
    if (len(form_set.forms) > 0):
        return form_set.forms[0].__class__.__name__
    else:
        raise ValidationError("フォームセットにフォームがありません")

def is_data(data):
    if isinstance(data, (list, tuple, QuerySet)):
        return bool(data)
    else:
        return data is not None

def is_form_set(form_set):
    return form_set.management_form.cleaned_data["TOTAL_FORMS"] > 0

def is_form_set_count_equal_to_data_count(form_set, data):
    return form_set.management_form.cleaned_data["TOTAL_FORMS"] == len(data)

def is_any_exchange_property(form_set):
    return any(form.cleaned_data.get('is_exchange') for form in form_set)

def get_current_function_name():
    """
    現在実行中の関数の名前を取得して返すヘルパー関数。
    """
    return inspect.currentframe().f_back.f_code.co_name

def id_not_match_message(str1 = None, str2 = None):
    """idが一致しないときのメッセージを返します
    
    str1とstr2のidが一致しない場合、それらのidを含んだエラーメッセージを返します。
    どちらかまたは両方の引数がNoneの場合は、一般的なエラーメッセージを返します。
    
    Args:
        str1 (str, optional): 比較するオブジェクト１. Defaults to None.
        str2 (str, optional): 比較するオブジェクト２. Defaults to None.

    Returns:
        str: エラーメッセージ
    """
    if(str1 and str2):
        return (f"{str1}と{str2}のidが一致しません")
    else:
        return ("idが一致しません")

def save_step_three_spouse_data(data, form, decedent, user):
    if is_data(data):
        save_step_three_form(decedent, user, form)
    else:
        basic_log(get_current_function_name(), None, user, "配偶者データがないにもかかわらず配偶者フォームがPOSTに含まれてます")
        raise ValidationError("配偶者データがありません")

def basic_log(function_name, e, user, message = None):
    """基本的なログ情報

    Args:
        function_name (str): 関数名
        e (_type_): エラークラスから生成されたオブジェクト
        user (User): 対象のユーザー
        message (str, optional): 特記事項. Defaults to None.
    """
    traceback_info = traceback.format_exc()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = user.id if user else ""
    logger.error(f"エラー発生箇所:{function_name}\n\
        開発者メッセージ:{message}\n\
        詳細：{e}\n\
        user_id:{user_id}\n\
        発生時刻：{current_time}\n\
        経路:{traceback_info}"
    )

def save_step_three_decedent_data(form, user):
    try:
        instance = form.save(commit=False)
        instance.progress = 4
        add_required_for_data(instance, user, instance)
        instance.save()
        return instance
    except Exception as e:
        basic_log(get_current_function_name(), e, user)
        raise e

def get_forms_idx_for_step_three():
    return {
        "decedent": 0,
        "spouse": 1,
        "type_of_division": 2,
        "number_of_properties": 3,
        "application": 4,
    }

def del_data_for_step_three(decedent):
    """ステップ３で削除と新規登録するモデルのデータ削除処理

    Args:
        decedent (_type_): _description_
    """
    RelatedIndividual.objects.filter(decedent=decedent).delete()
    Land.objects.filter(decedent=decedent).delete()
    House.objects.filter(decedent=decedent).delete()
    Bldg.objects.filter(decedent=decedent).delete()
    PropertyAcquirer.objects.filter(decedent=decedent).delete()
    CashAcquirer.objects.filter(decedent=decedent).delete()

def save_step_three_datas(user, forms, form_sets, data, data_idx):
    """ステップ３のデータ登録・更新処理

    Args:
        user (User): ユーザーデータ
        forms (form[]): データ操作対象のフォームを格納した配列
        form_sets (form_set[]): データ操作対象のフォームセットを格納した配列

    Returns:
        _type_: _description_
    """

    forms_idx = get_forms_idx_for_step_three()
    form_sets_idx = get_formsets_idx_for_step_three()
    function_name = get_current_function_name()
    try:
        #被相続人
        decedent = save_step_three_decedent_data(forms[forms_idx["decedent"]], user)
        #更新ではなく常に新規登録するモデルについてのデータ削除処理
        del_data_for_step_three(decedent)
        # 配偶者
        save_step_three_spouse_data(
            data[data_idx["spouse"]], 
            forms[forms_idx["spouse"]], 
            decedent, 
            user
        )
        # 遺産分割方法
        save_step_three_form(
            decedent,
            user,
            forms[forms_idx["type_of_division"]]
        )
        #不動産の数
        save_step_three_form(
            decedent,
            user,
            forms[forms_idx["number_of_properties"]]
        )
        #申請情報
        save_step_three_form(
            decedent,
            user,
            forms[forms_idx["application"]]
        )
        # 登記簿上の氏名住所
        save_step_three_registry_name_and_address(
            decedent,
            user,
            form_sets[form_sets_idx["registry_name_and_address"]],
        )
        # 子（前配偶者がいるとき、前配偶者の新規登録又は更新をしてから更新する）
        descendant_content_type = ContentType.objects.get_for_model(Descendant)
        update_form_set(
            data[data_idx["child"]], 
            form_sets[form_sets_idx["child"]],
            user,
            decedent,
            descendant_content_type,
            "前配偶者",
        )
        #子の配偶者
        update_form_set(
            data[data_idx["child_spouse"]],
            form_sets[form_sets_idx["child_spouse"]],
            user,
            decedent,
        )
        #孫
        update_form_set(
            data[data_idx["grand_child"]],
            form_sets[form_sets_idx["grand_child"]],
            user,
            decedent,
            descendant_content_type,
            "子の前配偶者"
        )
        #尊属
        update_form_set(
            data[data_idx["ascendant"]],
            form_sets[form_sets_idx["ascendant"]],
            user,
            decedent
        )
        #兄弟姉妹
        update_form_set(
            data[data_idx["collateral"]],
            form_sets[form_sets_idx["collateral"]],
            user,
            decedent,
            ContentType.objects.get_for_model(Collateral),
            "異父又は異母"
        )
        #土地
        if forms[forms_idx["number_of_properties"]].cleaned_data.get("land") > 0:
            land_index_and_properties = save_step_three_step_property(
                decedent,
                user,
                form_sets[form_sets_idx["land"]],
            )
            #土地取得者
            land_content_type = ContentType.objects.get_for_model(Land)
            save_step_three_acquirer(
                decedent,
                user,
                form_sets[form_sets_idx["land_acquirer"]],
                land_content_type,
                land_index_and_properties,
            )
            #土地金銭取得者
            if is_any_exchange_property(form_sets[form_sets_idx["land"]]):
                save_step_three_acquirer(
                    decedent,
                    user,
                    form_sets[form_sets_idx["land_cash_acquirer"]],
                    land_content_type,
                    land_index_and_properties,
                )
        #建物
        if forms[forms_idx["number_of_properties"]].cleaned_data.get("house") > 0:
            house_index_and_properties = save_step_three_step_property(
                decedent,
                user,
                form_sets[form_sets_idx["house"]],
                )
            #建物取得者
            house_content_type = ContentType.objects.get_for_model(House)
            save_step_three_acquirer(
                decedent,
                user,
                form_sets[form_sets_idx["house_acquirer"]],
                house_content_type,
                house_index_and_properties,
            )
            #建物金銭取得者
            if is_any_exchange_property(form_sets[form_sets_idx["house"]]):
                save_step_three_acquirer(
                    decedent,
                    user,
                    form_sets[form_sets_idx["house_cash_acquirer"]],
                    house_content_type,
                    house_index_and_properties,
                )
        #区分建物
        if forms[forms_idx["number_of_properties"]].cleaned_data.get("bldg") > 0:
            bldg_index_and_properties = save_step_three_step_property(
                decedent,
                user,
                form_sets[form_sets_idx["bldg"]],
                )
            #敷地権
            save_step_three_site(
                decedent,
                user,
                form_sets[form_sets_idx["site"]],
                bldg_index_and_properties,
            )
            #区分建物取得者
            bldg_content_type = ContentType.objects.get_for_model(Bldg)
            save_step_three_acquirer(
                decedent,
                user,
                form_sets[form_sets_idx["bldg_acquirer"]],
                bldg_content_type,
                bldg_index_and_properties,
            )
            #区分建物金銭取得者
            if is_any_exchange_property(form_sets[form_sets_idx["bldg"]]):
                save_step_three_acquirer(
                    decedent,
                    user,
                    form_sets[form_sets_idx["bldg_cash_acquirer"]],
                    bldg_content_type,
                    bldg_index_and_properties,
                )
    except (DatabaseError, ValidationError) as e:
        basic_log(function_name, e, user)
        raise e
    except Exception as e:
        basic_log(function_name, e, user)
        raise e
        
def get_data_idx_for_document():
    idxs = {
        "registry_name_and_address": 0,
        "spouse": 1,
        "child": 2,
        "child_spouse": 3,
        "grand_child": 4,
        "ascendant": 5,
        "collateral": 6,
        "type_of_division": 7,
        "number_of_properties": 8,
        "land": 9,
        "land_acquirer": 10,
        "land_cash_acquirer": 11,
        "house": 12,
        "house_acquirer": 13,
        "house_cash_acquirer": 14,
        "bldg": 15,
        "site": 16,
        "bldg_acquirer": 17,
        "bldg_cash_acquirer": 18,
        "application": 19,
    }
    return idxs

def get_data_for_document(decedent):
    """_summary_
    被相続人に紐づくステップ３で使用するデータを取得する
    Args:
        decedent (Decedent): 被相続人のデータ
    """
    function_name = get_current_function_name()
    try:
        registry_name_and_address_data = RegistryNameAndAddress.objects.filter(decedent=decedent).order_by('id')
        spouse_data = Spouse.objects.filter(object_id=decedent.id).first()
        child_data = Descendant.objects.filter(object_id1=decedent.id).order_by('id')
        child_ids = child_data.values_list('id', flat=True)  # child_dataの各要素が持つIDのリストを取得
        child_spouse_data = Spouse.objects.filter(object_id__in=child_ids).order_by('id')
        grand_child_data = Descendant.objects.filter(object_id1__in=child_ids).order_by('id')
        ascendant_data = Ascendant.objects.filter(decedent=decedent).order_by('id')
        collateral_data = Collateral.objects.filter(decedent=decedent).order_by('id')
        type_of_division_data = TypeOfDivision.objects.filter(decedent=decedent).first()
        number_of_properties_data = NumberOfProperties.objects.filter(decedent=decedent).first()
        land_data = Land.objects.filter(decedent=decedent).order_by('id')
        land_content_type = ContentType.objects.get_for_model(Land)
        land_acquirer_data = PropertyAcquirer.objects.filter(decedent=decedent, content_type1=land_content_type).order_by('id')
        land_cash_acquirer_data = CashAcquirer.objects.filter(decedent=decedent, content_type1=land_content_type).order_by('id')
        house_data = House.objects.filter(decedent=decedent).order_by('id')
        house_content_type = ContentType.objects.get_for_model(House)
        house_acquirer_data = PropertyAcquirer.objects.filter(decedent=decedent, content_type1=house_content_type).order_by('id')
        house_cash_acquirer_data = CashAcquirer.objects.filter(decedent=decedent, content_type1=house_content_type).order_by('id')
        bldg_data = Bldg.objects.filter(decedent=decedent).order_by('id')
        site_data = Site.objects.filter(decedent=decedent).order_by('id')
        bldg_content_type = ContentType.objects.get_for_model(Bldg)
        bldg_acquirer_data = PropertyAcquirer.objects.filter(decedent=decedent, content_type1=bldg_content_type).order_by('id')
        bldg_cash_acquirer_data = CashAcquirer.objects.filter(decedent=decedent, content_type1=bldg_content_type).order_by('id')
        application_data = Application.objects.filter(decedent=decedent).first()
        return [
            registry_name_and_address_data,
            spouse_data, child_data, child_spouse_data, grand_child_data, ascendant_data, collateral_data,
            type_of_division_data,
            number_of_properties_data,
            land_data, land_acquirer_data, land_cash_acquirer_data,
            house_data, house_acquirer_data, house_cash_acquirer_data,
            bldg_data, site_data, bldg_acquirer_data, bldg_cash_acquirer_data,
            application_data,
        ]
    except (MultipleObjectsReturned, DatabaseError) as e:
        basic_log(function_name, e, None, f"被相続人id：{decedent.id}")
        raise e
    except Exception as e:
        basic_log(function_name, e, None, f"被相続人id：{decedent.id}")
        raise e

step_three_formset_configuration = [
    (StepThreeRegistryNameAndAddressForm, 1, 10),
    (StepThreeDescendantForm, 0, 15),
    (StepThreeSpouseForm, 0, 15),
    (StepThreeDescendantForm, 0, 15),
    (StepThreeAscendantForm, 0, 15),
    (StepThreeCollateralForm, 0, 15),
    (StepThreeLandForm, 1, 20),
    (StepThreeLandAcquirerForm, 1, 20),
    (StepThreeLandCashAcquirerForm, 1, 20),
    (StepThreeHouseForm, 1, 20),
    (StepThreeHouseAcquirerForm, 1, 20),
    (StepThreeHouseCashAcquirerForm, 1, 20),
    (StepThreeBldgForm, 1, 20),
    (StepThreeSiteForm, 1, 20),
    (StepThreeBldgAcquirerForm, 1, 20),
    (StepThreeBldgCashAcquirerForm, 1, 20),    
]

def create_formset(form, extra, max_num):
    return formset_factory(form=form, extra=extra, max_num=max_num)

def get_formsets_for_step_three():
    form_sets = [create_formset(form, extra, max_num) for form, extra, max_num in step_three_formset_configuration]
    return form_sets

def get_forms_for_step_three_post(request, decedent, data, data_idx):
    forms = [
        StepThreeDecedentForm(
            request.POST or None,
            prefix="decedent",
            instance=decedent,
        ),
        StepThreeSpouseForm(
            request.POST or None,
            prefix="spouse",
            instance=data[data_idx["spouse"]] if data[data_idx["spouse"]] else None,
        ),
        StepThreeTypeOfDivisionForm(
            request.POST or None,
            prefix="type_of_division",
            instance=data[data_idx["type_of_division"]] if data[data_idx["type_of_division"]] else None,
        ),
        StepThreeNumberOfPropertiesForm(
            request.POST or None,
            prefix="number_of_properties",
            instance=data[data_idx["number_of_properties"]] if data[data_idx["number_of_properties"]] else None,
        ),
        StepThreeApplicationForm(
            request.POST or None,
            prefix="application",
            instance=data[data_idx["application"]] if data[data_idx["application"]] else None,
        ),
    ]    
    return forms

def get_formsets_idx_for_step_three():
    idxs = {
        "registry_name_and_address": 0,
        "child": 1,
        "child_spouse": 2,
        "grand_child": 3,
        "ascendant": 4,
        "collateral": 5,
        "land": 6,
        "land_acquirer": 7,
        "land_cash_acquirer": 8,
        "house": 9,
        "house_acquirer": 10,
        "house_cash_acquirer": 11,
        "bldg": 12,
        "site": 13,
        "bldg_acquirer": 14,
        "bldg_cash_acquirer": 15,
    }
    return idxs

def get_form_sets_for_step_three_post(request, form_sets, form_sets_idxs, data, data_idxs):
    form_sets =[
        form_sets[form_sets_idxs["registry_name_and_address"]](
            request.POST or None,
            initial=get_registry_name_and_address_initial_data(data[data_idxs["registry_name_and_address"]]),
            prefix="registry_name_and_address",
        ),
        form_sets[form_sets_idxs["child"]](
            request.POST or None,
            initial=get_descendant_or_collateral_initial_data(data[data_idxs["child"]], Descendant),
            prefix="child",
        ),
        form_sets[form_sets_idxs["child_spouse"]](
            request.POST or None,
            initial=get_spouse_or_ascendant_initial_data(data[data_idxs["child_spouse"]]),
            prefix="child_spouse",
        ),
        form_sets[form_sets_idxs["grand_child"]](
            request.POST or None,
            initial=get_descendant_or_collateral_initial_data(data[data_idxs["grand_child"]], Descendant),
            prefix="grand_child",
        ),
        form_sets[form_sets_idxs["ascendant"]](
            request.POST or None,
            initial=get_spouse_or_ascendant_initial_data(data[data_idxs["ascendant"]]),
            prefix="ascendant",
        ),
        form_sets[form_sets_idxs["collateral"]](
            request.POST or None,
            initial=get_descendant_or_collateral_initial_data(data[data_idxs["collateral"]], Collateral),
            prefix="collateral",
        ),
        form_sets[form_sets_idxs["land"]](
            request.POST or None,
            initial=get_property_initial_data(data[data_idxs["land"]]),
            prefix="land",
        ),
        form_sets[form_sets_idxs["land_acquirer"]](
            request.POST or None,
            initial=get_acquirer_initial_data(data[data_idxs["land_acquirer"]]), 
            prefix="land_acquirer",
        ),
        form_sets[form_sets_idxs["land_cash_acquirer"]](
            request.POST or None,
            initial=get_acquirer_initial_data(data[data_idxs["land_cash_acquirer"]]), 
            prefix="land_cash_acquirer",
        ),
        form_sets[form_sets_idxs["house"]](
            request.POST or None,
            initial=get_property_initial_data(data[data_idxs["house"]]),
            prefix="house",
        ),
        form_sets[form_sets_idxs["house_acquirer"]](
            request.POST or None,
            initial=get_acquirer_initial_data(data[data_idxs["house_acquirer"]]),
            prefix="house_acquirer",
        ),
        form_sets[form_sets_idxs["house_cash_acquirer"]](
            request.POST or None,
            initial=get_acquirer_initial_data(data[data_idxs["house_cash_acquirer"]]),
            prefix="house_cash_acquirer",
        ),
        form_sets[form_sets_idxs["bldg"]](
            request.POST or None,
            initial=get_property_initial_data(data[data_idxs["bldg"]]), 
            prefix="bldg",
        ),
        form_sets[form_sets_idxs["site"]](
            request.POST or None,
            initial=get_property_initial_data(data[data_idxs["site"]]),
            prefix="site",
        ),
        form_sets[form_sets_idxs["bldg_acquirer"]](
            request.POST or None, 
            initial=get_acquirer_initial_data(data[data_idxs["bldg_acquirer"]]),
            prefix="bldg_acquirer",
        ),
        form_sets[form_sets_idxs["bldg_cash_acquirer"]](
            request.POST or None, 
            initial=get_acquirer_initial_data(data[data_idxs["bldg_cash_acquirer"]]),
            prefix="bldg_cash_acquirer",
        ),
    ]    
    return form_sets

#メイン
def step_three(request):
    try:
        #ログインユーザー以外はログインページに遷移させる
        if not request.user.is_authenticated:
            return redirect(to='/account/login/')
        
        #ユーザーに紐づく被相続人データを取得する
        user = User.objects.get(email = request.user)
        decedent = user.decedent.first()
        
        #被相続人データがないときは、ステップ１に遷移させる
        if not decedent:
            return redirect(to='/toukiApp/step_one/')
        
        function_name = get_current_function_name()
        
        #被相続人に紐づくデータを取得する
        data = get_data_for_document(decedent)
        data_idx = get_data_idx_for_document()
        
        #フォームセットを生成
        form_sets = get_formsets_for_step_three()
        form_sets_idx = get_formsets_idx_for_step_three()
        
        #フォームからデータがPOSTされたとき
        if request.method == "POST":
            if request.user != decedent.user:
                messages.error(request, 'アカウントデータが一致しません。')
                return redirect('/toukiApp/index')
            #フォームセットの属性を更新
            forms = get_forms_for_step_three_post(request, decedent, data, data_idx)
            form_sets = get_form_sets_for_step_three_post(request, form_sets, form_sets_idx, data, data_idx)

            # if not all(form.is_valid() for form in forms) or not all(form_set.is_valid() for form_set in form_sets):
            #     for form in forms:
            #         if not form.is_valid():
            #             print(f"Form {form} errors: {form.errors}")
            #     for form_set in form_sets:
            #         if not form_set.is_valid():
            #             print(f"Formset {form_set} errors: {form_set.errors}")
            #     return redirect('/toukiApp/step_three')
            # else:
            #     return redirect('/toukiApp/step_four')
            if all(form.is_valid() for form in forms) and all(form_set.is_valid() for form_set in form_sets):
                try:
                    with transaction.atomic():
                        save_step_three_datas(user, forms, form_sets, data, data_idx)
                except DatabaseError as e:
                    basic_log(function_name, e, user)
                    messages.error(request, 'データ登録処理でエラー発生。\nページを更新しても解決しない場合は、お問い合わせからお知らせお願いします。')
                    return redirect('/toukiApp/step_three')
                except ValidationError as e:
                    basic_log(function_name, e, user)
                    return HttpResponse("データと入力内容に不一致がありました\nお手数ですが、再度ご入力をお願いします", status=400)
                except Exception as e:
                    basic_log(function_name, e, user)
                    messages.error(request, 'データ登録処理でエラー発生。\nページを更新しても解決しない場合は、お問い合わせからお知らせお願いします。')
                    return HttpResponse("想定しないエラーが発生しました。\nお手数ですが、お問い合わせからご連絡をお願いします", status=500)
                else:
                    return redirect('/toukiApp/step_four')
            else:
                for form in forms:
                    if not form.is_valid():
                        basic_log(function_name, None, user, f"Form {form} errors: {form.errors}")
                for form_set in form_sets:
                    if not form_set.is_valid():
                        basic_log(function_name, None, user, f"Formset {form_set} errors: {form_set.errors}")
                return redirect('/toukiApp/step_three')
        
        #入力が完了している項目を取得するための配列
        user_data_scope = [] 
        progress = decedent.progress
        #被相続人のデータを初期値にセットしたフォーム
        decedent_form = StepThreeDecedentForm(prefix="decedent", instance=decedent)
        
        #登記簿上の氏名住所のデータを取得してデータがあるとき
        registry_name_and_address_data = data[data_idx["registry_name_and_address"]]
        if registry_name_and_address_data.exists():
            #余分なフォームを消すためにextraを0に変更して、初期値を与える
            form_set = formset_factory(
                form=StepThreeRegistryNameAndAddressForm, 
                extra=0, 
                max_num=10
            )
            registry_name_and_address_forms = form_set(
                initial = get_registry_name_and_address_initial_data(registry_name_and_address_data),
                prefix="registry_name_and_address"
            )
            #被相続人情報の入力状況チェック
            if step_three_input_status(decedent):
                user_data_scope.append("decedent")
            #登記簿上の氏名住所の入力状況チェック
            if step_three_input_status(registry_name_and_address_data):
                user_data_scope.append("registry_name_and_address")
        #ないとき    
        else:
            registry_name_and_address_forms = form_sets[form_sets_idx["registry_name_and_address"]](prefix="registry_name_and_address")
        #配偶者
        spouse_data = data[data_idx["spouse"]]
        if spouse_data:
            spouse_form = StepThreeSpouseForm(prefix="spouse", instance=spouse_data)
            if step_three_input_status(spouse_data):
                user_data_scope.append("spouse")
        else:
            spouse_form = StepThreeSpouseForm(prefix="spouse")
        #子
        child_data = data[data_idx["child"]]
        if child_data.exists():
            child_forms = form_sets[form_sets_idx["child"]](
                initial=get_descendant_or_collateral_initial_data(child_data, Descendant),
                prefix="child"
            )
            if step_three_input_status(child_data):
                user_data_scope.append("child")
        else:
            child_forms = form_sets[form_sets_idx["child"]](prefix="child")
        #子の配偶者
        child_spouse_data = data[data_idx["child_spouse"]]
        if child_spouse_data.exists():
            child_spouse_forms = form_sets[form_sets_idx["child_spouse"]](
                initial=get_spouse_or_ascendant_initial_data(child_spouse_data), 
                prefix="child_spouse")
            if step_three_input_status(child_spouse_data):
                user_data_scope.append("child_spouse")
        else:
            child_spouse_forms = form_sets[form_sets_idx["child_spouse"]](prefix="child")
        #孫
        grand_child_data = data[data_idx["grand_child"]]
        if grand_child_data.exists():
            grand_child_forms = form_sets[form_sets_idx["grand_child"]](
                initial=get_descendant_or_collateral_initial_data(grand_child_data, Descendant),
                prefix="grand_child"
            )
            if step_three_input_status(grand_child_data):
                user_data_scope.append("grand_child")
        else:
            grand_child_forms = form_sets[form_sets_idx["grand_child"]](prefix="grand_child")
        #尊属
        ascendant_data = data[data_idx["ascendant"]]
        if ascendant_data.exists():
            ascendant_forms = form_sets[form_sets_idx["ascendant"]](
                initial=get_spouse_or_ascendant_initial_data(ascendant_data),
                prefix="ascendant")
            if step_three_input_status(ascendant_data):
                user_data_scope.append("ascendant")
        else:
            ascendant_forms = form_sets[form_sets_idx["ascendant"]](prefix="ascendant")
        #兄弟姉妹
        collateral_data = data[data_idx["collateral"]]
        if collateral_data.exists():
            collateral_forms = form_sets[form_sets_idx["collateral"]](
                initial=get_descendant_or_collateral_initial_data(collateral_data, Collateral),
                prefix="collateral"
            )
            if step_three_input_status(collateral_data):
                user_data_scope.append("collateral")
        else:
            collateral_forms = form_sets[form_sets_idx["collateral"]](prefix="collateral")
        #遺産分割方法
        type_of_division_data = data[data_idx["type_of_division"]]
        if type_of_division_data:
            type_of_division_form = StepThreeTypeOfDivisionForm(prefix="type_of_division", instance=type_of_division_data)
            if step_three_input_status(type_of_division_data):
                user_data_scope.append("type_of_division")
        else:
            type_of_division_form = StepThreeTypeOfDivisionForm(prefix="type_of_division")
        #不動産の数
        number_of_properties_data = data[data_idx["number_of_properties"]]
        if number_of_properties_data:
            number_of_properties_form = StepThreeNumberOfPropertiesForm(prefix="number_of_properties", instance=number_of_properties_data)
            if step_three_input_status(number_of_properties_data):
                user_data_scope.append("number_of_properties")
        else:
            number_of_properties_form = StepThreeNumberOfPropertiesForm(prefix="number_of_properties")
        #土地
        land_data = data[data_idx["land"]]
        if land_data.exists():
            form_set = formset_factory(
                form=StepThreeLandForm,
                extra=0,
                max_num=20
            )
            land_forms = form_set(
                initial=get_property_initial_data(land_data),
                prefix="land"
            )
            if step_three_input_status(land_data):
                user_data_scope.append("land")
        else:
            land_forms = form_sets[form_sets_idx["land"]](prefix="land")
            
        #土地取得者
        land_acquirer_data = data[data_idx["land_acquirer"]]
        if land_acquirer_data.exists():
            form_set = formset_factory(
                form=StepThreeLandAcquirerForm,
                extra=0,
                max_num=20
            )
            land_acquirer_forms = form_set(
                initial=get_acquirer_initial_data(land_acquirer_data), 
                prefix="land_acquirer"
            )
            if step_three_input_status(land_acquirer_data):
                user_data_scope.append("land_acquirer")
        else:
            land_acquirer_forms = form_sets[form_sets_idx["land_acquirer"]](prefix="land_acquirer")
            
        #土地金銭取得者
        land_cash_acquirer_data = data[data_idx["land_cash_acquirer"]]
        if land_cash_acquirer_data.exists():
            form_set = formset_factory(
                form=StepThreeLandCashAcquirerForm,
                extra=0,
                max_num=20
            )
            land_cash_acquirer_forms = form_set(
                initial=get_acquirer_initial_data(land_cash_acquirer_data),
                prefix="land_cash_acquirer"
            )
            if step_three_input_status(land_cash_acquirer_data):
                user_data_scope.append("land_cash_acquirer")
        else:
            land_cash_acquirer_forms = form_sets[form_sets_idx["land_cash_acquirer"]](prefix="land_cash_acquirer")
        #建物
        house_data = data[data_idx["house"]]
        if house_data.exists():
            form_set = formset_factory(
                form=StepThreeHouseForm,
                extra=0,
                max_num=20
            )
            house_forms = form_set(
                initial=get_property_initial_data(house_data),
                prefix="house"
            )
            if step_three_input_status(house_data):
                user_data_scope.append("house")
        else:
            house_forms = form_sets[form_sets_idx["house"]](prefix="house")
        #建物取得者
        house_acquirer_data = data[data_idx["house_acquirer"]]
        if house_acquirer_data.exists():
            form_set = formset_factory(
                form=StepThreeHouseAcquirerForm,
                extra=0,
                max_num=20
            )
            house_acquirer_forms = form_set(
                initial=get_acquirer_initial_data(house_acquirer_data),
                prefix="house_acquirer"
            )
            if step_three_input_status(house_acquirer_data):
                user_data_scope.append("house_acquirer")
        else:
            house_acquirer_forms = form_sets[form_sets_idx["house_acquirer"]](prefix="house_acquirer")
        
        #建物金銭取得者
        house_cash_acquirer_data = data[data_idx["house_cash_acquirer"]]
        if house_cash_acquirer_data.exists():
            form_set = formset_factory(
                form=StepThreeHouseCashAcquirerForm, 
                extra=0,
                max_num=20
            )
            house_cash_acquirer_forms = form_set(
                initial=get_acquirer_initial_data(house_cash_acquirer_data),
                prefix="house_cash_acquirer"
            )
            if step_three_input_status(house_cash_acquirer_data):
                user_data_scope.append("house_cash_acquirer")
        else:
            house_cash_acquirer_forms = form_sets[form_sets_idx["house_cash_acquirer"]](prefix="house_cash_acquirer")    
        #区分建物
        bldg_data = data[data_idx["bldg"]]
        if bldg_data.exists():
            form_set = formset_factory(
                form=StepThreeBldgForm,
                extra=0,
                max_num=20
            )
            bldg_forms = form_set(
                initial=get_property_initial_data(bldg_data), 
                prefix="bldg"
            )
            if step_three_input_status(bldg_data):
                user_data_scope.append("bldg")
        else:
            bldg_forms = form_sets[form_sets_idx["bldg"]](prefix="bldg")
        #敷地権
        site_data = data[data_idx["site"]]
        if site_data.exists():
            form_set = formset_factory(
                form=StepThreeSiteForm,
                extra=0,
                max_num=20
            )
            site_forms = form_set(
                initial=get_property_initial_data(site_data),
                prefix="site"
            )
            if step_three_input_status(site_data):
                user_data_scope.append("site")
        else:
            site_forms = form_sets[form_sets_idx["site"]](prefix="site")
        #区分建物取得者
        bldg_acquirer_data = data[data_idx["bldg_acquirer"]]
        if bldg_acquirer_data.exists():
            form_set = formset_factory(
                form=StepThreeBldgAcquirerForm,
                extra=0,
                max_num=20
            )
            bldg_acquirer_forms = form_set(
                initial=get_acquirer_initial_data(bldg_acquirer_data),
                prefix="bldg_acquirer"
            )
            if step_three_input_status(bldg_acquirer_data):
                user_data_scope.append("bldg_acquirer")
        else:
            bldg_acquirer_forms = form_sets[form_sets_idx["bldg_acquirer"]](prefix="bldg_acquirer")
        #区分建物金銭取得者
        bldg_cash_acquirer_data = data[data_idx["bldg_cash_acquirer"]]
        if bldg_cash_acquirer_data.exists():
            form_set = formset_factory(
                form=StepThreeBldgCashAcquirerForm, 
                extra=0,
                max_num=20
            )
            bldg_cash_acquirer_forms = form_set(
                initial=get_acquirer_initial_data(bldg_cash_acquirer_data),
                prefix="bldg_cash_acquirer"
            )
            if step_three_input_status(bldg_cash_acquirer_data):
                user_data_scope.append("bldg_cash_acquirer")
        else:
            bldg_cash_acquirer_forms = form_sets[form_sets_idx["bldg_cash_acquirer"]](prefix="bldg_cash_acquirer")
        #申請情報
        application_data = data[data_idx["application"]]
        if application_data:
            application_form = StepThreeApplicationForm(prefix="application", instance=application_data)
            if step_three_input_status(application_data):
                user_data_scope.append("application")
        else:
            application_form = StepThreeApplicationForm(prefix="application")

        context = {
            "title" : "３．データ入力",
            "progress": progress,
            "user" : user,
            "user_data_scope": json.dumps(user_data_scope),
            "decedent": decedent,
            "decedent_form": decedent_form,
            "registry_name_and_address_forms": registry_name_and_address_forms,
            "spouse_form": spouse_form,
            "child_forms": child_forms,
            "child_spouse_forms": child_spouse_forms,
            "grand_child_forms": grand_child_forms,
            "ascendant_forms": ascendant_forms,
            "collateral_forms": collateral_forms,
            "type_of_division_form": type_of_division_form,
            "number_of_properties_form": number_of_properties_form,
            "land_forms": land_forms,
            "land_acquirer_forms": land_acquirer_forms,
            "land_cash_acquirer_forms": land_cash_acquirer_forms,
            "house_forms": house_forms,
            "house_acquirer_forms": house_acquirer_forms,
            "house_cash_acquirer_forms": house_cash_acquirer_forms,
            "bldg_forms": bldg_forms,
            "site_forms": site_forms,
            "bldg_acquirer_forms": bldg_acquirer_forms,
            "bldg_cash_acquirer_forms": bldg_cash_acquirer_forms,
            "application_form": application_form,
            "sections" : Sections.SECTIONS[Sections.STEP3],
            "service_content" : Sections.SERVICE_CONTENT,
        }
        return render(request, "toukiApp/step_three.html", context)
    except HTTPError as e:
        basic_log(function_name, e, user)
        messages.error(request, f'通信エラー（コード：{e.response.status_code}）が発生したため処理が中止されました。\
                       \nコードが５００の場合は、お手数ですがお問い合わせからご連絡をお願いします。')
        return render(request, "toukiApp/step_three.html", context)
    except ConnectionError as e:
        basic_log(function_name, e, user)
        messages.error(request, '通信エラーが発生したため処理が中止されました。\nお手数ですが、再入力をお願いします。')
        return render(request, "toukiApp/step_three.html", context)        
    except Timeout as e:
        basic_log(function_name, e, user)
        messages.error(request, 'システムに接続できませんでした。\nお手数ですが、ネットワーク環境をご確認のうえ再入力をお願いします。')
        return render(request, "toukiApp/step_three.html", context)   
    except Exception as e:
        basic_log(function_name, e, user)
        return HttpResponse("想定しないエラーが発生しました\nお問い合わせからご連絡をお願いします", status=500)

#
# ステップ4
# 

def step_four(request):
    """ステップ４のメイン処理

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if not request.user.is_authenticated:
        return redirect(to='/account/login/')
    
    user = User.objects.get(email = request.user)
    decedent = user.decedent.first()
    
    if not decedent:
        return redirect(to='/toukiApp/step_one/')
    
    data = get_data_for_document(decedent)
    data_idx = get_data_idx_for_document()
    heirs = get_heirs(decedent)
    minors = [heir for heir in heirs if hasattr(heir, 'is_adult') and heir.is_adult is False]
    overseas = [heir for heir in heirs if hasattr(heir, 'is_japan') and heir.is_japan is False]
    context = {
        "title" : "４．書類の印刷",
        "user" : user,
        "decedent": decedent,
        "progress": decedent.progress,
        "heirs": heirs,
        "minors": minors,
        "overseas": overseas,
        "sections" : Sections.SECTIONS[Sections.STEP4],
        "service_content" : Sections.SERVICE_CONTENT,
    }
    return render(request, "toukiApp/step_four.html", context)

def step_division_agreement(request):
    """遺産分割協議証明書の表示

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        if not request.user.is_authenticated:
            return redirect(to='/account/login/')
        
        user = User.objects.get(email = request.user)
        decedent = user.decedent.first()
        
        if not decedent:
            return redirect(to='/toukiApp/step_one/')
        
        function_name = get_current_function_name()
        
        #被相続人の氏名、死亡年月日、死亡時の住所
        decedent_info = get_decedent_info_for_division_agreement(decedent)
        
        property_acquirer_data = PropertyAcquirer.objects.filter(decedent=decedent).select_related('content_type1', 'content_type2')
        cash_acquirer_data = CashAcquirer.objects.filter(decedent=decedent).select_related('content_type1', 'content_type2')
        sites = Site.objects.filter(decedent=decedent)
        
        #区分建物データがあるとき、敷地権データも存在するかチェック
        check_bldg_and_site_related(property_acquirer_data, sites)
        
        #換価しない不動産と相続人を紐づける
        normal_division_properties = get_normal_division_properties(property_acquirer_data, cash_acquirer_data)
        
        #換価する不動産と相続人を紐づける
        exchange_division_properties = None
        if cash_acquirer_data.exists():
            exchange_division_properties = get_exchange_division_properties(property_acquirer_data, cash_acquirer_data)
        
        context = {
            "title" : "遺産分割協議証明書",
            "decedent_info": decedent_info,
            "normal_division_properties": normal_division_properties,
            "exchange_division_properties": exchange_division_properties,
            "sites": sites,
        }
        return render(request, "toukiApp/step_division_agreement.html", context)
    except DatabaseError as e:
        messages.error(request, 'データベース処理でエラーが発生しました。\n再度このエラーが出る場合は、お問い合わせからお知らせお願いします。')
        return redirect('/toukiApp/step_three')
    except HTTPError as e:
        basic_log(function_name, e, user)
        messages.error(request, f'通信エラー（コード：{e.response.status_code}）が発生したため処理が中止されました。\
                       \nコードが５００の場合は、お手数ですがお問い合わせからご連絡をお願いします。')
        return render(request, "toukiApp/step_three.html", context)
    except ConnectionError as e:
        basic_log(function_name, e, user)
        messages.error(request, '通信エラーが発生したため処理が中止されました。\nお手数ですが、再入力をお願いします。')
        return render(request, "toukiApp/step_three.html", context)        
    except Timeout as e:
        basic_log(function_name, e, user)
        messages.error(request, 'システムに接続できませんでした。\nお手数ですが、ネットワーク環境をご確認のうえ再入力をお願いします。')
        return render(request, "toukiApp/step_three.html", context)   
    except ValidationError as e:
        basic_log(function_name, e, user)
        return HttpResponse("登録されているデータに誤りがあります\nお手数ですが、お問い合わせをお願いします", status=400)
    except Exception as e:
        basic_log(function_name, e, user)
        return HttpResponse("想定しないエラーが発生しました\nお手数ですが、お問い合わせをお願いします", status=500)

def check_bldg_and_site_related(acquirer_data, site_data):
    """区分建物と敷地権のデータが正確に紐づいているか判別する

    Args:
        acquirer_data (_type_): _description_
        site_data (_type_): _description_
    """
    function_name = get_current_function_name()
    bldg_content_type = ContentType.objects.get_for_model(Bldg)
    bldg_related_acquirers = acquirer_data.filter(content_type1=bldg_content_type)
    #区分建物も敷地権もないとき処理をしない
    if not bldg_related_acquirers.exists() and not site_data.exists():
        return True
    
    #区分建物もしくは敷地権のどちらかしかないときエラー
    if bldg_related_acquirers.exists() != site_data.exists():
        raise ValidationError(function_name + "区分建物と敷地権のデータの数が不正です")
    
    #敷地権が全て区分建物と関連付けされているか判別する
    bldg_ids = set(bldg.object_id1 for bldg in bldg_related_acquirers)
    for site in site_data:
        if site.bldg.id not in bldg_ids:
            raise ValidationError(f"{function_name}: 区分建物と関連付けされてない敷地権があります。")
        
    # フィルタリングされたクエリセットにレコードが存在するか判別
    return True

def get_unique_property_acquirer_data(property_acquirer_data, cash_acquirer_data):
    """通常分割の不動産データを取得する

    Args:
        property_acquirer_data (_type_): _description_
        cash_acquirer_data (_type_): _description_

    Returns:
        _type_: _description_
    """
    # Step 1: CashAcquirerのcontent_type1とobject_id1の組み合わせのセットを作成
    cash_content_object1_set = {
        (obj.content_type1_id, obj.object_id1) for obj in cash_acquirer_data
    }

    # Step 2: PropertyAcquirerのレコードをループして、cash_acquirer_dataに含まれないcontent_object1を持つレコードのみを抽出
    return [
        obj for obj in property_acquirer_data
        if (obj.content_type1_id, obj.object_id1) not in cash_content_object1_set
    ]

def get_base_normal_division_data(data):
    """_summary_

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    # PropertyAcquirer インスタンスをループ
    formatted_data = defaultdict(list)
    for d in data:
        content_object1 = d.content_object1
        name = d.content_object2.name
        percentage = d.percentage
        # content_object1をキーとして、content_object2の名前と取得割合のマッピングを追加
        formatted_data[content_object1].append({name: percentage})
        
    return formatted_data

def get_content_object1_duplicate_checked_data(data):
    """_summary_

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    formatted_data = []
    for content_object1, mappings in data.items():
        formatted_data.append((content_object1, mappings))
        
    return formatted_data

def get_group_properties_by_mappings(data):
    """_summary_

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    formatted_data = defaultdict(list)

    # content_object1_duplicate_checked_dataはステップ1で作成したデータ
    for content_object1, mappings in data:
        # mappingsは[{content_object2.name: percentage}, ...]のリスト
        # mappingsを一意のキーとして使用
        key = frozenset((name, percentage) for mapping in mappings for name, percentage in mapping.items())
        formatted_data[key].append(content_object1)
        
    return formatted_data

def get_normal_division_properties(property_acquirer_data, cash_acquirer_data):
    """換価しない不動産情報を取得する
    
    取得者が重複する不動産はまとめて表示する
    返すデータ形式(
        [不動産データ],
        [{"不動産取得者名": "取得割合"}]
    )
    
    Args:
        decedent (_type_): _description_
    """
    try:
        #通常分割の不動産データを取得する
        first_data = get_unique_property_acquirer_data(property_acquirer_data, cash_acquirer_data)
        
        # PropertyAcquirer インスタンスをループ
        second_data = get_base_normal_division_data(first_data)

        # 最終的なデータ構造を準備
        third_data = get_content_object1_duplicate_checked_data(second_data)

        # ステップ1: グループ化のための辞書を準備
        fourth_data = get_group_properties_by_mappings(third_data)

        # ステップ2: 最終的なデータ構造を生成
        return [(content_objects, [dict([item]) for item in key]) for key, content_objects in fourth_data.items()]
     
    except (HTTPError, ConnectionError, Timeout, DatabaseError) as e:
        raise e
    except Exception as e:
        raise e

def get_integrated_acquirers(property_acquirers, cash_acquirers):
    """不動産、不動産取得者、金銭取得者を関連付けして不動産の重複をなくしたデータを返す

    Args:
        property_acquirers (_type_): _description_
        cash_acquirers (_type_): _description_
    """
    formatted_data = defaultdict(lambda: {'property_acquirers': {}, 'cash_acquirers': {}})
    
    # content_object1をキーとする辞書を作成
    property_dict = defaultdict(dict)
    for acquirer in property_acquirers:
        key = (acquirer.content_type1.model, acquirer.object_id1)
        property_dict[key][acquirer.content_object2.name] = acquirer.percentage

    cash_dict = defaultdict(dict)
    for acquirer in cash_acquirers:
        key = (acquirer.content_type1.model, acquirer.object_id1)
        cash_dict[key][acquirer.content_object2.name] = acquirer.percentage

    # property_acquirers と cash_acquirers の共通キーでデータをマージ
    for key in property_dict.keys() & cash_dict.keys():
        formatted_data[key]['property_acquirers'] = property_dict[key]
        formatted_data[key]['cash_acquirers'] = cash_dict[key]
                
    return formatted_data

def get_base_exchange_data(data):
    """換価データの形式に変換したデータを返す

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    return [
        ([{ct1_model: obj_id1}],
         [{key: value} for key, value in acquirers['property_acquirers'].items()],
         [{key: value} for key, value in acquirers['cash_acquirers'].items()])
        for (ct1_model, obj_id1), acquirers in data.items()
    ]

def get_unique_exchange_data(data):
    """取得者の重複を解消したデータを返す

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    formatted_data = defaultdict(lambda: {'models': [], 'property_acquirers': [], 'cash_acquirers': []})

    for record in data:
        ct1_model_obj_id_list, property_acquirers, cash_acquirers = record
        # 辞書型からリストへ変換して比較可能な形式にする
        property_acquirers_dict = {list(item.keys())[0]: list(item.values())[0] for item in property_acquirers}
        cash_acquirers_dict = {list(item.keys())[0]: list(item.values())[0] for item in cash_acquirers}
        
        # property_acquirersとcash_acquirersの組み合わせをキーとする
        key = (frozenset(property_acquirers_dict.items()), frozenset(cash_acquirers_dict.items()))
        
        # すでに存在する組み合わせの場合は、modelsのリストにct1_modelとobj_id1を追加
        formatted_data[key]['models'].extend(ct1_model_obj_id_list)
        if not formatted_data[key]['property_acquirers']:
            formatted_data[key]['property_acquirers'].extend(property_acquirers)
        if not formatted_data[key]['cash_acquirers']:
            formatted_data[key]['cash_acquirers'].extend(cash_acquirers)
    
    return formatted_data

def get_completed_exchange_data(data):
    """テンプレートに渡す形に整形した換価不動産データを返す

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    # モデルインスタンスを格納するための辞書を用意
    model_instances_cache = {}

    # ContentTypeのキャッシュを用意
    content_type_cache = {}

    formatted_data = []

    for key, value in data.items():
        real_models = []

        for model_dict in value['models']:
            for model_name, model_id in model_dict.items():
                # ContentTypeとモデルインスタンスのキャッシュを使用
                model_key = (model_name, model_id)
                if model_key not in model_instances_cache:
                    if model_name not in content_type_cache:
                        content_type_cache[model_name] = ContentType.objects.get(model=model_name)
                    ct = content_type_cache[model_name]
                    model_class = ct.model_class()
                    model_instance = model_class.objects.get(id=model_id)
                    model_instances_cache[model_key] = model_instance
                else:
                    model_instance = model_instances_cache[model_key]
                
                real_models.append(model_instance)

        value['models'] = real_models
        formatted_data.append((value['models'], value['property_acquirers'], value['cash_acquirers']))

    return formatted_data
            
def get_exchange_division_properties(property_acquirer_data, cash_acquirer_data):
    """換価する不動産情報を取得する
    
    取得者が重複する不動産はまとめて表示する
    返すデータ形式(
        [不動産データ],
        [{"不動産取得者名": "取得割合"}],
        [{"金銭取得者名": "取得割合"}]
    )
    Args:
        decedent (_type_): _description_
    """
    try:
        # 不動産、不動産取得者、金銭取得者を連結して不動産の重複をなくす
        first_data = get_integrated_acquirers(property_acquirer_data, cash_acquirer_data)
        
        # テンプレートに渡すデータ形式に変換
        second_data = get_base_exchange_data(first_data)

        # 取得者の重複をなくす
        third_data = get_unique_exchange_data(second_data)

        # 不動産のデータに入れ替えて完成させる
        return get_completed_exchange_data(third_data)
    
    except (HTTPError, ConnectionError, Timeout, DatabaseError) as e:
        raise e
    except Exception as e:
        raise e

def get_decedent_info_for_division_agreement(decedent):
    """遺産分割協議証明書に書く被相続人情報を取得する
    
    取得する情報：被相続人氏名、死亡年月日、死亡時の住所

    Args:
        decedent (_type_): _description_

    Returns:
        _type_: _description_
    """
    info = []
    info.append(decedent.name)
    death_date = decedent.death_year[:4] + "年" + decedent.death_month + "月" + decedent.death_date + "日"
    info.append(death_date)
    prefecture = next((name for code, name in PREFECTURES if code == decedent.prefecture), "不明")
    address = prefecture + decedent.city + decedent.address + decedent.bldg
    info.append(address)
    return info

def step_diagram(request):
    """相続関係説明図の表示

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if not request.user.is_authenticated:
        return redirect(to='/account/login/')
    
    user = User.objects.get(email = request.user)
    decedent = user.decedent.first()
    
    if not decedent:
        return redirect(to='/toukiApp/step_one/')


    context = {
        "title" : "相続関係図",
    }
    return render(request, "toukiApp/step_diagram.html", context)

def step_application_form(request):
    """登記申請書の表示

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    if not request.user.is_authenticated:
        return redirect(to='/account/login/')
    
    user = User.objects.get(email = request.user)
    decedent = user.decedent.first()
    
    if not decedent:
        return redirect(to='/toukiApp/step_one/')
    
    application_form_data = [
        {
            "purpose_of_registration": "",
            "cause": "",
            "acquirers": [
                {
                    "address": "",
                    "percentage": "",
                    "name": "",
                    "phone_number": "",
                }
            ],
            "office": "",
            "agent": {
                "address": "",
                "name": "",
                "phone_number": "",
            },
            "price": "",
            "tax": "",
            "property": [
                {
                    "number": "",
                    "purparty": "",
                    "site_number": "",
                    "site_type": "",
                    "site_purparty": "",
                }
            ],
        },
    ]
    
    lands = Land.objects.filter(decedent=decedent)
    houses = House.objects.filter(decedent=decedent)
    bldgs = Bldg.objects.filter(decedent=decedent)
    
    #管轄別に不動産をまとめる
    
    
    #取得者別に不動産をまとめる
    
    #登記の目的
    purpose_of_registration = get_purpose_of_registration(decedent)
    #原因
    cause = decedent.death_year + decedent.death_month + "月" + decedent.death_date + "日"
    #相続人
    acquirers = get_acquirers_for_application_form(decedent)
    
    data = get_data_for_document(decedent)
    data_idx = get_data_idx_for_document()

    context = {
        "title" : "登記申請書",
        "purpose_of_registration": purpose_of_registration,
        "cause": cause,
    }
    return render(request, "toukiApp/step_application_form.html", context)

def get_acquirers_for_application_form(decedent):
    """申請書に記載する相続人情報を取得する
    
    

    Args:
        decedent (_type_): _description_
    """

def get_purpose_of_registration(decedent):
    """登記の目的を取得する
    
    被相続人が持分のみの不動産を持っているかどうかで変わる

    Args:
        decedent (_type_): _description_

    Returns:
        _type_: _description_
    """
    function_name = get_current_function_name()
    
    lands = Land.objects.filter(decedent=decedent)
    houses = House.objects.filter(decedent=decedent)
    bldgs = Bldg.objects.filter(decedent=decedent)
    
    if not lands.exists() and not houses.exists() and not bldgs.exists():
        raise ValidationError(function_name + "：不動産がありません")

    is_owner = False
    is_purparty = False
    
    if lands.exists():
        for x in lands:
            if x.purparty == "１分の１":
                is_owner = True
            else:
                is_purparty = True
                
            if is_owner and is_purparty:
                break
    
    if houses.exists() and not is_owner and not is_purparty:
        for x in houses:
            if x.purparty == "１分の１":
                is_owner = True
            else:
                is_purparty = True
            
            if is_owner and is_purparty:
                break

    if bldgs.exists() and not is_owner and not is_purparty:
        for x in bldgs:
            if x.purparty == "１分の１":
                is_owner = True
            else:
                is_purparty = True
                
            if is_owner and is_purparty:
                break
    
    if is_owner and not is_purparty:
        return "所有権移転"
    elif is_owner and is_purparty:
        return "所有権移転及び" + decedent.name + "持分全部移転"
    elif not is_owner and is_purparty:
        return decedent.name + "持分全部移転"
    else:
        raise ValidationError(function_name + "所有権割合が登録されてません")
    
#ステップ5
#申請
def step_five(request):
    if not request.user.is_authenticated:
        return redirect(to='/account/login/')
    
    user = User.objects.get(email = request.user)
    
    context = {
        "title" : "５．法務局に郵送",
        "user" : user,
        "sections" : Sections.SECTIONS[Sections.STEP5],
        "service_content" : Sections.SERVICE_CONTENT,
    }
    return render(request, "toukiApp/step_five.html", context)

#ステップ6
#申請後について
def step_six(request):
    if not request.user.is_authenticated:
        return redirect(to='/account/login/')
    
    user = User.objects.get(email = request.user)
    
    context = {
        "title" : "申請後について",
        "user" : user,
        "sections" : Sections.SECTIONS[Sections.STEP6],
        "service_content" : Sections.SERVICE_CONTENT,
    }
    return render(request, "toukiApp/step_six.html", context)

#ユーザー情報
def step_option_select(request):
    if not request.user.is_authenticated:
        return redirect(to='/account/login/')
    
    user = request.user
    
    context = {
        "title": "ユーザー情報",
        "user": user,
    }

    return render(request, 'toukiApp/step_option_select.html', context)

#お問い合わせ
def step_inquiry(request):
    if not request.user.is_authenticated:
        return redirect(to='/account/login/')
    
    user = User.objects.get(email = request.user)
    
    context = {
        "title" : "お問い合わせ",
        "sections" : Sections.SECTIONS,
        "service_content" : Sections.SERVICE_CONTENT,
        "user" : user,
    }
    return render(request, "toukiApp/step_inquiry.html", context)

#お問い合わせ・運営者情報
def administrator(request):
    context = {
        "title" : "運営者情報・お問い合わせ",
        "CompanyData" : CompanyData,
    }
    return render(request, "toukiApp/administrator.html", context)

#特商法
def commerceLaw(request):
    context = {
        "title" : "特定商取引法に基づく表記",
        "CompanyData" : CompanyData,
    }
    return render(request, "toukiApp/commerce-law.html", context)

#プライバシーポリシー
def privacy(request):
    context = {
        "title" : "プライバシーポリシー",
        "CompanyData" : CompanyData,
    }
    return render(request, "toukiApp/privacy.html", context)

#利用規約
def terms(request):
    context = {
        "title" : "利用規約",
        "CompanyData" : CompanyData,
    }
    return render(request, "toukiApp/terms.html", context)

#利用条件確認
def condition(request):
    context = {
        "title" : "利用条件確認",
    }
    return render(request, "toukiApp/condition.html", context)

#不正な投稿があったとき
def csrf_failure(request, reason=""):

    # 何かしらの処理

    return HttpResponseForbidden('<h1>403 アクセスが制限されています。</h1>', content_type='text/html')

# ユーザーに紐づく被相続人の市区町村データを取得する
def get_decedent_city_data(request):
    user = User.objects.get(email = request.user)
    decedent = Decedent.objects.filter(user=user).first()
    
    if decedent:
        repsonse_data = {
            'city': decedent.city,
            'domicileCity': decedent.domicile_city
        }
    else:
        repsonse_data = {}
        
    return JsonResponse(repsonse_data)

# ユーザーに紐づく被相続人の登記上の住所の市区町村データリストを取得する
def get_registry_name_and_address_city_data(request):
    user = User.objects.get(email = request.user)
    decedent = Decedent.objects.filter(user=user).first()
    registry_name_and_address_datas = RegistryNameAndAddress.objects.filter(decedent=decedent)
    
    if registry_name_and_address_datas.exists():
        citys = [data.city for data in registry_name_and_address_datas]
    else:
        citys = []
    repsonse_data = {
        'citys': citys,
    }
    return JsonResponse(repsonse_data)

# ユーザーに紐づく相続人の住所の市区町村データリストを取得する
def get_heirs_city_data(request):
    try:
        user = User.objects.get(email = request.user)
        decedent = Decedent.objects.filter(user=user).first()
        spouse_datas = Spouse.objects.filter(Q(decedent=decedent) & Q(is_heir=True) & ~Q(city__isnull=True) & ~Q(city=""))
        is_ascendant = True
        datas = []
        if spouse_datas.exists():
            contentType = str(ContentType.objects.get_for_model(Spouse).id)
            for d in spouse_datas:
                datas.append([d.id, contentType, d.city])
                if d.object_id != decedent.id:
                    is_ascendant = False
                                
        descendant_datas = Descendant.objects.filter(Q(decedent=decedent) & Q(is_heir=True) & ~Q(city__isnull=True) & ~Q(city=""))
        if descendant_datas.exists():
            contentType = str(ContentType.objects.get_for_model(Descendant).id)
            is_ascendant = False
            for d in descendant_datas:
                datas.append([d.id, contentType, d.city])

        if is_ascendant:
            ascendant_datas = Ascendant.objects.filter(Q(decedent=decedent) & Q(is_heir=True) & ~Q(city__isnull=True) & ~Q(city=""))
            if ascendant_datas.exists():
                contentType = str(ContentType.objects.get_for_model(Ascendant).id)
                for d in ascendant_datas:
                    datas.append([d.id, contentType, d.city])
            else:
                collateral_datas = Collateral.objects.filter(Q(decedent=decedent) & Q(is_heir=True) & ~Q(city__isnull=True) & ~Q(city=""))
                if collateral_datas.exists():
                    contentType = str(ContentType.objects.get_for_model(Collateral).id)
                    for d in collateral_datas:
                        datas.append([d.id, contentType, d.city])
        
        repsonse_data = {
            'datas': datas,
        }
        return JsonResponse(repsonse_data)
    except (OperationalError, ConnectionError) as e:
        return JsonResponse({'エラー原因': 'ネットワークエラー', '詳細': str(e)}, status=500)
    except ObjectDoesNotExist:
        return JsonResponse({'エラー原因': 'データがありません'}, status=404)
    except Exception as e:
        return JsonResponse({'エラー原因': '想定しないエラー', '詳細': str(e)}, status=500)

# 選択された都道府県から市区町村データを取得する
def get_city(request):
    data = json.loads(request.body)
    prefecture = data["prefecture"]
        
    url = "https://www.land.mlit.go.jp/webland/api/CitySearch?area=" + prefecture
    r = requests.get(url)
    r = r.json()
    r = r['data']
    
    if r:
        context = {
            "city": r,
        }
    else:
        context = {
            "city" : "",
        }
        
    return JsonResponse(context)

# 入力された不動産番号から法務局データを取得する
def get_office(request):
    try:
        data = json.loads(request.body)
        officeCode = data["officeCode"]
        office_data = Office.objects.filter(code=officeCode).first()

        if office_data:
            office = office_data.office_name
        else:
            office = ""

        repsonse_data = {
            'office': office,
        }
        return JsonResponse(repsonse_data)
    except (OperationalError, ConnectionError) as e:
        return JsonResponse({'error': 'ネットワークエラーが発生しました', 'details': str(e)}, status=500)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'データがありません'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'エラーが発生しました', 'details': str(e)}, status=500)

#djangoのメール形式チェック
def is_email(request):
    input_email = request.POST.get("email")
    
    try:
        validate_email(input_email)
    except ValidationError:
        context = {"message" : "メールアドレスの規格と一致しません",}
        return JsonResponse(context)

    context = {"message":"",}
    
    return JsonResponse(context)

def step_back(request):
    user = User.objects.get(email = request.user)
    decedent = Decedent.objects.filter(user=user).first()
    data = json.loads(request.body)
    progress = data.get('progress')
    if progress is not None:
        decedent.progress = int(progress)
        decedent.save()
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'})

# 法務局データスクレイピング用（どこかのstep内に配置してデータを更新する）
# def import_offices(html_file_path):
#     with open(html_file_path, 'r', encoding='utf-8') as file:
#         soup = BeautifulSoup(file, 'html.parser')
        
#     for row in soup.find_all('tr'):
#         cols = row.find_all('td')
#         if cols and not cols[0].has_attr('class'):
#             code = cols[0].text.strip()
#             name = cols[1].text.strip()
#             try:
#                 with transaction.atomic():
#                     Office.objects.get_or_create(code=code, name=name, created_by=user, updated_by=user)
#             except Exception as e:
#                 # ログにエラーメッセージを記録します
#                 print(f"Error occurred: {e}")
# HTMLファイルのパスを指定して実行
# import_offices('toukiApp/登記所選択.html')