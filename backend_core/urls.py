from django.conf import settings
from rest_framework import (
    serializers,
    routers,
    viewsets
)
from rest_framework.decorators import (
    permission_classes,
    authentication_classes,
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
import importlib
import re
from rest_api.views import applyOption, applyPagination

ITEM_COUNT_PER_PAGE = 20

def get_serializer(model_class):
    class ApiSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_class
            fields = '__all__'
    return ApiSerializer

def get_viewset(model_class):
    config = getattr(model_class, 'rest_api')()
    
    @permission_classes([config['permission'],])
    @authentication_classes([JWTAuthentication,])
    class ApiViewSet(viewsets.ModelViewSet):
        queryset = model_class.objects.all().order_by('-id')
        serializer_class = get_serializer(model_class)

        def list(self, request):
            if not config['list']:
                raise Response({'message':'not support'}, status=404)
            page = request.GET.get('page', 1)
            count = request.GET.get('count_per_page', ITEM_COUNT_PER_PAGE)
            queryset = applyOption(request, self.queryset)
            res = applyPagination(queryset, self.serializer_class, page, count)
            return Response(res, status=200)

        def create(self, request):
            if not config['create']:
                raise Response({'message':'not support'}, status=404)
            return super().create(request)

        def retrieve(self, request, pk=None):
            if not config['retrieve']:
                raise Response({'message':'not support'}, status=404)
            return super().retrieve(request, pk)

        def update(self, request, pk=None):
            if not config['update']:
                raise Response({'message':'not support'}, status=404)
            return super().update(request, pk, partial=True)

        def destroy(self, request, pk=None):
            if not config['destroy']:
                raise Response({'message':'not support'}, status=404)
            return super().destroy(request, pk)

    return ApiViewSet

def load_models():
    mod = importlib.import_module(settings.API_MODELS)
    model_classes = {}
    for class_name in dir(mod):
        if class_name.startswith('__'): continue
        if class_name == 'models': continue
        model_class = getattr(mod, class_name)
        if hasattr(model_class, 'rest_api'):
            model_classes[class_name] = model_class
    return model_classes

router = routers.DefaultRouter()
for model_name, model_class in load_models().items():
    parts = re.findall('[A-Z][^A-Z]*',model_name)
    router.register(r'%s'%'/'.join(parts).lower(), get_viewset(model_class))
urlpatterns = router.urls
