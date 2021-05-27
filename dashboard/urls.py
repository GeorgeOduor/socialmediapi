from django.urls import path

from .views import fb_dashboard,lk_dashboard,tw_dashboard,nba
app_name = 'dashboard'
urlpatterns = [
    path('', fb_dashboard, name="facebook"),
    path('linkedin/', lk_dashboard, name="linkedin"),
    path('twitter/', tw_dashboard, name="twitter"),
    path('nba/', nba, name="nba")
]
