from django.utils import timezone
import uuid
from django.contrib.auth.models import AbstractUser,AbstractBaseUser,PermissionsMixin
from django.db import models
from django.contrib.auth.models import User,BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.contrib.auth.models import  UserManager
import PIL

    




class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CustomUserManager(UserManager):
    def _create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser,PermissionsMixin):
    choices=[
        ("AGENT", "agent"),
        ("TECHNICIAN", "technician"),
        ("SUPERVISOR", "supervisor"),
        ("ADMIN", "admin"),
        ("SUPERVISOR_ADMIN", "supervisor_admin"),
    ]
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    function = models.CharField(max_length=255,choices=[
        ("AGENT", "agent"),
        ("TECHNICIAN", "technician"),
        ("SUPERVISOR", "supervisor"),
        ("ADMIN", "admin"),
        ("SUPERADMIN", "superadmin")
    ],default="AGENT")
    date_joined = models.DateTimeField(default=timezone.now)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural='users'


    def __str__(self):
        return self.email

class Agent(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,null=True,blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricule = models.CharField(max_length=255)
    cin = models.CharField(max_length=15)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.IntegerField()
    phone = PhoneNumberField(blank=True)
    image = models.ImageField(upload_to='Agent_images/',null=True,blank=True)




    def __str__(self):
        return self.nom


class Technician(Agent):
    choices = [
        ('batiments', 'Bâtiments'),
        ('electricite', 'Electricité'),
        ('electricite_balisage', 'Electricité balisage'),
        ('electromecanique', 'Electromécanique'),
        ('electronique', 'Electronique'),
        ('electrothermie', 'Electrothermie'),
        ('exploitation', 'Exploitation'),
        ('gestion_dechets', 'Gestion des déchets'),
        ('informatique', 'Informatique'),
        ('infrastructures', 'Infrastructures'),
        ('radar_detection', 'Radar Détection'),
        ('radiocom', 'RadioComm'),
        ('radionav', 'RadioNav'),
        ('telecommunications', 'Télécommunications'),
        ('telecoms', 'Télécoms'),
        ('ti', 'TI'),
        ('equipements', 'Tous les équipements'),
        ('traitement_plan_vol', 'Traitement et plan de vol'),
    ]
    profession = models.CharField(max_length=100, choices=choices)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.nom



class Supervisor(Technician):

    def __str__(self):
        return self.nom

# Ticket Model
class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
    ]

    STATUS_CHOICES = [
        ('unaffected', 'Unaffected'),
        ('Affected', 'Affected'),
        ('declared_fixed', 'Declared Fixed'),
        ('closed', 'Closed'),
    ]


    ROLE_CHOICES = [
        ('batiments', 'Bâtiments'),
        ('electricite', 'Electricité'),
        ('electricite_balisage', 'Electricité balisage'),
        ('electromecanique', 'Electromécanique'),
        ('electronique', 'Electronique'),
        ('electrothermie', 'Electrothermie'),
        ('exploitation', 'Exploitation'),
        ('gestion_dechets', 'Gestion des déchets'),
        ('informatique', 'Informatique'),
        ('infrastructures', 'Infrastructures'),
        ('radar_detection', 'Radar Détection'),
        ('radiocom', 'RadioComm'),
        ('radionav', 'RadioNav'),
        ('telecommunications', 'Télécommunications'),
        ('telecoms', 'Télécoms'),
        ('ti', 'TI'),
        ('equipements', 'Tous les équipements'),
        ('traitement_plan_vol', 'Traitement et plan de vol'),
    ]

    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='electricite')
    description = models.TextField()
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unaffected')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    airport = models.CharField(max_length=100, default='Unknown')
    creationDate = models.DateTimeField(auto_now_add=True)
    date_validated = models.DateTimeField(null=True, blank=True)  # When the ticket is validated
    date_closed = models.DateTimeField(null=True, blank=True)  # When the ticket is closed
    validated_by = models.ForeignKey(Technician, related_name='validated_tickets', on_delete=models.SET_NULL, null=True, blank=True)
    closed_by = models.ForeignKey(Supervisor, related_name='closed_tickets', on_delete=models.SET_NULL, null=True, blank=True)

    def _str_(self):
        return f"{self.role} - {self.location}"


class ClosedTicket(models.Model):
    PRIORITY_CHOICES = [
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
    ]

    STATUS_CHOICES = [
        ('closed', 'Closed'),
    ]

    ROLE_CHOICES = [
        ('batiments', 'Bâtiments'),
        ('electricite', 'Electricité'),
        ('electricite_balisage', 'Electricité balisage'),
        ('electromecanique', 'Electromécanique'),
        ('electronique', 'Electronique'),
        ('electrothermie', 'Electrothermie'),
        ('exploitation', 'Exploitation'),
        ('gestion_dechets', 'Gestion des déchets'),
        ('informatique', 'Informatique'),
        ('infrastructures', 'Infrastructures'),
        ('radar_detection', 'Radar Détection'),
        ('radiocom', 'RadioComm'),
        ('radionav', 'RadioNav'),
        ('telecommunications', 'Télécommunications'),
        ('telecoms', 'Télécoms'),
        ('ti', 'TI'),
        ('equipements', 'Tous les équipements'),
        ('traitement_plan_vol', 'Traitement et plan de vol'),
    ]

    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='electricite')
    description = models.TextField()
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unaffected')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    airport = models.CharField(max_length=100, default='Unknown')
    creationDate = models.DateTimeField(auto_now_add=True)
    date_validated = models.DateTimeField(null=True, blank=True)
    date_closed = models.DateTimeField(null=True, blank=True)

    validated_by = models.ForeignKey(Technician, related_name='closed_validated_tickets', on_delete=models.SET_NULL, null=True, blank=True)
    closed_by = models.ForeignKey(Supervisor, related_name='closed_closed_tickets', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.role} - {self.location}"



class Admin (models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,null=True,blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricule = models.CharField(max_length=255,default="default")
    cin = models.CharField(max_length=15)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.IntegerField()
    phone = PhoneNumberField(blank=True)
    image = models.ImageField(upload_to='Agent_images/',null=True,blank=True)

class Superuser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,null=True,blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricule = models.CharField(max_length=255,default="default")
    cin = models.CharField(max_length=15)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    age = models.IntegerField()
    phone = PhoneNumberField(blank=True)
    image = models.ImageField(upload_to='Agent_images/',null=True,blank=True)