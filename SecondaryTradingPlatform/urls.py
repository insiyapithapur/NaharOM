from django.contrib import admin
from django.urls import path , include
# from django.conf import settings
# from django.conf.urls.static import static
# from django.conf import settings
# from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('UserFeatures.urls')),
    path('appAdmin/',include('AdminFeatures.urls')),
    path('irr/',include('IRRCalc.urls'))
]
urlpatterns += staticfiles_urlpatterns()
