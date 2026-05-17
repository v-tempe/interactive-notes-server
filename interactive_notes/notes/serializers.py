from rest_framework import serializers
from .models import Notebook, Section, ContentBlock, Collaborator
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ContentBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentBlock
        fields = ['id', 'block_type', 'content', 'image_url', 'order']


class SectionSerializer(serializers.ModelSerializer):
    blocks = ContentBlockSerializer(many=True, read_only=False)

    class Meta:
        model = Section
        fields = ['id', 'title', 'order', 'blocks']

    def create(self, validated_data):
        blocks_data = validated_data.pop('blocks')
        section = Section.objects.create(**validated_data)
        for block_data in blocks_data:
            ContentBlock.objects.create(section=section, **block_data)
        return section

    def update(self, instance, validated_data):
        blocks_data = validated_data.pop('blocks')

        # update fields
        instance.title = validated_data.get('title', instance.title)
        instance.order = validated_data.get('order', instance.order)
        instance.save()

        # delete old blocks & create new
        instance.blocks.all().delete()
        for block_data in blocks_data:
            ContentBlock.objects.create(section=instance, **block_data)

        return instance


class CollaboratorSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Collaborator
        fields = ['id', 'user', 'user_details', 'role']


class NotebookSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=False)
    collaborators = CollaboratorSerializer(many=True, read_only=True)
    owner_details = UserSerializer(source='owner', read_only=True)

    class Meta:
        model = Notebook
        fields = ['id', 'title', 'owner', 'owner_details', 'created_at', 'updated_at', 'sections', 'collaborators']
        read_only_fields = ['owner']

    def create(self, validated_data):
        sections_data = validated_data.pop('sections')
        notebook = Notebook.objects.create(**validated_data)

        for section_data in sections_data:
            blocks_data = section_data.pop('blocks')
            section = Section.objects.create(notebook=notebook, **section_data)
            for block_data in blocks_data:
                ContentBlock.objects.create(section=section, **block_data)

        return notebook

    def update(self, instance, validated_data):
        # 1. Обновляем простые поля конспекта (например, title)
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        # 2. Обрабатываем секции
        sections_data = validated_data.pop('sections', [])

        # Для простоты реализации:
        # Мы удалим все старые секции (и их блоки) и создадим новые на основе присланных данных.
        # Это гарантирует синхронизацию состояния фронтенда и бэкенда.

        # Удаляем старые секции (каскадное удаление удалит и блоки)
        instance.sections.all().delete()

        for section_data in sections_data:
            blocks_data = section_data.pop('blocks', [])
            # Создаем новую секцию
            section = Section.objects.create(
                notebook=instance,
                title=section_data.get('title'),
                order=section_data.get('order', 0)
            )
            # Создаем блоки для этой секции
            for block_data in blocks_data:
                ContentBlock.objects.create(
                    section=section,
                    block_type=block_data.get('block_type'),
                    content=block_data.get('content', ''),
                    image_url=block_data.get('image_url'),
                    order=block_data.get('order', 0)
                )

        return instance
