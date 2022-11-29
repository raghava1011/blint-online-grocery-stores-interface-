from django.urls import path
from . import views
urlpatterns = [
    path('',views.homepage,name='homepage'),
    path("login", views.login,name="login"),
    path("logout", views.logout,name="logout"),
    path("register", views.register , name="register"),
    #path('home',views.home,name="home"),
    path('vhome',views.vhome,name='vhome'),
    path('pending',views.pending,name='pending'),
    path('myorders',views.myorders,name='myorders'),
    path('accept',views.accept_order,name='accept_order'),
    path('pastorders',views.pastorders,name='pastorders'),
    path('shop',views.shop,name="shop"),
    path('cart',views.cart,name="cart"),
    path('homepage',views.homepage,name="homepage"),
    path('notfound',views.notfound,name="notfound")

]
