# Generated by Django 3.1.5 on 2021-10-24 07:55

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Designates whether this item should be treated as active. Unselected this instead of deleting.', verbose_name='Active status')),
                ('created_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation On')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='Modified On')),
                ('imdb_id', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=30)),
                ('photo', models.URLField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_time', '-updated_time'],
                'abstract': False,
            },
            managers=[
                ('active_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Film',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Designates whether this item should be treated as active. Unselected this instead of deleting.', verbose_name='Active status')),
                ('created_time', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation On')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='Modified On')),
                ('imdb_id', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('plot', models.TextField(blank=True, null=True)),
                ('content_rating', models.CharField(blank=True, max_length=5, null=True)),
                ('genres', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=20), blank=True, null=True, size=None)),
                ('countries', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=20), blank=True, null=True, size=None)),
                ('languages', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=20), blank=True, null=True, size=None)),
                ('photo', models.URLField(blank=True, null=True)),
                ('banner', models.URLField(blank=True, null=True)),
                ('trailer', models.URLField(blank=True, null=True)),
                ('year', models.IntegerField()),
                ('imdb', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(10.0)])),
                ('rotten', models.IntegerField(blank=True, null=True)),
                ('metacritic', models.IntegerField(blank=True, null=True)),
                ('time', models.IntegerField(blank=True, help_text='Film length based on minutes', null=True)),
                ('actors', models.ManyToManyField(related_name='acted_films', to='film.Artist')),
                ('directors', models.ManyToManyField(related_name='directed_films', to='film.Artist')),
                ('writers', models.ManyToManyField(related_name='wrote_films', to='film.Artist')),
            ],
            options={
                'ordering': ['-created_time', '-updated_time'],
                'abstract': False,
            },
            managers=[
                ('active_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]
