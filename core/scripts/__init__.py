'''
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# File: __init__.py
# Project: core.bimaasia.id
# File Created: Tuesday, 18th June 2019 3:24:59 pm
# 
# Author: Arif Dzikrullah
#         ardzix@hotmail.com>
#         https://github.com/ardzix/>
# 
# Last Modified: Tuesday, 18th June 2019 3:25:00 pm
# Modified By: arifdzikrullah (ardzix@hotmail.com>)
# 
# Handcrafted and Made with Love - Ardz
# Copyright - 2019 PT Bima Kapital Asia Teknologi, bimaasia.id
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''

from core.scripts.administrative import *
# from core.scripts.agreement import *
# from core.scripts.numbering import *
# import_provices()
# import_regencies()


def import_bank():
    from enterprise.libs.pay_constants import BANK_CHOICES
    from enterprise.structures.authentication.models import User
    from slugify import slugify

    user, created = User.objects.get_or_create(
        full_name='Admin',
        email='admin@investx.id',
        phone_number='6281111'
    )
    for b in BANK_CHOICES:
        display_name = b[1]
        short_name = slugify(display_name)
        code = b[0]
        Bank.objects.get_or_create(
            display_name=display_name,
            short_name=short_name,
            code=code,
            created_by=user
        )
