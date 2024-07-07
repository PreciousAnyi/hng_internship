from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, OrganizationListView, OrganizationDetailView, OrganizationCreateView, AddUserToOrganizationView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('api/users/<str:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('api/organisations/', OrganizationListView.as_view(), name='org-list'),
    path('api/organisations/<str:pk>/', OrganizationDetailView.as_view(), name='org-detail'),
    path('api/organisations/create/', OrganizationCreateView.as_view(), name='org-create'),
    path('api/organisations/<str:pk>/users/', AddUserToOrganizationView.as_view(), name='org-add-user'),
]
