from django.db import models
from app.audit.models import Audit


class User (models.Model):
    email = models.CharField (max_length=150, blank=False)
    phone = models.CharField (max_length=10, blank=False)
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE,blank=True, null=True)


class Contact (models.Model):
    owner = models.ForeignKey (User, on_delete=models.CASCADE)
    contact_list = models.ManyToManyField(User, related_name='contact_list_user')
    audit = models.ForeignKey (Audit, on_delete=models.CASCADE,blank=True,null=True)


