from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from phonenumber_field.formfields import PhoneNumberField
from django.forms import inlineformset_factory,BaseFormSet
from django.contrib.auth import authenticate

# forms.py



class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name']  # Inclure uniquement le champ 'name'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'emplacement'})
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']




class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['role', 'location', 'priority', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'priority': forms.Select(choices=Ticket.PRIORITY_CHOICES),
            'role': forms.Select(choices=Ticket.ROLE_CHOICES)}
from django import forms

from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Mot de passe'
        })
    )




class AdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [ 'email', 'password']

class SuperAdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [ 'email', 'password']

class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']

class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
            form.use_required_attribute = True


AgentFormSet = inlineformset_factory(CustomUser,Agent,fields=['matricule','cin','nom','prenom','age','phone','image'])
TechnicianFormSet = inlineformset_factory(CustomUser,Technician,fields=['matricule','cin','nom','prenom','age','phone', 'profession','image'])
SupervisorFormSet = inlineformset_factory(CustomUser,Supervisor,fields=['matricule','cin','nom','prenom','age','phone', 'profession','image'])
AdminFormSet = inlineformset_factory(CustomUser,Admin,fields=['matricule','cin','nom','prenom','age','phone','image'])
SuperAdminFormSet = inlineformset_factory(CustomUser,Superuser,fields=['matricule','cin','nom','prenom','age','phone','image'])
