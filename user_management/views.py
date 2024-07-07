from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Organization
from .serializers import UserSerializer, OrganizationSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import LoginSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            errors = []
            for field, messages in serializer.errors.items():
                for message in messages:
                    errors.append({'field': field, 'message': message})
            return Response({'errors': errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        self.perform_create(serializer)
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        
        # Create default organization
        org_name = f"{user_data['firstName']}'s Organisation"
        organization = Organization.objects.create(name=org_name)
        organization.users.add(user)  # Add user to organization

        refresh = RefreshToken.for_user(user)
        return Response({
            'status': 'success',
            'message': 'Registration successful',
            'data': {
                'accessToken': str(refresh.access_token),
                'user': {
                    'userId': user.userId,
                    'firstName': user.firstName,
                    'lastName': user.lastName,
                    'email': user.email,
                    'phone': user.phone,
                }
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'status': 'success',
            'message': 'Login successful',
            'data': {
                'accessToken': str(refresh.access_token),
                'user': {
                    'userId': user.userId,
                    'firstName': user.firstName,
                    'lastName': user.lastName,
                    'email': user.email,
                    'phone': user.phone,
                }
            }
        }, status=status.HTTP_200_OK)
        
class OrganizationListView(generics.ListCreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        org = serializer.save()
        org.users.add(self.request.user)
        return org

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            org = self.perform_create(serializer)
            return Response({
                'status': 'success',
                'message': 'Organisation created successfully',
                'data': {
                    'orgId': org.orgId,
                    'name': org.name,
                    'description': org.description
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrganizationDetailView(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

class OrganizationCreateView(generics.CreateAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        org_name = serializer.validated_data['name']
        org = serializer.save()
        org.users.add(self.request.user)

        return Response({
            'status': 'success',
            'message': 'Organisation created successfully',
            'data': {
                'orgId': org.orgId,
                'name': org.name,
                'description': org.description
            }
        }, status=status.HTTP_201_CREATED)
    
class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.get_queryset()
        # Use 'pk' from URL to filter queryset
        obj = get_object_or_404(queryset, userId=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

class OrganizationDetailView(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.get_queryset()
        # Use 'pk' from URL to filter queryset
        obj = get_object_or_404(queryset, orgId=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

class AddUserToOrganizationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        org_id = self.kwargs['pk']
        user_id = request.data.get('userId')

        try:
            organization = Organization.objects.get(orgId=org_id)
            user = User.objects.get(userId=user_id)
        except (Organization.DoesNotExist, User.DoesNotExist):
            return Response({
                'status': 'Bad request',
                'message': 'Organization or user not found',
                'statusCode': 404
            }, status=status.HTTP_404_NOT_FOUND)

        organization.users.add(user)
        return Response({
            'status': 'success',
            'message': 'User added to organization successfully',
        })
