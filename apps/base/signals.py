from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.apps import apps

from apps.base.permission.role_permissions import ROLE_PERMISSIONS


def get_model_permissions(app_label, model, actions):
    codenames = [f"{action}_{model}" for action in actions]
    return Permission.objects.filter(
        content_type__app_label=app_label,
        codename__in=codenames
    )


@receiver(post_migrate)
def create_roles(sender, **kwargs):
    for role, config in ROLE_PERMISSIONS.items():
        group, _ = Group.objects.get_or_create(name=role)

        if config == "__all__":
            group.permissions.set(Permission.objects.all())
            continue

        permissions = Permission.objects.none()

        for app_label, actions in config.items():
            permissions |= get_model_permissions(app_label, app_label, actions)

        group.permissions.set(permissions)


User = apps.get_model("user", "User")


@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, **kwargs):
    try:
        group = Group.objects.get(name=instance.role)
        instance.groups.set([group])
    except Group.DoesNotExist:
        pass


# MODULE GROUPS
MODULE_GROUPS = {
    "Invoice Access": ["invoice"],
    "Inventory Access": ["inventory"],
    "Product Access": ["product"],
    "Analytics Access": ["analytics"],
}


@receiver(post_migrate)
def create_module_groups(sender, **kwargs):
    for group_name, app_labels in MODULE_GROUPS.items():
        group, _ = Group.objects.get_or_create(name=group_name)

        perms = Permission.objects.filter(content_type__app_label__in=app_labels)
        group.permissions.set(perms)