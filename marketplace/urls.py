from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'), # Must match 'product_detail'
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('search/', views.search_view, name='search'),
    path('profile/', views.profile_view, name='profile'),
    path('cart/', views.cart_view, name='cart'), 
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('become-vendor/', views.become_vendor_landing, name='become_vendor'),
    path('create-store/', views.create_store_logic, name='create_store'),
    path('vendor-terms/', views.terms_and_conditions, name='terms_and_conditions'),
    path('activate-vendor/', views.final_onboarding_step, name='activate_vendor'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('my-store/', views.my_store_profile, name='my_store_profile'),
    path('add-product/', views.add_product, name='add_product'),
    path('product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('settings/', views.settings_page, name='settings_page'),
    path('store/<int:vendor_id>/', views.store_detail, name='store_detail'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('follow/<int:vendor_id>/', views.toggle_follow, name='toggle_follow'),
    path('followed-stores/', views.followed_stores_view, name='followed_stores'),
    path('partner-with-us/', views.business_onboarding_view, name='business_onboarding'),
    path('send-message/<int:product_id>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/chat/<int:product_id>/<int:other_user_id>/', views.chat_thread, name='chat_thread'),
    path('product/<int:product_id>/report/', views.report_product, name='report_product'),
]

