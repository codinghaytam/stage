# Generated by Django 5.0.6 on 2024-08-08 15:17

import django.db.models.deletion
import django.utils.timezone
import myapp.models
import phonenumber_field.modelfields
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('matricule', models.CharField(default='default', max_length=255)),
                ('cin', models.CharField(max_length=15)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('image', models.ImageField(blank=True, null=True, upload_to='Agent_images/')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('batiments', 'Bâtiments'), ('electricite', 'Electricité'), ('electricite_balisage', 'Electricité balisage'), ('electromecanique', 'Electromécanique'), ('electronique', 'Electronique'), ('electrothermie', 'Electrothermie'), ('exploitation', 'Exploitation'), ('gestion_dechets', 'Gestion des déchets'), ('informatique', 'Informatique'), ('infrastructures', 'Infrastructures'), ('radar_detection', 'Radar Détection'), ('radiocom', 'RadioComm'), ('radionav', 'RadioNav'), ('telecommunications', 'Télécommunications'), ('telecoms', 'Télécoms'), ('ti', 'TI'), ('equipements', 'Tous les équipements'), ('traitement_plan_vol', 'Traitement et plan de vol')], default='electricite', max_length=100)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('status', models.CharField(choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('closed', 'Closed')], default='open', max_length=50)),
                ('priority', models.CharField(choices=[('low', 'Faible'), ('high', 'Haute')], default='low', max_length=10)),
                ('airport', models.CharField(default='Unknown', max_length=100)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('function', models.CharField(choices=[('AGENT', 'agent'), ('TECHNICIAN', 'technician'), ('SUPERVISOR', 'supervisor'), ('ADMIN', 'admin'), ('SUPERADMIN', 'superadmin')], default='AGENT', max_length=255)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', myapp.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('matricule', models.CharField(default='default', max_length=255)),
                ('cin', models.CharField(max_length=15)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('image', models.ImageField(blank=True, null=True, upload_to='Agent_images/')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Technician',
            fields=[
                ('agent_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='myapp.agent')),
                ('profession', models.CharField(choices=[('ECTRICIAN', 'electrician'), ('DOCTOR', 'doctor')], max_length=100)),
                ('score', models.IntegerField(default=0)),
            ],
            bases=('myapp.agent',),
        ),
        migrations.AddField(
            model_name='agent',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Superuser',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('matricule', models.CharField(default='default', max_length=255)),
                ('cin', models.CharField(max_length=15)),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('image', models.ImageField(blank=True, null=True, upload_to='Agent_images/')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Supervisor',
            fields=[
                ('technician_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='myapp.technician')),
            ],
            bases=('myapp.technician',),
        ),
    ]
