from django.contrib.auth.models import Group

WORK_GROUP_MAP = {
    "INVOICE": "Invoice Access",
    "INVENTORY": "Inventory Access",
    "PRODUCT": "Product Access",
    "ANALYTICS":"Analytics Access"
}


def sync_user_work_group(user):
    if not user.work:
        return user

    group_name = WORK_GROUP_MAP.get(user.work)
    if not group_name:
        return user

    try:
        target_group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return user

    # already correct group → skip
    if user.groups.filter(id=target_group.id).exists():
        return user

    # remove previous module groups
    old_groups = Group.objects.filter(name__in=WORK_GROUP_MAP.values())
    user.groups.remove(*old_groups)

    # add correct group
    user.groups.add(target_group)

    return user
