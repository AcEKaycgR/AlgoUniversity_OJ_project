# Generated by Django 5.2.4 on 2025-07-22 07:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compiler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='constraints',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='question',
            name='cpp_starter',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='question',
            name='explanation',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='question',
            name='follow_up',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='question',
            name='java_starter',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='question',
            name='python_starter',
            field=models.TextField(default='class Solution:\n    def solve(self):\n        pass'),
        ),
        migrations.AddField(
            model_name='testcase',
            name='is_example',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_data', models.TextField()),
                ('output_data', models.TextField()),
                ('explanation', models.TextField(blank=True)),
                ('order', models.IntegerField(default=1)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examples', to='compiler.question')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
