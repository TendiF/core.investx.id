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
from enterprise.libs.payment.wallet import *

from core.structures.account.models import Company
from enterprise.libs import storage

from core.libs import constant


class CompanyCampaign(BaseModelGeneric):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, blank=True, null=True)
    status = models.PositiveIntegerField(
        choices=constant.CAMPAIGN_STATUS_CHOICES, default=1)
    started = models.DateTimeField(db_index=True)
    time_limit = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.company.name

    class Meta:
        verbose_name = _("Company Campaign")
        verbose_name_plural = _("Company Campaigns")


class Investment(BaseModelGeneric):
    campaign = models.ForeignKey(CompanyCampaign, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField(blank=True, null=True)
    dividend = models.IntegerField(blank=True, null=True, default=0)

    def __init__(self, campaign, user, amount, *args, **kwargs):
        super().__init__(*args, **kwargs)

        deduct_wallet(
            user=user,
            amount=amount
        )

        self.campaign = campaign
        self.user = user
        self.amount = amount

    def __str__(self):
        return f"{self.created_by}: {self.campaign}"

    class Meta:
        verbose_name = _("Investment")
        verbose_name_plural = _("Investments")