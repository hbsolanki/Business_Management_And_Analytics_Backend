from rest_framework.response import Response
from rest_framework import status
from apps.subscription.services.access import can_use_feature

def limit_required(feature_name,usage_field):
    def decorator(view_func):
        def wrapper(self,request,*args,**kwargs):
            allow,message=can_use_feature(
                business=request.user.business,
                feature_name=feature_name,
                usage_field=usage_field
            )

            if not allow:
                return Response({'message':message},status=status.HTTP_403_FORBIDDEN)

            return view_func(self,request,*args,**kwargs)

        return wrapper

    return decorator

def feature_required(feature_name):
    def decorator(view_func):
        def wrapper(self, request, *args, **kwargs):
            allow, message = can_use_feature(
                business=request.user.business,
                feature_name=feature_name,
            )

            if not allow:
                return Response({'message': message}, status=status.HTTP_403_FORBIDDEN)

            return view_func(self, request, *args, **kwargs)

        return wrapper

    return decorator