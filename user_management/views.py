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
from django.core.exceptions import ValidationError

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
            return Response({
                'errors': errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
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

        except Exception as e:
            return Response({
                'status': 'Bad request',
                'message': 'Registration unsuccessful',
                'statusCode': status.HTTP_400_BAD_REQUEST
            })


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            errors = []
            for field, messages in serializer.errors.items():
                for message in messages:
                    errors.append({'field': field, 'message': message})
            return Response({
                'errors': errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            # Proceed with authentication logic
            user = serializer.validated_data['user']
            # Generate tokens
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

        except Exception as e:
            return Response({
                'status': 'Bad request',
                'message': 'Authentication failed',
                'statusCode': status.HTTP_401_UNAUTHORIZED
            })
        
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

        if not serializer.is_valid():
            errors = []
            for field, messages in serializer.errors.items():
                for message in messages:
                    errors.append({'field': field, 'message': message})
            return Response({
                'errors': errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        try:
            
            # Validation passed, proceed with organization creation
            org = self.perform_create(serializer)
            
            return Response({
                'status': 'success',
                'message': 'Organization created successfully',
                'data': {
                    'orgId': org.orgId,
                    'name': org.name,
                    'description': org.description
                }
            }, status=status.HTTP_201_CREATED)


        except Exception as e:
            # Handle any other unexpected errors
            return Response({
                'status': 'Bad request',
                'message': 'Client error',
                'statusCode': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
    
class OrganizationDetailView(generics.RetrieveAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    
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

class AddUserToOrganizationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        org_id = self.kwargs['pk']
        user_id = request.data.get('userId')

        try:
            # Attempt to retrieve organization and user
            organization = Organization.objects.get(orgId=org_id)
            user = User.objects.get(userId=user_id)

            # Add user to organization
            organization.users.add(user)
            
            return Response({
                'status': 'success',
                'message': 'User added to organization successfully',
            })

        except Organization.DoesNotExist:
            return Response({
                'status': 'Bad request',
                'message': 'Organization not found',
            }, status=status.HTTP_404_NOT_FOUND)

        except User.DoesNotExist:
            return Response({
                'status': 'Bad request',
                'message': 'User not found',
            }, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as e:
            # Handle validation error for UUID format
            return Response({
                'status': 'Bad request',
                'message': str(e),  # Display the validation error message
            }, status=status.HTTP_400_BAD_REQUEST)
