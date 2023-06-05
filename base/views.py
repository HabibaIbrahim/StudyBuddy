from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from base.forms import RoomForm, UserForm
from .models import Room, Topic, Message


# Rooms = [
#     {'id':1, 'name':'Lets learn python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Fronend developers'},
# ]



def loginPage(request):
    
    page = 'login'

    if request.user.is_authenticated:
        return redirect('Home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('Home')
        else:
           messages.error(request, 'User OR Password does not exist') 
        
    context = {"page": page}
    return render(request, 'base/login_register.html', context)


def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect ('Home')
        else:
            messages.error(request, 'An error has occurred during registeration!')
    return render(request, 'base/login_register.html',{'form':form})


def logoutUser(request):
    logout(request)
    return redirect('Home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    Rooms = Room.objects.filter( 
        Q(topic__name__icontains=q) |
        Q(name__icontains=q)|
        Q(description__icontains=q)
        ) # at least contains one char from the parameter in the search bar, not case sensitve
    topics = Topic.objects.all()[0:5]
    room_count = Rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context ={'Rooms': Rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def rooms(request,pk):
    # Primary Key (pk) the variable used to create the database based on the following logic
    # The logic is each room has an id and name, the link of each room returns the room id in the url. 
    # In order to change the content inside the url, the loop and condition are used. 
    # room = None
    # for i in Rooms:
    #     if i['id']==int(pk):
    #         room = i
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect ('ROOM', pk=room.id)
    context = {'room': room, 'room_messages': room_messages, 'participants': participants} # used to return the room name when the link is clicked
    return render(request, 'base/room.html',context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    Rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user': user, 'Rooms': Rooms, "room_messages": room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)
    


@login_required(login_url='/base/login/')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    # print(form)
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        return redirect('Home')

    context = {'form': form, 'topics':topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='/base/login/')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('Home')
    context = {'form': form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='/base/login/')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    if request.method == 'POST':
        room.delete()
        return redirect('Home')
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='/base/login/')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    if request.method == 'POST':
        message.delete()
        return redirect('Home')
    return render(request, 'base/delete.html', {'obj':message})



@login_required(login_url='/base/login/')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})