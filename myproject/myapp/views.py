from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from .models import *
import json
from .utils import is_ajax
from .forms import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib import messages
User = get_user_model()
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
import os
from django.db.models.functions import TruncDate
# views.py
from django.shortcuts import render, redirect
from .models import Category
from .forms import CategoryForm


from django.shortcuts import render
from .models import Ticket, Technician, Supervisor
from django.db.models import Count



from django.shortcuts import render
from django.db.models import Count
from .models import Ticket, Location, Category, Agent, Admin, Superuser

def dashboard(request):
    # Récupération des filtres depuis les paramètres de la requête
    selected_category = request.GET.get('category')
    selected_location = request.GET.get('location')

    # Statistiques des emplacements, catégories, et employés
    num_locations = Location.objects.count()
    num_categories = Category.objects.count()
    num_employees = Agent.objects.count() + Admin.objects.count() + Superuser.objects.count()

    # Filtrer les tickets selon les filtres sélectionnés
    tickets = Ticket.objects.all()
    if selected_category:
        tickets = tickets.filter(role=selected_category)
    if selected_location:
        tickets = tickets.filter(location=selected_location)  # Assurez-vous que vous avez un champ pour location dans Ticket

    # Statistiques des tickets
    total_tickets = tickets.count()
    open_tickets = tickets.filter(status='unaffected').count()
    
    # Données pour les graphiques
    tickets_per_category = tickets.values('role').annotate(count=Count('id'))
    tickets_per_priority = tickets.values('priority').annotate(count=Count('id')).order_by('-priority')
    
    # Contexte pour le template
    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'num_locations': num_locations,
        'num_categories': num_categories,
        'num_employees': num_employees,
        'tickets_per_category': tickets_per_category,
        'tickets_per_priority': tickets_per_priority,
        'categories': Category.objects.all(),  # Pour le filtre de catégorie
        'locations': Location.objects.all(),  # Pour le filtre d'emplacement
        'selected_category': selected_category,
        'selected_location': selected_location,
    }
    
    return render(request, 'admin/dashboard.html', context)










@login_required
def location_list(request):
    query = request.GET.get('search', '')
    locations = Location.objects.filter(name__icontains=query)
    
    if request.method == 'POST':
        if 'add' in request.POST:
            form = LocationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Emplacement ajouté avec succès.')
                return redirect('location_list')
        elif 'delete' in request.POST:
            location_id = request.POST.get('delete')
            location = get_object_or_404(Location, id=location_id)
            location.delete()
            messages.success(request, 'Emplacement supprimé avec succès.')
            return redirect('location_list')
    else:
        form = LocationForm()

    # Vérifiez si l'utilisateur est dans le groupe ADMIN
    is_admin = request.user.groups.filter(name='ADMIN').exists()

    # Si l'utilisateur est ADMIN, incluez les catégories dans le contexte
    context = {
        'locations': locations,
        'form': form,
        'is_admin': is_admin,  # Passez cette variable au template
    }
    
    return render(request, 'admin/location_list.html', context)



def category_list(request):
    categories = Category.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        categories = categories.filter(name__icontains=search_query)
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            category_id = request.POST.get('delete')
            Category.objects.filter(id=category_id).delete()
            return redirect('category_list')
        elif 'add' in request.POST:
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('category_list')
    
    return render(request, 'admin/category_list.html', {
        'categories': categories,
        'form': CategoryForm(),
        'search_query': search_query
    })



def index(request):
    return redirect("login")


def about(request):
    return render(request,'myapp/about.html')

def service(request):
    return render(request,'myapp/service.html')

def contact(request):
    return render(request,'myapp/contact.html')


# Custom decorator to check if the user is a technician
def is_technician(user):
    return hasattr(user, 'Technician')


# Custom decorator to check if the user is a supervisor
def is_supervisor(user):
    return hasattr(user, 'Supervisor')


def is_administrator(user):
    return user.is_staff


def is_agent(user):
    return hasattr(user, 'Agent')


def is_superadmin(user):
    return user.is_superuser


@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ticket_list')
        else:
            return HttpResponse(form.errors)
    else:
        form = TicketForm()
    return render(request, 'myapp/create_ticket.html', {'form': form})


