# Generated by Django 4.0.4 on 2022-04-29 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_product_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=400)),
                ('email', models.EmailField(max_length=400)),
                ('message', models.TextField()),
            ],
        ),
    ]
