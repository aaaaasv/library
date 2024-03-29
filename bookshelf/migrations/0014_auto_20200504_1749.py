# Generated by Django 3.0.3 on 2020-05-04 14:49

from django.conf import settings
from django.db import migrations
import sortedm2m.fields
from sortedm2m.operations import AlterSortedManyToManyField

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bookshelf', '0013_auto_20200502_1159'),
    ]

    operations = [
        AlterSortedManyToManyField(
            model_name='paperbook',
            name='reserver',
            field=sortedm2m.fields.SortedManyToManyField(blank=True, help_text=None, related_name='reserverOfBook', to=settings.AUTH_USER_MODEL),
        ),
    ]
