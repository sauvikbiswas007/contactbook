from rest_framework.serializers import ModelSerializer

from app.audit.models import Audit


class AuditSerializer (ModelSerializer):

    class Meta:
        model = Audit
        fields = ('__all__')