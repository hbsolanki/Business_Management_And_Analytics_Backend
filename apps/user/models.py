from django.db import models
from django.contrib.auth.models import AbstractUser,UserManager
from apps.business.models import Business
from apps.base.models import BaseModel
from apps.base.utils.active_use_manager import ActiveUserManager

class User(BaseModel,AbstractUser):
    objects = ActiveUserManager()
    all_objects = UserManager()

    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        MANAGER = "MANAGER", "Manager"
        EMPLOYEE = "EMPLOYEE", "Employee"

    class Work(models.TextChoices):
        PRODUCT = "PRODUCT","Production"
        INVENTORY = "INVENTORY", "Inventory"
        ANALYTICS = "ANALYTICS", "Analytics"
        INVOICE = "INVOICE", "Invoice"


    role = models.CharField(max_length=10,choices=Role.choices, default=Role.EMPLOYEE,)

    business = models.ForeignKey(Business, on_delete=models.SET_NULL,null=True, blank=True)
    mobile_number = models.CharField(max_length=10)
    salary=models.IntegerField(default=0)
    address = models.TextField(blank=True,null=True)
    profile_picture=models.ImageField(upload_to="profile_picture",null=True,blank=True)
    work=models.CharField(max_length=10, choices=Work.choices,null=True,blank=True)
    description=models.TextField(blank=True,null=True)

    class Meta:
        db_table ="bma_user"
        constraints = [
            models.UniqueConstraint(fields=["business", "username"], name="unique_username_per_business"),]
        indexes = [
            models.Index(fields=["business", "username"]),
        ]
        permissions = [
            ("can_create_owner", "Can create owner"),
            ("can_create_manager", "Can create manager"),
            ("can_create_employee", "Can create employee"),
            ("can_update_salary", "Can update salary"),
            ("can_update_work", "Can update work"),
        ]

    def __str__(self):
        return self.username
