from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
# Para crear un formulario user creation del django
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone

# Para las rutas protegidas
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                # registrar y crear el usuario
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                # guardar en la base de datos el usuario creado
                user.save()
                
                # Loguear al usuario y se crea una cockie
                login(request, user)
                return redirect('tasks')
                # return HttpResponse('Usuario creado !!!!')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': 'El usuario ya existe'})
        else:
            return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': 'Las contraseñas no coinciden'})

@login_required
def tasks (request):
    # traer tareas de todos los usuarios
    # tasks = Task.objects.all()
    # Solo las tareas de este usuario
    # tasks = Task.objects.filter(user = request.user)
    # Solo las tareas del usuario de este usuario y la fecha de completado vacío (no completadas)
    tasks = Task.objects.filter(user = request.user, dateCompleted__isnull = True)
    return render (request, 'tasks.html', {'tasks': tasks})

@login_required
def cerrarSesion (request):
    logout(request)
    return redirect ('home')

def iniciarSesion (request):
        if request.method == 'GET':
            return render (request,'signin.html', {
                'form': AuthenticationForm()
            })
        else:
            user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
            if user is None:
                return render (request,'signin.html', {
                    'form': AuthenticationForm(),
                    'error': 'Password incorrecto'
                })
            else:
                login(request, user)
                return redirect('tasks')

@login_required
def create_task (request):
    if request.method == 'GET':
        return render (request, 'create_task.html', {
        'form': TaskForm
    })
    else:
        try:
            # recibir los datos de la URL con el mismo Taskform
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render (request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Falta validar la data'
                })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        # Es bueno, pero tumba el servidor si ponen task_id = 1000
        # task = Task.objects.get(pk=task_id)
        # Ésto es mejor ya que te manda un 404 , es más seguro
        # Filtra por id y por usuario, para que otro usuario no vea tus tareas
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html',{'task':task, 'form':form})
    else:
        try:
            # Acceso a todas las tareas de los usuarios
            # task = get_object_or_404(Task, pk=task_id)
            # Acceso a solo las tareas del user
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect ('tasks')
        except ValueError:
            return render(request, 'task_detail.html',{'task':task, 'form':form , 'error' : 'Error actualizando task'})

@login_required
def task_complete(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.dateCompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def tasks_completed (request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull = False).order_by('-dateCompleted')
    return render (request, 'tasks.html', {'tasks': tasks})