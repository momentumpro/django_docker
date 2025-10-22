from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Profile, Category, Course, Lesson, Enrollment,
    LessonProgress, CourseReview
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django User model"""
    password = serializers.CharField(
        write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'is_active', 'date_joined', 'password']
        read_only_fields = ['id', 'date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""
    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'birth_date', 'phone',
                  'avatar', 'is_instructor', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'instructor', 'category', 'difficulty', 'status', 'price',
            'thumbnail', 'duration_hours', 'max_students', 'prerequisites',
            'learning_objectives', 'is_featured', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""

    class Meta:
        model = Lesson
        fields = [
            'id', 'course', 'title', 'description', 'lesson_type',
            'content', 'video_url', 'duration_minutes', 'order', 'is_published',
            'is_free', 'attachments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'course', 'status', 'enrolled_at',
            'completed_at', 'progress_percentage', 'last_accessed', 'notes'
        ]
        read_only_fields = ['id', 'enrolled_at', 'completed_at']


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for LessonProgress model"""

    class Meta:
        model = LessonProgress
        fields = [
            'id', 'student', 'lesson', 'is_completed',
            'completed_at', 'time_spent_minutes', 'last_position', 'notes'
        ]
        read_only_fields = ['id']


class CourseReviewSerializer(serializers.ModelSerializer):
    """Serializer for CourseReview model"""

    class Meta:
        model = CourseReview
        fields = [
            'id', 'student', 'course', 'rating', 'comment',
            'is_anonymous', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
