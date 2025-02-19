# Generated by Django 4.1 on 2024-08-10 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_alter_ticket_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClosedTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('batiments', 'Bâtiments'), ('electricite', 'Electricité'), ('electricite_balisage', 'Electricité balisage'), ('electromecanique', 'Electromécanique'), ('electronique', 'Electronique'), ('electrothermie', 'Electrothermie'), ('exploitation', 'Exploitation'), ('gestion_dechets', 'Gestion des déchets'), ('informatique', 'Informatique'), ('infrastructures', 'Infrastructures'), ('radar_detection', 'Radar Détection'), ('radiocom', 'RadioComm'), ('radionav', 'RadioNav'), ('telecommunications', 'Télécommunications'), ('telecoms', 'Télécoms'), ('ti', 'TI'), ('equipements', 'Tous les équipements'), ('traitement_plan_vol', 'Traitement et plan de vol')], default='electricite', max_length=100)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('status', models.CharField(choices=[('unaffected', 'Unaffected'), ('Affected', 'Affected'), ('declared_fixed', 'Declared Fixed'), ('closed', 'Closed')], default='unaffected', max_length=50)),
                ('priority', models.CharField(choices=[('medium', 'Moyenne'), ('high', 'Haute')], default='low', max_length=10)),
                ('airport', models.CharField(default='Unknown', max_length=100)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
