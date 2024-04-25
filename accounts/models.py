from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import datetime

from common.validations import *
from toukiApp.common_model import *
    
class UserManager(BaseUserManager):
    """ターミナルでユーザーを作成するときに使用される"""
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('名前を入力して下さい')
        
        if not email:
            raise ValueError('メールアドレスを入力して下さい')
        
        username = self.model.normalize_username(username)
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        
        return user
    
    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        return self._create_user( username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff=Trueである必要があります。')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser=Trueである必要があります。')
        
        return self._create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """ユーザーのデータ

    Args:
        AbstractBaseUser (_type_): _description_
        PermissionsMixin (_type_): _description_
    """
    username = models.CharField(verbose_name="氏名", max_length=30, validators=[JapaneseOnlyUsernameValidator()], unique=False, default="")
    address = models.CharField(verbose_name="住所", max_length=100, default="")
    email = models.EmailField(verbose_name="メールアドレス", unique=True)
    phone_number_regex = RegexValidator(regex=r'^[0-9]+$', message = ("ハイフンなしの10桁又は11桁で入力してください"))
    phone_number = models.CharField(verbose_name="電話番号", validators=[phone_number_regex], max_length=11, default="")
    basic = models.BooleanField(verbose_name="システムの有料版", default=False) # システムの本使用
    basic_date = models.DateTimeField(verbose_name="システムの有料版の利用開始日", null=True, blank=True)
    option1 = models.BooleanField(verbose_name="戸籍取得代行の利用状況", default=False)
    option1_date = models.DateTimeField(verbose_name="戸籍取得代行の利用開始日", null=True, blank=True)
    option2 = models.BooleanField(verbose_name="司法書士紹介の利用状況", default=False)
    option2_date = models.DateTimeField(verbose_name="司法書士紹介の利用開始日", null=True, blank=True)
    option3 = models.BooleanField(verbose_name="オプション3の利用状況", default=False)
    option3_date = models.DateTimeField(verbose_name="オプション3の利用開始日", null=True, blank=True)
    option4 = models.BooleanField(verbose_name="オプション4の利用状況", default=False)
    option4_date = models.DateTimeField(verbose_name="オプション4の利用開始日", null=True, blank=True)
    option5 = models.BooleanField(verbose_name="オプション5の利用状況", default=False)
    option5_date = models.DateTimeField(verbose_name="オプション5の利用開始日", null=True, blank=True)
    payment_choice = (
        ("振込", "振込"),
        ("カード", "カード"),
    )
    payment = models.CharField(verbose_name="支払方法", choices=payment_choice, max_length=30, null=True, blank=True)
    pay_amount = models.PositiveIntegerField(verbose_name="支払額", default=0)
    is_staff = models.BooleanField(verbose_name="スタッフ権限", default=False)
    is_active = models.BooleanField(verbose_name="利用状況", default=True)
    last_update = models.DateTimeField(verbose_name="最終更新日", auto_now=True)
    date_joined = models.DateTimeField(verbose_name="利用開始日", auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _("ユーザー")
        verbose_name_plural = _("ユーザー")

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
        
class OptionRequest(CommonModel):
    """オプションの利用申請データ

    Args:
        models (_type_): _description_
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="ユーザー",
        on_delete=models.CASCADE,
        null = False,
        blank = False,
        related_name="option_request",
    )
    
    is_recieved = models.BooleanField(verbose_name="着金確認", default=False)
    is_recieved_date = models.DateTimeField(verbose_name="着金確認日", null=True, blank=True)
    name = models.CharField(verbose_name="氏名", max_length=30, validators=[JapaneseOnlyUsernameValidator()], null=False, blank=False)
    payer = models.CharField(verbose_name="支払名義人", max_length=30, validators=[validate_katakana], null=False, blank=False)
    address = models.CharField(verbose_name="住所", max_length=100, default="")
    
    phone_number_regex = RegexValidator(regex=r'^[0-9]+$', message = ("ハイフンなしの10桁又は11桁で入力してください"))
    phone_number = models.CharField(verbose_name="電話番号", validators=[phone_number_regex], max_length=11, null=False, blank=False)
    
    basic = models.BooleanField(verbose_name="システムの有料版の申込み", default=False)
    option1 = models.BooleanField(verbose_name="戸籍取得代行の申込み", default=False)
    option2 = models.BooleanField(verbose_name="司法書士紹介の申込み", default=False)
    is_phone_required = models.BooleanField(verbose_name="電話による連絡を希望", default=False)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name = "作成者",
        on_delete = models.CASCADE,
        null = False,
        blank = False,
        related_name = "option_request_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name = "最終更新者",
        on_delete = models.CASCADE,
        null = False,
        blank = False,
        related_name = "option_request_update_by"
    )
    
    fields =[
        "name",
        "payer",
        "address",
        "phone_number",
        "basic",
        "option1",
        "option2",
        "is_phone_required",
    ]
    
    class Meta:
        verbose_name = _("オプション利用申請")
        verbose_name_plural = _("オプション利用申請")

class EmailChange(models.Model):
    """メールアドレス変更申請データ

    Args:
        models (_type_): _description_
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="ユーザー",
        on_delete=models.CASCADE,
        null = False,
        blank = False,
        related_name="EmailChange",
    )
    
    email = models.EmailField(verbose_name="変更後のメールアドレス", unique=True)
    token = models.CharField(verbose_name="トークン", max_length=100, unique=True)
    created_at = models.DateTimeField(verbose_name="作成日", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="最終更新日", auto_now=True)
    
    fields =["email", "user", "token"]
    
    class Meta:
        verbose_name = _("メールアドレス変更申請")
        verbose_name_plural = _("メールアドレス変更申請")