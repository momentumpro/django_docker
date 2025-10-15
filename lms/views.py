from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm

from .models import (
    Profile, Category, Course, Lesson, Enrollment,
    LessonProgress, CourseReview
)
from .serializers import (
    UserSerializer, ProfileSerializer, CategorySerializer, CourseSerializer,
    LessonSerializer, EnrollmentSerializer, LessonProgressSerializer, CourseReviewSerializer
)


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Usuario registrado correctamente')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def iniciar_sesion(request):
    # Detect whether a Google SocialApp is configured for allauth so the
    # template can safely show/hide the provider login link.
    google_provider_enabled = False
    try:
        from allauth.socialaccount.models import SocialApp
        google_provider_enabled = SocialApp.objects.filter(
            provider='google').exists()
    except Exception:
        # allauth may not be available or DB may not have SocialApp entries.
        google_provider_enabled = False

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('perfil')
        else:
            messages.error(request, 'Credenciales incorrectas')
            # Redirect to home so the base template (which contains the login modal)
            # will render the messages and our JS will keep the modal open.
            return redirect('home')
    return render(request, 'usuarios/login.html', {'google_provider_enabled': google_provider_enabled})


@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')


def cerrar_sesion(request):
    logout(request)
    return redirect('home')


def index(request):
    # Show up to 20 published courses on the home page
    courses = Course.objects.filter(
        status='published').order_by('-created_at')[:20]
    return render(request, 'index.html', {'courses': courses})


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined']
    ordering = ['username']


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Profile model"""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_instructor']
    search_fields = ['user__username', 'bio']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Categorias para los cursos ofrecidos (read-only)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course model"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['difficulty', 'status', 'category', 'instructor']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'price']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    """ViewSet for Lesson model"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'lesson_type', 'is_published']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'title', 'created_at']
    ordering = ['course', 'order']


class EnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Enrollment model"""
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'course', 'student']
    search_fields = ['course__title']
    ordering_fields = ['enrolled_at']
    ordering = ['-enrolled_at']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class CourseReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for CourseReview model"""
    queryset = CourseReview.objects.all()
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'rating']
    search_fields = ['comment']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class LessonProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for LessonProgress model"""
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'lesson', 'is_completed']
    search_fields = ['lesson__title']
    ordering_fields = ['completed_at', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