@login_required
def ticket_list(request):
    user = request.user  # Get the currently logged-in user

    # Determine the full name, function (rank), and profession (role) based on user type
    full_name = f"{user.agent.prenom} {user.agent.nom}" if hasattr(user, 'agent') else "Unknown"
    rank = user.function  # This will be 'TECHNICIAN', 'SUPERVISOR', etc.
    role = None

    # Initialize tickets as an empty queryset
    tickets = Ticket.objects.none()

    if user.function == "TECHNICIAN":
        # Get the Technician object associated with the user
        try:
            technician = Technician.objects.get(user=user)
            role = technician.profession
            # Filter tickets by the technician's profession (role)
            tickets = Ticket.objects.filter(role=technician.profession)
        except Technician.DoesNotExist:
            return HttpResponseForbidden("You are not authorized to view this page.")

    elif user.function in ["SUPERVISOR", "ADMIN", "SUPERADMIN"]:
        # Supervisors, Admins, and Superadmins can see all tickets
        tickets = Ticket.objects.all()
        # Assuming these users may have associated roles as well
        if hasattr(user, 'supervisor'):
            role = user.supervisor.profession
        elif hasattr(user, 'admin'):
            role = "Admin"  # You can customize this if Admin has a specific profession

    # Handle search parameters
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    description = request.GET.get('description', '')

    if status:
        tickets = tickets.filter(status=status)
    if category:
        tickets = tickets.filter(role=category)
    if description:
        tickets = tickets.filter(description__icontains=description)

    # Get role choices for the category dropdown
    ticket_role_choices = Ticket.ROLE_CHOICES

    context = {
        'tickets': tickets,
        'full_name': full_name,
        'rank': rank,
        'role': role,
        'can_validate': lambda ticket: user.function == "TECHNICIAN" and ticket.status == "unaffected",
        'can_close': lambda ticket: user.function in ["SUPERVISOR", "ADMIN", "SUPERADMIN"] and ticket.status == "declared_fixed",
        'ticket_role_choices': ticket_role_choices,  # Add this line
    }

    return render(request, 'myapp/ticket_list.html', context)

@login_required
def ticket_details(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
        data = {
            'role': ticket.get_role_display(),
            'description': ticket.description,
            'location': ticket.location,
            'priority': ticket.get_priority_display(),
            'status': ticket.get_status_display(),
            'creationDate': ticket.creationDate.strftime('%Y-%m-%d %H:%M:%S'),
            'image': ticket.image.url if ticket.image else None,
        }
        return JsonResponse(data)
    except Ticket.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)


@login_required
def closedticket_details(request, ticket_id):
    try:
        closed_ticket = ClosedTicket.objects.select_related('validated_by', 'closed_by').get(id=ticket_id)

        data = {
            'role': closed_ticket.get_role_display(),
            'description': closed_ticket.description,
            'location': closed_ticket.location,
            'priority': closed_ticket.get_priority_display(),
            'status': closed_ticket.get_status_display(),
            'creationDate': closed_ticket.creationDate.strftime('%Y-%m-%d %H:%M:%S'),
            'dateValidated': closed_ticket.date_validated.strftime('%Y-%m-%d %H:%M:%S') if closed_ticket.date_validated else 'Not validated',
            'validatedBy': f"{closed_ticket.validated_by.nom} {closed_ticket.validated_by.prenom}" if closed_ticket.validated_by else 'N/A',  # Technician's full name
            'dateClosed': closed_ticket.date_closed.strftime('%Y-%m-%d %H:%M:%S') if closed_ticket.date_closed else 'Not closed',
            'closedBy': f"{closed_ticket.closed_by.nom} {closed_ticket.closed_by.prenom}" if closed_ticket.closed_by else 'N/A',  # Supervisor's full name
            'image': closed_ticket.image.url if closed_ticket.image else None,
        }
        return JsonResponse(data)
    except ClosedTicket.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)

@login_required
def validate_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        if request.user.function == "TECHNICIAN" and ticket.status == "unaffected":
            ticket.status = 'declared_fixed'
            ticket.date_validated = timezone.now()  # Set the validation date
            ticket.save()
            return redirect('ticket_list')
        else:
            return HttpResponseForbidden("You are not authorized to perform this action.")
    else:
        return HttpResponseForbidden("Invalid request method.")


@login_required
def assign_ticket(request, ticket_id):
    """Assign a ticket to a technician."""
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.status != 'unaffected':
        return HttpResponseForbidden("This ticket cannot be reassigned.")

    if request.method == 'POST':
        technician_id = request.POST.get('technician')
        technician = get_object_or_404(Technician, id=technician_id)
        ticket.assigned_to = technician
        ticket.status = 'Affected'  # Update status to 'Affected'
        ticket.save()
        return redirect('ticket_list')

    technicians = Technician.objects.all()
    return render(request, 'myapp/assign_ticket.html', {'ticket': ticket, 'technicians': technicians})

