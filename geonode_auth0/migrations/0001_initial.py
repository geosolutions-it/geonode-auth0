# Generated by Django 2.2.16 on 2021-03-15 13:51

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('social_django', '0010_uid_db_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomPrivilegeUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('social_django.usersocialauth',),
        ),
    ]
