import os
import requests
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from concert.forms import LoginForm
from concert.models import Concert, ConcertAttending


def index(request):
    return render(request, 'index.html')


def service_data(variable, default, suffix):
    response = requests.get(os.environ.get(variable, default).rstrip('/') + suffix, timeout=8)
    response.raise_for_status()
    return response.json()


def songs(request):
    try:
        data = service_data('SONGS_SERVICE_URL', 'http://127.0.0.1:5001', '/song')
    except (requests.RequestException, ValueError):
        return render(request, 'service_error.html', {'service': 'Songs'}, status=503)
    return render(request, 'songs.html', {'songs': data})


def photos(request):
    try:
        data = service_data('PICTURES_SERVICE_URL', 'http://127.0.0.1:5000', '/picture')
    except (requests.RequestException, ValueError):
        return render(request, 'service_error.html', {'service': 'Photos'}, status=503)
    return render(request, 'photos.html', {'photos': data})


def singlephoto(request, id):
    try:
        data = service_data('PICTURES_SERVICE_URL', 'http://127.0.0.1:5000', f'/picture/{id}')
    except (requests.RequestException, ValueError):
        return render(request, 'service_error.html', {'service': 'Photo'}, status=503)
    return render(request, 'singlephoto.html', {'photo': data})


def login_view(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('index')
    return render(request, 'login.html', {'form': form})


def signup(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.save())
        return redirect('index')
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


def concerts(request):
    items = []
    for concert in Concert.objects.order_by('date'):
        attendance = concert.attendee.filter(user=request.user).first() if request.user.is_authenticated else None
        items.append({'concert': concert, 'status': attendance.attending if attendance else '-'})
    return render(request, 'concerts.html', {'concerts': items})


@login_required(login_url='login')
def concert_detail(request, id):
    obj = get_object_or_404(Concert, pk=id)
    attendance = obj.attendee.filter(user=request.user).first()
    return render(request, 'concert_detail.html', {'concert_details': obj,
        'status': attendance.attending if attendance else '-',
        'attending_choices': ConcertAttending.AttendingChoices.choices})


@login_required(login_url='login')
@require_POST
def concert_attendee(request):
    concert = get_object_or_404(Concert, pk=request.POST.get('concert_id'))
    choice = request.POST.get('attendee_choice')
    if choice not in ConcertAttending.AttendingChoices.values:
        return HttpResponseBadRequest('Invalid RSVP')
    ConcertAttending.objects.update_or_create(concert=concert, user=request.user,
        defaults={'attending': choice})
    return redirect('concerts')
