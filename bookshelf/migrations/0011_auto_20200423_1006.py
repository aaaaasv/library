# Generated by Django 3.0.3 on 2020-04-23 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookshelf', '0010_auto_20200413_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='status',
            field=models.CharField(choices=[('A', 'Available'), ('N', 'Not available')], default='A', max_length=1),
        ),
    ]
