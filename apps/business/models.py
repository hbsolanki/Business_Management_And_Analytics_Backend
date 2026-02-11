from django.db import models
from apps.base.models import BaseModel


class Business(BaseModel):
    name = models.CharField(max_length=100,null=True,blank=True)
    gst_number = models.CharField(max_length=20,unique=True, null=True, blank=True)
    description = models.CharField(max_length=255,null=True, blank=True)


    class Meta:
        db_table = 'bma_business'

        permissions = [
            ("update_business", "Can update business"),
        ]