from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path("", views.index, name="index"),
    path("pro/", views.pro, name="pro"),
    path("my-subscription/", views.my_subscription, name="my_subscription"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:service_id>/", views.add_to_cart, name="cart_add"),
    path("cart/remove/<int:service_id>/", views.remove_from_cart, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("order/<int:service_id>/", views.order, name="order"),
]
