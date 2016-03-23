# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-23 19:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_order_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='count',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
