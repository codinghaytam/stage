# Generated by Django 4.1 on 2024-08-10 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_agent_matricule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.CharField(choices=[('unaffected', 'Unaffected'), ('Affected', 'Affected'), ('declared_fixed', 'Declared Fixed'), ('closed', 'Closed')], default='open', max_length=50),
        ),
    ]
