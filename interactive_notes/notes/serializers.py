from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Notebook, Section, ContentBlock, Collaborator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        # Используем create_user для корректного хеширования пароля
        user = User.objects.create_user(**validated_data)
        return user


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
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Collaborator
        fields = ['id', 'user', 'user_details', 'role', 'username']

    def validate(self, data):
        request = self.context.get('request')

        # Проверяем, что передан либо user, либо username
        user = data.get('user')
        username = data.get('username')

        if not user and not username:
            raise serializers.ValidationError(
                "Необходимо указать пользователя (user или username)"
            )

        # Если передан username, ищем пользователя
        if username and not user:
            try:
                user_obj = User.objects.get(username=username)
                data['user'] = user_obj
                data.pop('username')  # Удаляем username из данных
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"username": "Пользователь с таким именем не найден"}
                )

        # Проверка на добавление самого себя
        if request and data.get('user'):
            if request.user == data['user']:
                raise serializers.ValidationError(
                    "Владелец конспекта уже имеет полный доступ и не может быть добавлен как соавтор."
                )

        return data

    def create(self, validated_data):
        validated_data.pop('username', None)
        return super().create(validated_data)


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
