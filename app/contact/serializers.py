from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from app.audit.models import Audit
from app.audit.serializers import AuditSerializer
from app.contact.models import User, Contact


class UserSerializer(ModelSerializer):
    audit = serializers.SlugRelatedField('id', queryset=Audit.objects.all(), required=False)

    class Meta:
        model = User
        fields = ('__all__')


class UserDisplaySerializer(ModelSerializer):
    audit = AuditSerializer(many=False, required=False)

    class Meta:
        model = User
        fields = ('__all__')


class ContactSerializer(ModelSerializer):
    audit = serializers.SlugRelatedField('id', queryset=Audit.objects.all(), required=False)
    owner = serializers.SlugRelatedField('id', queryset=User.objects.all(), required=False)
    contact_list = serializers.SlugRelatedField('id', queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Contact
        fields = ('__all__')


class ContactDisplaySerializer(ModelSerializer):
    audit = AuditSerializer(many=False, required=False)
    owner = UserDisplaySerializer(many=False, required=False)
    contact_list = UserDisplaySerializer(many=True, required=False)

    class Meta:
        model = Contact
        fields = ('__all__')
