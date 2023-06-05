from rest_framework.serializers import ModelSerializer
from base.models import Room

class RoomSerliazer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'