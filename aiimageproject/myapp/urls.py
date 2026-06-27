from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('image-generator/', views.image_generator_view, name='image_generator'),
    # path('download-image/', views.download_image_api, name='download_image_api'),
    path('download/<str:image_name>/', views.download_image, name='download_image'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
