from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from notes.serializers import UserSerializer  # Убедитесь, что импорт верный

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Здесь сработает вся валидация!
        self.perform_create(serializer)

        return Response(
            {"message": "User created successfully"},
            status=status.HTTP_201_CREATED
        )
