from django.urls import path,include
from screenshot_app import views
urlpatterns = [
    path('user_login/',views.user_login,name='user_login'),

    path('logout/',views.user_logout,name='logout'),

	path('upload_screenshot/',views.upload_screenshot,name='upload_screenshot'),
    path('get_csrf_token/',views.csrf,name='get_csrf_token'),
	
]