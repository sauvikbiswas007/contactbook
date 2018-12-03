from django.shortcuts import render

# Create your views here.
from app.audit.models import Audit
from app.audit.serializers import AuditSerializer
from common.util import is_empty


def get_new_audit(created_by=0, updated_by=0, is_deleted=False):
    audit_serializer_data = {
        'created_by': created_by,
        'updated_by': updated_by,
        'is_deleted': is_deleted
    }
    audit_serializer = AuditSerializer(data = audit_serializer_data)
    if audit_serializer.is_valid():
        audit = audit_serializer.save()
        return True, audit
    else:
        return False, audit_serializer.errors
