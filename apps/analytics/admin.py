from django.contrib import admin
from apps.subscription.models import Subscription,Plan

admin.site.register(Subscription)
admin.site.register(Plan)