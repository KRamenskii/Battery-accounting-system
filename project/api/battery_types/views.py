import threading
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from battery_types.models import BatteryType
from .serializers import BatteryTypeSerializer
from api.views import EventTrackingAPIView


class BatteryTypeListCreateAPIView(EventTrackingAPIView, generics.ListCreateAPIView):
    queryset = BatteryType.objects.all()

    def get_serializer_class(self):
        # Возвращает подходящий сериализатор в зависимости от запроса
        if self.request.method == 'POST':
            return BatteryTypeSerializer
        return BatteryTypeSerializer
    
    def get(self, request, *args, **kwargs):
        # Обрабатывает GET запрос для получения списка типов АБ
        return super().get(request, *args, **kwargs)


class BatteryTypeDetailAPIView(EventTrackingAPIView, generics.RetrieveUpdateDestroyAPIView):
    queryset = BatteryType.objects.all()

    def get_serializer_class(self):
        # Возвращает подходящий сериализатор в зависимости от запроса
        if self.request.method in ['PUT', 'PATCH']:
            return BatteryTypeSerializer
        return BatteryTypeSerializer
    
    def update(self, request, *args, **kwargs):
        # Обрабатывает обновление типа АБ с валидацией
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        # Метод удаления типа АБ
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Тип АБ успешно удален'},
            status=status.HTTP_204_NO_CONTENT,
        )