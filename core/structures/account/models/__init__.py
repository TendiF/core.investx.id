from random import randint
from datetime import date
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.gis.db import models as geo
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from enterprise.structures.common.models import File
from enterprise.structures.common.models.base import BaseModelGeneric, BaseModelUnique
from enterprise.structures.authentication.models import User, EmailVerification
from enterprise.structures.transaction.models import BankAccount
from enterprise.libs import storage

from core.libs import constant

User = settings.AUTH_USER_MODEL


class Province(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Province')
        verbose_name_plural = _('Provinces')


class Regency(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Regency')
        verbose_name_plural = _('Regencies')


class Address(BaseModelGeneric):
    name = models.CharField(max_length=255)
    address = models.TextField()
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=3, choices=constant.COUNTRY_CHOICES,
                               default='IDN')
    timezone = models.CharField(max_length=48, blank=True, null=True)
    point = geo.PointField(blank=True, null=True)
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, blank=True, null=True)
    regency = models.ForeignKey(
        Regency, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')


class Phone(BaseModelGeneric):
    name = models.CharField(max_length=20, default="Default")
    number = models.CharField(max_length=20)
    country = models.CharField(
        max_length=3,
        choices=constant.COUNTRY_CHOICES,
        default='IDN')
    is_available = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        return super(Phone, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Phone')
        verbose_name_plural = _('Phones')


class Profile(BaseModelUnique):
    nick_name = models.CharField(_('nick name'), max_length=150, blank=True, null=True)
    avatar = models.FileField(
        max_length=300,
        storage=storage.FILE_STORAGE,
        blank=True,
        null=True
    )
    background_cover = models.FileField(
        max_length=300,
        storage=storage.FILE_STORAGE,
        blank=True,
        null=True
    )
    gender = models.PositiveIntegerField(choices=constant.GENDER_CHOICES,
                                         default=1)
    birth_date = models.DateField(blank=True, null=True)
    marital_status = models.PositiveIntegerField(
        choices=constant.MARITAL_STATUS_CHOICES, default=1)
    citizenship = models.PositiveIntegerField(
        choices=constant.CITIZENSHIP_CHOICES, default=1)
    background_story = models.TextField(blank=True, null=True)
    phones = models.ManyToManyField(Phone, blank=True)
    addresses = models.ManyToManyField(Address, blank=True)

    # EDUCATION & PROFESSION
    last_education = models.PositiveIntegerField(
        choices=constant.LAST_EDUCATION_CHOICES, default=2)
    profession = models.PositiveIntegerField(
        choices=constant.PROFESSION_CHOICES, default=5)
    job_industry = models.PositiveIntegerField(
        choices=constant.JOB_INDUSTRY_CHOICES, default=2)
    monthly_salary = models.PositiveIntegerField(  # CONSTANT NOT COMPLETED YET
        choices=constant.MONTHLY_SALARY_CHOICES, default=2)
    income_source = models.PositiveIntegerField(
        choices=constant.INCOME_SOURCE_CHOICES, default=2)

    # DOCUMENTS
    id_card_num = models.CharField(max_length=40, blank=True, null=True)
    npwp_num = models.CharField(max_length=40, blank=True, null=True)
    id_card = models.FileField(
        max_length=300,
        storage=storage.FILE_STORAGE,
        blank=True,
        null=True
    )
    id_card_selfie = models.FileField(
        max_length=300,
        storage=storage.FILE_STORAGE,
        blank=True,
        null=True
    )
    npwp = models.FileField(
        max_length=300,
        storage=storage.FILE_STORAGE,
        blank=True,
        null=True
    )

    # BANK
    bank_accounts = models.ManyToManyField(BankAccount, blank=True)

    # PREFERENCE
    budget_preference = models.PositiveIntegerField(
        choices=constant.BUDGET_PREFERENCE_CHOICES, default=1)
    risk_preference = models.PositiveIntegerField(
        choices=constant.RISK_PREFERENCE_CHOICES, default=2)
    information_source = models.PositiveIntegerField(
        choices=constant.INFORMATION_SOURCE_CHOICES, default=1)

    def __str__(self):
        return self.owned_by.nick_name

    def get_id_card(self):
        if self.id_card:
            return self.id_card.url
        else:
            return '-'

    def get_id_card_selfie(self):
        if self.id_card:
            return self.id_card_selfie.url
        else:
            return '-'

    def get_gender(self):
        return dict(constant.GENDER_CHOICES)[self.gender]

    def get_type(self):
        return dict(constant.PROFILE_TYPE_CHOICES)[self.type]

    def get_number(self, *args, **kwargs):
        return str(self.pk).zfill(5)

    def get_age(self, *args, **kwargs):
        today = date.today()
        return today.year - self.birth_date.year

    def get_total_topup(self):
        from enterprise.structures.transaction.models import TopUp
        total_topup = TopUp.objects.filter(
            created_by_id=self.created_by_id,
            status='success'
        ).aggregate(
            models.Sum('amount')
        )['amount__sum']
        if total_topup:
            return 'Rp.{:,.0f},-'.format(int(total_topup))
        else:
            return 'Rp.{:,.0f},-'.format(0)

    def get_cash_balance(self):
        from enterprise.structures.transaction.models import Wallet
        cash_balance = Wallet.objects.filter(
            created_by_id=self.created_by_id
        ).aggregate(
            models.Sum('amount')
        )['amount__sum']
        if cash_balance:
            return 'Rp.{:,.0f},-'.format(int(cash_balance))
        else:
            return 'Rp.{:,.0f},-'.format(0)

    def get_total_withdraw(self):
        from enterprise.structures.transaction.models import Withdraw
        total_withdraw = Withdraw.objects.filter(
            created_by_id=self.created_by_id
        ).aggregate(
            models.Sum('amount')
        )['amount__sum']
        if total_withdraw:
            return 'Rp.{:,.0f},-'.format(int(total_withdraw))
        else:
            return 'Rp.{:,.0f},-'.format(0)


class Company(BaseModelGeneric):
    # General
    name = models.CharField(max_length=150, blank=True, null=True)
    trademark = models.CharField(max_length=150, blank=True, null=True)
    business_type = models.PositiveIntegerField(
        choices=constant.BUSINESS_TYPE_CHOICES, default=1)
    business_subtype = models.CharField(max_length=150, blank=True, null=True)
    city = models.CharField(max_length=150, blank=True, null=True)
    addresses = models.ManyToManyField(Address, blank=True)
    company_age = models.IntegerField(blank=True, null=True)
    number_of_branches = models.IntegerField(blank=True, null=True)
    number_of_employees = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Financial
    investment_needed = models.IntegerField(blank=True, null=True)
    average_monthly_turnover = models.IntegerField(blank=True, null=True)
    average_monthly_profit = models.IntegerField(blank=True, null=True)
    average_monthly_turnover_last_year = models.IntegerField(blank=True, null=True)
    average_monthly_profit_last_year = models.IntegerField(blank=True, null=True)
    total_debt = models.IntegerField(blank=True, null=True)
    bank_account = models.ManyToManyField(BankAccount, blank=True)
    paid_up_capital = models.IntegerField(blank=True, null=True)
    book_value_per_share = models.IntegerField(blank=True, null=True)

    # Non financial
    financial_data_collection_system = models.PositiveIntegerField(
        choices=constant.DATA_COLLECTION_SYSTEM_CHOICES, default=1)
    credit_reputation = models.PositiveIntegerField(
        choices=constant.LOAN_REPUTATION_CHOICES, default=1)
    market_position = models.PositiveIntegerField(
        choices=constant.MARKET_POSITION_CHOICES, default=1)
    future_strategy = models.PositiveIntegerField(
        choices=constant.FUTURE_STRATEGY_CHOICES, default=1)
    location_status = models.PositiveIntegerField(
        choices=constant.LOCATION_STATUS_CHOICES, default=1)
    competition_level = models.PositiveIntegerField(
        choices=constant.COMPETITION_LEVEL_CHOICES, default=1)
    managerial_skill = models.PositiveIntegerField(
        choices=constant.MANAGERIAL_SKILL_CHOICES, default=1)
    technical_skill = models.PositiveIntegerField(
        choices=constant.TECHNICAL_SKILL_CHOICES, default=1)

    # Media
    operational_photo = models.FileField(
        max_length=300,
        storage=storage.FILE_STORAGE,
        blank=True,
        null=True
    )
    video_url = models.URLField(blank=True, null=True)

    # Campaign
    status = models.PositiveIntegerField(
        choices=constant.COMPANY_STATUS_CHOICES, default=1)
    time_limit = models.PositiveIntegerField(default=60, null=True, blank=True)

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')


class ProfileDetail(BaseModelGeneric):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    body = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Profile Detail')
        verbose_name_plural = _('Profile Details')


class CompanyDetail(BaseModelGeneric):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    body = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Company Detail')
        verbose_name_plural = _('Company Details')


class Favorite(BaseModelGeneric):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.company.name

    class Meta:
        verbose_name = _('Favorite')
        verbose_name_plural = _('Favorites')
