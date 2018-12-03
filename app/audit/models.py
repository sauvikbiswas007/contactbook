from django.db import models



class Audit(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(blank=False)
    updated_by = models.IntegerField(blank=False)
    is_deleted = models.BooleanField(default=False)