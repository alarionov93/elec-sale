# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-24 12:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_orderitem_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='in_stock',
            new_name='count',
        ),
    ]