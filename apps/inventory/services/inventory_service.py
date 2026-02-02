from apps.inventory.models import Inventory

def create_inventory(business):
    return Inventory.objects.create(business=business)