@login_required
@require_POST
def close_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.user.function not in ["SUPERVISOR", "ADMIN", "SUPERADMIN"]:
        return JsonResponse({"status": "error", "message": "You are not authorized to perform this action."}, status=403)

    if ticket.status != 'declared_fixed':
        return JsonResponse({"status": "error", "message": "This ticket cannot be closed."}, status=403)

    try:
        supervisor = Supervisor.objects.get(user=request.user)

        closed_ticket = ClosedTicket(
            role=ticket.role,
            description=ticket.description,
            location=ticket.location,
            priority=ticket.priority,
            status='closed',
            creationDate=ticket.creationDate,
            date_validated=ticket.date_validated,
            date_closed=timezone.now(),
            image=ticket.image,
            validated_by=ticket.validated_by,
            closed_by=supervisor
        )
        closed_ticket.save()
        ticket.delete()

        return JsonResponse({"status": "success"})
    except Supervisor.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Supervisor not found."}, status=500)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@require_POST
def return_to_unaffected(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Check if the user is authorized
    if request.user.function not in ["SUPERVISOR", "ADMIN", "SUPERADMIN"]:
        return JsonResponse({"status": "error", "message": "You are not authorized to perform this action."}, status=403)

    # Check if the ticket is in a state that can be returned to unaffected
    if ticket.status != 'declared_fixed':
        return JsonResponse({"status": "error", "message": "This ticket cannot be returned to unaffected."}, status=403)

    try:
        supervisor = Supervisor.objects.get(user=request.user)

        # Update ticket status
        ticket.status = 'unaffected'
        ticket.date_validated = None  # Optionally reset the validation date
        ticket.save()

        return JsonResponse({"status": "success"})
    except Supervisor.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Supervisor not found."}, status=500)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def is_superuser_or_admin(user):
    return user.is_superuser or user.function in ['ADMIN', 'SUPERADMIN']

@user_passes_test(is_superuser_or_admin)
def closed_tickets_list(request):
    tickets = ClosedTicket.objects.all()
    return render(request, 'closed_tickets_list.html', {'tickets': tickets})

@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.delete()
    return redirect('ticket_list')

@login_required
def delete_closed_ticket(request, ticket_id):
    ticket = get_object_or_404(ClosedTicket, id=ticket_id)
    if request.method == 'POST':
        ticket.delete()
        return redirect('closed_tickets_list')  # Redirect to the list of closed tickets after deletion
    # If it's not a POST request, you might want to handle it differently or return an error
    return redirect('closed_tickets_list')  # Or handle the non-POST request as needed

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm

def login_form(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, email=form.cleaned_data["email"], password=form.cleaned_data["password"])
            if user is not None:
                login(request, user)
                # Redirect to ticket_list after login
                return redirect('ticket_list')
            else:
                return render(request, "registration/login.html", {
                    'form': form, 
                    'error': 'Identifiants invalides. Veuillez réessayer.'
                })
        else:
            return render(request, "registration/login.html", {
                'form': form, 
                'error': 'Identifiants invalides. Veuillez réessayer.'
            })
    else:
        form = LoginForm()
        return render(request, "registration/login.html", {'form': form})

@login_required
def home(request):
    customer = Agent.objects.get(user=request.user)
    return render(request, "myapp/agentpage.html", {"customer": customer})


@login_required
def UserRoter(request):
    if request.user.is_authenticated:

        if request.user.is_superuser:

            return redirect('admin')
        elif request.user.is_staff:
            return redirect('station_de_base')
        else:
            if request.user.function == "AGENT":
                return redirect('agent_page')
            elif request.user.function == "TECHNICIAN":
                return redirect('technician_page')
            else:
                return redirect('supervisor_page')
    else:
        return redirect('login')


@login_required
@user_passes_test(is_superadmin)
def CreateAgent(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        agent_formset = AgentFormSet(request.POST, request.FILES)

        if user_form.is_valid() and agent_formset.is_valid():
            user_form.instance.password = make_password(user_form.cleaned_data["password"])
            user = user_form.save()
            agents = agent_formset.save(commit=False)
            for agent in agents:
                agent.created_by = user
                agent.user = user
                agent.save()
            agent_formset.save_m2m()
            messages.success(request,'Agent créer avec succès')
            return redirect("admin", permanent=True)
        else:
            print(user_form.errors)
            messages.error(request,'les données saisie sont invalide')
            return render(request, "admin/agent_block.html", {
                'user_form': user_form,
                'agent_formset': agent_formset,
            })
    else:
        user_form = UserForm()
        agent_formset = AgentFormSet(initial=None)
        for form in agent_formset:
            form.use_required_attribute = True
    return render(request, "admin/agent_block.html", {
        'user_form': user_form,
        'agent_formset': agent_formset,
    })


@login_required
@user_passes_test(is_superadmin)
def CreateTechnician(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES)
        technician_formset = TechnicianFormSet(request.POST, request.FILES)
        user_form.instance.function = "TECHNICIAN"
        if user_form.is_valid() and technician_formset.is_valid():
            user_form.instance.password = make_password(user_form.cleaned_data["password"])
            user = user_form.save()
            technicians = technician_formset.save(commit=False)
            for technician in technicians:
                technician.created_by = user
                technician.user = user
                technician.save()
            technician_formset.save_m2m()
            messages.success(request,'Technicien créer avec succès')
            return redirect("admin", permanent=True)
        else:
            messages.error(request,'les données saisie sont invalide')
            return render(request, "admin/technician_block.html", {
                'user_form': user_form,
                'technician_formset': technician_formset
            })
    else:
        user_form = UserForm()
        technician_formset = TechnicianFormSet(initial=None)
        for form in technician_formset:
            form.use_required_attribute = True
    return render(request, "admin/technician_block.html", {
        'user_form': user_form,
        'technician_formset': technician_formset
    })

@login_required

@user_passes_test(is_superadmin)
def CreateSupervisor(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        supervisor_formset = SupervisorFormSet(request.POST, request.FILES)
        user_form.instance.function = "SUPERVISOR"
        if user_form.is_valid() and supervisor_formset.is_valid():
            user_form.instance.password = make_password(user_form.cleaned_data['password'])
            user = user_form.save()
            supervisors = supervisor_formset.save(commit=False)
            for supervisor in supervisors:
                supervisor.created_by = user
                supervisor.user = user
                supervisor.save()
            supervisor_formset.save_m2m()
            messages.success(request,'Superviseur créer avec succès')
            return redirect("admin", permanent=True)
        else:
            return render(request, "admin/supervisor_block.html", {
            'user_form': user_form,
            'supervisor_formset': supervisor_formset
            })
    else:
        user_form = UserForm()
        supervisor_formset = SupervisorFormSet(initial=None)
        for form in supervisor_formset:
            form.use_required_attribute = True
    return render(request, "admin/supervisor_block.html", {
        'user_form': user_form,
        'supervisor_formset': supervisor_formset
    })


@login_required
@user_passes_test(is_superadmin)
def admin_page(request):
    return render(request, "admin/admin_home_page.html")



@user_passes_test(is_superadmin)
def DeleteUser(request):
    if request.user.is_authenticated:
            if is_ajax(request):
                if request.GET.get('users') is not None:
                    users = request.GET.get('users')
                else:
                    users = []
            data=users.split(",")
            data = list(map(lambda x: int(x), data))

            for user_id in data:
                user = User.objects.get(id=user_id)
                if user.function == "AGENT":
                    agent = Agent.objects.get(user=user)
                    agent.delete()
                    user.delete()
                elif user.function == "TECHNICIAN":
                    technician = Technician.objects.get(user=user)
                    technician.delete()
                    user.delete()
                elif user.function == "SUPERVISOR":
                    supervisor = Supervisor.objects.get(user=user)
                    supervisor.delete()
                    user.delete()
                elif user.function == "ADMIN":
                    admin = Admin.objects.get(user=user)
                    admin.delete()
                    user.delete()
                else:
                    superadmin = Superuser.objects.get(user=user)
                    superadmin.delete()
                    user.delete()
            messages.success(request,'Utilisateur supprimer avec success')
            return JsonResponse("success")



@user_passes_test(is_superadmin)
def UpdateUser(request, user_id):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            target = User.objects.get(id=user_id)
            if target.function == "AGENT":
                agent = Agent.objects.get(user=target)
                user_form = UserForm(initial={"function": "TECHNICIAN", "email": target.email, "password": ""})
                user_form.fields['password'].required = False
                agent_form = AgentFormSet(initial=[
                    {"nom": agent.nom, "prenom": agent.prenom, "cin": agent.cin,
                     "age": agent.age, "phone": agent.phone, "image": agent.image
                     }
                ])
                # start of the user updating(agent)
                if request.method == "POST":
                    user_post_form = UserForm(request.POST)
                    agent_post_form = AgentFormSet(request.POST, request.FILES)
                    if agent_post_form.is_valid():
                        for form in agent_post_form:
                            Agent.objects.filter(id=agent.id).update(age=form.cleaned_data["age"])
                            Agent.objects.filter(id=agent.id).update(phone=form.cleaned_data["phone"])
                            Agent.objects.filter(id=agent.id).update(image=form.cleaned_data["image"])
                            Agent.objects.filter(id=agent.id).update(nom=form.cleaned_data["nom"])
                            Agent.objects.filter(id=agent.id).update(matricule=form.cleaned_data["matricule"])
                            Agent.objects.filter(id=agent.id).update(age=form.cleaned_data["age"])
                            Agent.objects.filter(id=agent.id).update(prenom=form.cleaned_data["prenom"])
                            Agent.objects.filter(id=agent.id).update(cin=form.cleaned_data["cin"])
                            User.objects.filter(id=user_id).update(email=user_post_form.data["email"])
                            if user_post_form.data["password"] != "":
                                User.objects.filter(id=user_id).update(
                                    password=make_password(user_post_form.data["password"]))
                            return redirect("admin", permanent=True)
                    else:
                        return render(request, "admin/update_agent.html", {
                            "agent_formset": agent_form,
                            "user_form": user_form
                        })

                else:
                    return render(request, "admin/update_agent.html", {
                        "agent_formset": agent_form,
                        "user_form": user_form
                    })
            elif target.function == "TECHNICIAN":
                technician = Technician.objects.get(user=target)
                user_form = UserForm(initial={"function": "TECHNICIAN", "email": target.email, "password": ""})
                user_form.fields['password'].required = False
                technician_form = TechnicianFormSet(initial=[
                    {"nom": technician.nom, "prenom": technician.prenom, "cin": technician.cin,
                     "age": technician.age, "profession": technician.profession, "phone": technician.phone,
                     "image": technician.image}
                ])
                # start of the user updating (technician)
                if request.method == "POST":
                    user_post_form = UserForm(request.POST)
                    technician_post_form = TechnicianFormSet(request.POST, request.FILES)
                    if technician_post_form.is_valid():
                        for form in technician_post_form:
                            Technician.objects.filter(id=technician.id).update(age=form.cleaned_data["age"])
                            Technician.objects.filter(id=technician.id).update(phone=form.cleaned_data["phone"])
                            Technician.objects.filter(id=technician.id).update(image=form.cleaned_data["image"])
                            Technician.objects.filter(id=technician.id).update(nom=form.cleaned_data["nom"])
                            Technician.objects.filter(id=technician.id).update(age=form.cleaned_data["age"])
                            Technician.objects.filter(id=technician.id).update(prenom=form.cleaned_data["prenom"])
                            Technician.objects.filter(id=technician.id).update(cin=form.cleaned_data["cin"])
                            Technician.objects.filter(id=technician.id).update(matricule=form.cleaned_data["matricule"])
                            Technician.objects.filter(id=technician.id).update(profession=form.cleaned_data["profession"])
                            User.objects.filter(id=user_id).update(email=user_post_form.data["email"])
                            if user_post_form.data["password"] != "":
                                User.objects.filter(id=user_id).update(
                                    password=make_password(user_post_form.data["password"]))
                            return redirect("admin", permanent=True)
                    else:
                        return render(request, "admin/update_agent.html", {
                            "technician_formset": technician_form,
                            "user_form": user_form
                        })

                else:
                    return render(request, "admin/update_technician.html", {
                        "technician_formset": technician_form,
                        "user_form": user_form
                    })
            elif target.function == "SUPERVISOR":
                supervisor = Supervisor.objects.get(user=target)
                user_form = UserForm(initial={"function": "SUPERVISOR", "email": target.email, "password": ""})
                user_form.fields['password'].required = False

                supervisor_form = SupervisorFormSet(initial=[
                    {"nom": supervisor.nom, "prenom": supervisor.prenom, "cin": supervisor.cin,
                     "age": supervisor.age, "profession": supervisor.profession, "phone": supervisor.phone,
                     "image": supervisor.image
                     }])
                # start of the user updating (supervisor)
                if request.method == "POST":
                    user_post_form = UserForm(request.POST)
                    supervisor_post_form = SupervisorFormSet(request.POST, request.FILES)
                    user_post_form.fields['password'].required = False

                    if supervisor_post_form.is_valid():
                        for form in supervisor_post_form:
                            Supervisor.objects.filter(id=supervisor.id).update(age=form.cleaned_data["age"])
                            Supervisor.objects.filter(id=supervisor.id).update(phone=form.cleaned_data["phone"])
                            Supervisor.objects.filter(id=supervisor.id).update(image=form.cleaned_data["image"])
                            Supervisor.objects.filter(id=supervisor.id).update(nom=form.cleaned_data["nom"])
                            Supervisor.objects.filter(id=supervisor.id).update(age=form.cleaned_data["age"])
                            Supervisor.objects.filter(id=supervisor.id).update(prenom=form.cleaned_data["prenom"])
                            Supervisor.objects.filter(id=supervisor.id).update(matricule=form.cleaned_data["matricule"])
                            Supervisor.objects.filter(id=supervisor.id).update(cin=form.cleaned_data["cin"])
                            Supervisor.objects.filter(id=supervisor.id).update(profession=form.cleaned_data["profession"])
                            User.objects.filter(id=user_id).update(email=user_post_form.data["email"])
                            if user_post_form.data["password"] != "":
                                User.objects.filter(id=user_id).update(
                                    password=make_password(user_post_form.data["password"]))
                            return redirect("admin", permanent=True)
                    else:
                        return HttpResponse(user_post_form.errors)

                else:
                    return render(request, "admin/update_supervisor.html", {
                        "supervisor_formset": supervisor_form,
                        "user_form": user_form
                    })

            elif target.function == "ADMIN":
                admin = Admin.objects.get(user=target)
                user_form = UserForm(initial={"function": "SUPERVISOR", "email": target.email, "password": ""})
                user_form.fields['password'].required = False

                admin_form = AdminFormSet(initial=[
                    {"nom": admin.nom, "prenom": admin.prenom, "cin": admin.cin,
                     "age": admin.age, "matricule": admin.matricule, "phone": admin.phone,
                     "image": admin.image
                     }])
                # start of the user updating (supervisor)
                if request.method == "POST":
                    user_post_form = UserForm(request.POST)
                    admin_post_form = AdminFormSet(request.POST, request.FILES)
                    user_post_form.fields['password'].required = False

                    if admin_post_form.is_valid():
                        for form in admin_post_form:
                            Admin.objects.filter(id=admin.id).update(age=form.cleaned_data["age"])
                            Admin.objects.filter(id=admin.id).update(phone=form.cleaned_data["phone"])
                            Admin.objects.filter(id=admin.id).update(image=form.cleaned_data["image"])
                            Admin.objects.filter(id=admin.id).update(nom=form.cleaned_data["nom"])
                            Admin.objects.filter(id=admin.id).update(age=form.cleaned_data["age"])
                            Admin.objects.filter(id=admin.id).update(prenom=form.cleaned_data["prenom"])
                            Admin.objects.filter(id=admin.id).update(cin=form.cleaned_data["cin"])
                            Admin.objects.filter(id=admin.id).update(matricule=form.cleaned_data["matricule"])
                            User.objects.filter(id=user_id).update(email=user_post_form.data["email"])
                            if user_post_form.data["password"] != "":
                                User.objects.filter(id=user_id).update(
                                    password=make_password(user_post_form.data["password"]))
                            return redirect("admin", permanent=True)
                    else:
                        return render(request, "admin/update_admin.html", {
                            "admin_formset": admin_form,
                            "user_form": user_form
                        })
                else:
                    return render(request, "admin/update_admin.html", {
                        "admin_formset": admin_form,
                        "user_form": user_form
                    })
            elif target.function == "SUPERADMIN":
                superuser = Superuser.objects.get(user=target)
                user_form = UserForm(initial={"function": "SUPERVISOR", "email": target.email, "password": ""})
                user_form.fields['password'].required = False

                superuser_form = SuperAdminFormSet(initial=[
                        {"nom": superuser.nom, "prenom": superuser.prenom, "cin": superuser.cin,
                         "age": superuser.age, "matricule": superuser.matricule, "phone": superuser.phone,
                         "image": superuser.image
                         }])
                    # start of the user updating (supervisor)
                if request.method == "POST":
                    user_post_form = UserForm(request.POST)
                    superuser_post_form = SuperAdminFormSet(request.POST, request.FILES)
                    user_post_form.fields['password'].required = False
                    if superuser_post_form.is_valid():
                        for form in superuser_post_form:
                             Superuser.objects.filter(id=superuser.id).update(age=form.cleaned_data["age"])
                             Superuser.objects.filter(id=superuser.id).update(phone=form.cleaned_data["phone"])
                             Superuser.objects.filter(id=superuser.id).update(image=form.cleaned_data["image"])
                             Superuser.objects.filter(id=superuser.id).update(nom=form.cleaned_data["nom"])
                             Superuser.objects.filter(id=superuser.id).update(age=form.cleaned_data["age"])
                             Superuser.objects.filter(id=superuser.id).update(prenom=form.cleaned_data["prenom"])
                             Superuser.objects.filter(id=superuser.id).update(
                                    matricule=form.cleaned_data["matricule"])
                             Supervisor.objects.filter(id=superuser.id).update(cin=form.cleaned_data["cin"])


                             User.objects.filter(id=user_id).update(email=user_post_form.data["email"])
                             if user_post_form.data["password"] != "":
                                User.objects.filter(id=user_id).update(
                                        password=make_password(user_post_form.data["password"]))
                                return redirect("admin", permanent=True)
                    else:
                        return render(request, "admin/update_superuser.html", {
                            "superuser_formset": superuser_form,
                            "user_form": user_form
                        })
                else:
                    return render(request, "admin/update_superuser.html", {
                        "superuser_formset": superuser_form,
                        "user_form": user_form
                    })


@login_required
@user_passes_test(is_technician)
def resolve_ticket(request, ticket_id):
    """Mark a ticket as resolved."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        ticket.status = 'completed'
        ticket.save()
        return redirect('ticket_list')
    return render(request, 'myapp/resolve_ticket.html', {'ticket': ticket})



@login_required
@user_passes_test(is_supervisor)
def approve_ticket(request, ticket_id):
    """Approve a completed ticket."""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        ticket.status = 'approved'
        ticket.approved_by = Supervisor.objects.get(user=request.user)
        ticket.save()
        return redirect('ticket_list')
    return render(request, 'myapp/approve_ticket.html', {'ticket':ticket})

# placeholder for all the user pages
@login_required
@user_passes_test(is_agent)
def AgentPage(request):
    return render(request, 'myapp/agentpage.html', {"user": request.user})


@login_required
@user_passes_test(is_technician)
def TechnicianPage(request):
    return render(request, 'myapp/technicianpage.html', {"user": request.user})


@login_required
@user_passes_test(is_supervisor)
def SupervisorPage(request):
    return render(request, 'myapp/supervisorpage.html')


@login_required
@user_passes_test(is_administrator)
def StationDeBase(request):
    return render(request, 'myapp/ticket_list.html')


@login_required
@user_passes_test(is_superadmin)
def search_general(request):
    query = ""
    if is_ajax(request):
        if request.GET.get('query') is not None:
            query = request.GET.get('query')
        else:
            query = ""

    user = list()
    for agent in Agent.objects.all():
        role = ""
        FullName = ""
        if agent.user.function == "TECHNICIAN":
            role = "TECHNICIAN /" + Technician.objects.get(user=agent.user).profession
        elif agent.user.function == "SUPERVISOR":
            role = "SUPERVISOR /" + Supervisor.objects.get(user=agent.user).profession
        else:
            role = "Agent"
        FullName = agent.nom + " " + agent.prenom
        Phone = agent.phone
        image = agent.image.name
        if image!=None:
            image = os.path.join(settings.MEDIA_URL, image)
        matricule = agent.matricule
        if query.lower() in FullName.lower() or query.lower() in matricule.lower():
            user.append({"id": agent.user.id,
                         "full_name": FullName,
                         "matricule": matricule,
                         "phone":Phone.as_national,
                         "email":agent.user.email,
                         "image":image,
                         "cin":agent.cin,
                         "status": agent.user.is_active,
                         "role": role})
    for superuser in Superuser.objects.all():
        role = "Super admin"
        FullName = ""
        FullName = superuser.nom + " " + superuser.prenom
        Phone = superuser.phone
        image = superuser.image.name
        if image != None:
            image = os.path.join(settings.MEDIA_URL, image)
        matricule =superuser.matricule
        if query.lower() in FullName.lower() or query.lower() in matricule.lower():
            user.append({"id": superuser.user.id,
                         "full_name": FullName,
                         "matricule": matricule,
                         "phone": Phone.as_national,
                         "email": superuser.user.email,
                         "image": image,
                         "cin":superuser.cin,
                         "status": superuser.user.is_active,
                         "role": role})
    for admin in Admin.objects.all():
        role = "Admin"
        FullName = ""
        FullName = admin.nom + " " + admin.prenom
        Phone = admin.phone
        image = admin.image.name
        if image != None:
            image = os.path.join(settings.MEDIA_URL, image)
        matricule =admin.matricule
        if query.lower() in FullName.lower() or query.lower() in matricule.lower():
            user.append({"id": admin.user.id,
                         "full_name": FullName,
                         "matricule": matricule,
                         "phone": Phone.as_national,
                         "email": admin.user.email,
                         "image": image,
                         "cin":admin.cin,
                         "status": admin.user.is_active,
                         "role": role})
    return JsonResponse({"users": user}, safe=False)







# create station de base user
@user_passes_test(is_superadmin)
def CreationAdminSationBase(request):
    if request.method == "POST":
        user_form = AdminForm(request.POST)
        admin_form = AdminFormSet(request.POST,request.FILES)
        if admin_form.is_valid() and admin_form.is_valid():
            user_form.instance.password = make_password(admin_form.instance.password)
            user_form.instance.is_staff = True
            user_form.instance.function = "ADMIN"
            user = user_form.save()
            admins = admin_form.save(commit=False)
            for admin in admins:
                admin.user = user
                admin.save()
            admin_form.save_m2m()
            messages.success(request,'Admin station de base créer avec succès')
            return redirect("admin")
        else:
            messages.error(request,'les données saisie sont invalide')
            return render(request, "admin/station_de_base_block.html",
                          {"user_form": UserForm, "adminformset": AdminFormSet})

    else:
        user_form = AdminForm()
        admin_form = AdminFormSet()
        for form in admin_form:
            form.use_required_attribute = True
        return render(request, "admin/station_de_base_block.html", {"user_form":user_form,"adminformset": admin_form})


def UpdateAdminSationBase(request, admin_id):
    if request.method == "POST":
        form = AdminForm(request.POST)
        if form.is_valid():
            User.objects.filter(id=admin_id).update(email=form.cleaned_data['email'],
                                                    password=make_password(form.cleaned_data['password']))
            return redirect("admin_station_base")
        else:
            return HttpResponse(form.errors, status=400)

    else:
        form = AdminForm(initial={"email": User.objects.get(id=admin_id).email, "password": ""})
        return render(request, "admin/station_de_base_block.html", {"form": form})


def DeleteAdminSationBase(request, admin_id):
    if request.user.is_authenticated:
        User.objects.filter(id=admin_id).delete()
        return redirect("admin_station_base")

    else:
        form = AdminForm(initial={"email": User.objects.get(id=admin_id).email, "password": ""})
        return render(request, "admin/station_de_base_block.html", {"form": form})

def DataDisplay(request):
    name = "qsdftrez"
    ticket_list = list()
    for one in Ticket.objects.all():
        ticket_list.append({"id": one.id,
                            "type": one.Categorie,
                            "priorite":one.priority,
                            "creator":one.name,
                            "image":one.image.name})

    return JsonResponse({"tickets": ticket_list}, safe=False)

def CreateSuperUser(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        superadmin_formset = SuperAdminFormSet(request.POST, request.FILES)
        user_form.instance.function = "SUPERADMIN"
        if user_form.is_valid() and superadmin_formset.is_valid():
            user_form.instance.password = make_password(user_form.cleaned_data['password'])
            user_form.instance.is_superuser = True
            user = user_form.save()
            superusers = superadmin_formset.save(commit=False)
            for superuser in superusers:
                superuser.user = user
                superuser.save()
            superadmin_formset.save_m2m()
            messages.success(request,'Admin système créer avec succès')
            return redirect("admin", permanent=True)
        else:
            messages.error(request,'les données saisie sont invalide')
            return render(request, "admin/super_user.html", {
                'user_form': user_form,
                'superadmin_formset': superadmin_formset
            })
    else:
        user_form = UserForm()
        superadmin_formset = SuperAdminFormSet(initial=None)
        for form in superadmin_formset:
            form.use_required_attribute = True
    return render(request, "admin/super_user.html", {
        'user_form': user_form,
        'superadmin_formset':  superadmin_formset
    })

def DesactivateAcount(request):
    if request.user.is_authenticated:
            if is_ajax(request):
                if request.GET.get('users') is not None:
                    users = request.GET.get('users')
                else:
                    users = []
            data=users.split(",")
            data = list(map(lambda x: int(x), data))

            for user_id in data:
                User.objects.filter(id=user_id).update(is_active=False)
                messages.success(request,'comptes d\'utilisateurs désactivé avec success')
            return JsonResponse({"success":"success"})
def ActivateAcount(request):
    if request.user.is_authenticated:
            if is_ajax(request):
                if request.GET.get('users') is not None:
                    users = request.GET.get('users')
                else:
                    users = []
            data=users.split(",")
            data = list(map(lambda x: int(x), data))

            for user_id in data:
                User.objects.filter(id=user_id).update(is_active=True)
                messages.success(request,'comptes d\'utilisateurs désactivè avec success')
            return JsonResponse({"success":"success"})