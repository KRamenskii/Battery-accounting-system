import threading
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from journal.models import InstallationLocation
from .serializers import InstallationLocationSerializer
from api.views import EventTrackingAPIView


class InstallationLocationListCreateAPIView(EventTrackingAPIView, generics.ListCreateAPIView):
    queryset = InstallationLocation.objects.all()

    def get_serializer_class(self):
        # Возвращает подходящий сериализатор в зависимости от запроса
        if self.request.method == 'POST':
            return InstallationLocationSerializer
        return InstallationLocationSerializer
    
    def get(self, request, *args, **kwargs):
        # Обрабатывает GET запрос для получения списка серийных номеров
        return super().get(request, *args, **kwargs)


class InstallationLocationDetailAPIView(EventTrackingAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = InstallationLocation.objects.all()

    def get_serializer_class(self):
        # Возвращает подходящий сериализатор в зависимости от запроса
        if self.request.method in ['PUT', 'PATCH']:
            return InstallationLocationSerializer
        return InstallationLocationSerializer
    
    def update(self, request, *args, **kwargs):
        # Обрабатывает обновление серийного номера
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        # Метод удаления серийного номера
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Серийный номер успешно удален'},
            status=status.HTTP_204_NO_CONTENT,
        )