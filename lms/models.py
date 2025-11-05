from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Extended user profile for LMS users"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_instructor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Category(models.Model):
    """Course categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default='#007bff', help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Course(models.Model):
    """Course model"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses_taught')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    difficulty = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/', null=True, blank=True)
    duration_hours = models.PositiveIntegerField(
        default=0, help_text="Total course duration in hours")
    max_students = models.PositiveIntegerField(
        null=True, blank=True, help_text="Maximum number of students (null = unlimited)")
    prerequisites = models.TextField(
        blank=True, help_text="Course prerequisites")
    learning_objectives = models.TextField(
        blank=True, help_text="What students will learn")
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Course"
        verbose_name_plural = "Courses"


class Lesson(models.Model):
    """Lesson model for course content"""
    LESSON_TYPES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('live', 'Live Session'),
    ]

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lesson_type = models.CharField(
        max_length=20, choices=LESSON_TYPES, default='video')
    content = models.TextField(
        blank=True, help_text="Lesson content (text, video URL, etc.)")
    video_url = models.URLField(
        blank=True, help_text="Video URL for video lessons")
    duration_minutes = models.PositiveIntegerField(
        default=0, help_text="Lesson duration in minutes")
    order = models.PositiveIntegerField(
        default=0, help_text="Order within the course")
    is_published = models.BooleanField(default=True)
    is_free = models.BooleanField(
        default=False, help_text="Free lesson (accessible without enrollment)")
    attachments = models.FileField(
        upload_to='lesson_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"


class Enrollment(models.Model):
    """Student enrollment in courses (inscriptions)"""
    ENROLLMENT_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('suspended', 'Suspended'),
    ]

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(
        max_length=20, choices=ENROLLMENT_STATUS, default='active')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Course completion percentage"
    )
    last_accessed = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(
        blank=True, help_text="Instructor notes about this enrollment")

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title}"

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"


class LessonProgress(models.Model):
    """Track student progress through individual lessons"""
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(
        default=0, help_text="Time spent on this lesson")
    last_position = models.PositiveIntegerField(
        default=0, help_text="Last position in video (seconds)")
    notes = models.TextField(
        blank=True, help_text="Student notes for this lesson")

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.lesson.title}"

    class Meta:
        unique_together = ['student', 'lesson']
        verbose_name = "Lesson Progress"
        verbose_name_plural = "Lesson Progress"


class CourseReview(models.Model):
    """Student reviews for courses"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='course_reviews')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title} ({self.rating} stars)"

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-created_at']
        verbose_name = "Course Review"
        verbose_name_plural = "Course Reviews"
