import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Movie, MovieList
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def index(request):
    movies = Movie.objects.all()
    featured_movie = movies[len(movies)-1]

    context = {
        'movies': movies,
        'featured_movie': featured_movie,
    }
    return render(request, 'index.html', context)

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credential Invalid')
            return redirect('login')
    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already registered.')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already registered.')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect('/')
        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')
    else:
        pass
    return render(request, 'signup.html')

@login_required(login_url='login')
def movie(request, pk):
    movie = Movie.objects.get(uu_id=pk)

    context = {
        'movie_details': movie,
    }
    return render(request, 'movie.html', context)

@login_required(login_url='login')
def my_list(request):
    movie_list = MovieList.objects.filter(owner_user=request.user)
    user_movie_list = []
    for movie in movie_list:
        user_movie_list.append(movie.movie)

    context = {
        'movies': user_movie_list,
    }
    return render(request, 'my_list.html', context)

@login_required(login_url='login')
def add_to_list(request):
    if request.method == 'POST':
        movie_id = request.POST['movie_id']
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, movie_id)
        movie_id = match.group() if match else None
        movie = get_object_or_404(Movie, uu_id=movie_id)
        movie_list, created = MovieList.objects.get_or_create(owner_user=request.user, movie=movie)

        if created:
            response_data = {'status': 'success', 'message': 'Movie added ✓'}
        else:
            response_data = {'status': 'info', 'message': 'Movie already in list'}
        return JsonResponse(response_data)
    else:
        response_data = {'status': 'error', 'message': 'Invalid request'}
        return JsonResponse(response_data, status=400)

@login_required(login_url='login')
def search(request):
    if request.method == 'POST':
        search = request.POST['search_term']
        movies = Movie.objects.filter(title__icontains=search)

        context = {
            'movies': movies,
            'search_term': search,
        }
    else:
        return redirect('/')
    return render(request, 'search.html', context)

@login_required(login_url='login')
def genre(request, pk):
    movies = Movie.objects.filter(genre=pk)

    context = {
        'movies': movies,
        'movie_genre': pk,
    }
    return render(request, 'genre.html', context)

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('/')