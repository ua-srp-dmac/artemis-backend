"""artemis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include


from rest_framework import routers, serializers, viewsets
from artemis.api.api import (
    UserViewSet,
    SiteViewSet,
    GeochemistryViewSet,
    PlotViewSet,
    ReplicateViewSet,
    SiteGeochemistry,
    TreatmentViewSet,
    SiteMineralogy,
    SiteGeochemistryCached,
    SiteMineralogyCached,
    SiteExtractions,
    SiteExtractionsCached
)

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'treatments', TreatmentViewSet)
router.register(r'sites', SiteViewSet)
router.register(r'geochemistry', GeochemistryViewSet)
router.register(r'plots', PlotViewSet)
router.register(r'replicates', ReplicateViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    re_path('^site-geochem-cache/(?P<site_id>.+)/$', SiteGeochemistryCached.as_view()),
    re_path('^site-geochemistry/(?P<site_id>.+)/$', SiteGeochemistry.as_view()),
    
    re_path('^site-mineralogy/(?P<site_id>.+)/$', SiteMineralogy.as_view()),
    re_path('^site-mineralogy-cache/(?P<site_id>.+)/$', SiteMineralogyCached.as_view()),

    re_path('^site-extractions/(?P<site_id>.+)/$', SiteExtractions.as_view()),
    re_path('^site-extractions-cache/(?P<site_id>.+)/$', SiteExtractionsCached.as_view()),

]

