# Generated by Django 3.1 on 2020-09-02 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20200901_2314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbookrelation',
            name='rate',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Ok'), (2, 'Fine'), (3, 'Good'), (4, 'Amazing'), (5, 'Incredible')], null=True),
        ),
    ]
