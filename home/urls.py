from django.urls import path
from .views import *

app_name = 'home'

urlpatterns = [
    path('',HomeView.as_view(),name = 'home'),
    path('detail/<slug>',DetailView.as_view(),name = 'detail'),
    path('category/<slug>',CategoryView.as_view(),name = 'category'),
    path('subcategory/<slug>',SubCategoryView.as_view(),name = 'subcategory'),
    path('search',SearchView.as_view(),name = 'search'),
    path('signup',signup,name = 'signup'),

]
