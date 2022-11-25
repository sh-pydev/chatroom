from django.shortcuts import render, redirect
from django.db.models import Q
from . models import *
from . forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
# Create your views here.

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        page = 'login'
        if request.method == "POST":
            username = request.POST.get('username').lower()
            password = request.POST.get('password')
            try:
                user = User.objects.get(username = username)
                user = authenticate(request, username = username, password = password)
                if user is None:
                    messages.error(request, 'Wrong password')
                else:
                    login(request, user)
                    return redirect('home')
            except:
                messages.error(request, 'User does not exist')
    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def registerPage(request):
    form = UserCreationForm
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured')
    context = {'form': form}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains = q) |
                                Q(name__icontains = q) |
                                Q(host__username__icontains = q) |
                                Q(description__icontains = q))
    topics = Topic.objects.all()
    room_count = rooms.count()
    msgs = Message.objects.filter(Q(room__name__icontains=q) | Q(room__topic__name__icontains=q)).order_by('-created')
    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'msgs':msgs}
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def room(request, pk):
    room = Room.objects.get(id=pk)
    msgs = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    topics = Topic.objects.all() 
    if request.method == "POST":
        msg = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room':room, 'msgs': msgs, 'participants':participants, 'topics':topics}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    topics = Topic.objects.all() 
    msgs = Message.objects.filter(user=request.user)
    context = {'user':user, 'rooms':rooms, 'msgs':msgs, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.user == room.host:
        if request.method == "POST":
            form = RoomForm(request.POST, instance=room)
            if form.is_valid():
                form.save()
                return redirect('home')
    else:
        return Http404
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user == room.host:
        if request.method == "POST":
            room.delete()
            return redirect('home')
    else:
        return Http404
    return render(request, 'base/room_delete.html')