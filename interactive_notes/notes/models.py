from django.db import models
from django.conf import settings


class Notebook(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название конспекта")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_notebooks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class Collaborator(models.Model):
    ROLE_CHOICES = (
        ('viewer', 'Просмотр'),
        ('editor', 'Редактирование'),
    )
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')

    class Meta:
        unique_together = ('notebook', 'user')


class Section(models.Model):
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255, verbose_name="Заголовок раздела")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.notebook.title} - {self.title}"


class ContentBlock(models.Model):
    BLOCK_TYPES = (
        ('text', 'Текст'),
        ('code', 'Код'),
        ('image', 'Изображение'),
    )
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='blocks')
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPES, default='text')
    content = models.TextField(blank=True)
    image_url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
