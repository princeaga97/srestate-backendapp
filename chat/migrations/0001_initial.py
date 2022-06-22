# Generated by Django 3.0 on 2022-06-22 10:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('sender_name', models.TextField()),
                ('receiver_name', models.TextField()),
                ('time', models.TimeField(auto_now_add=True)),
                ('sent', models.BooleanField(default=False)),
                ('seen', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
        migrations.CreateModel(
            name='Contacts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact', models.TextField()),
                ('owner', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='latest_msg', to='chat.Messages')),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
    ]