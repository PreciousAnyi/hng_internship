from rest_framework import serializers
from .models import User, Organization
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    userId = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'password', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate(self, data):
        if not data.get('firstName'):
            raise serializers.ValidationError({'firstName': 'This field is required'})
        if not data.get('lastName'):
            raise serializers.ValidationError({'lastName': 'This field is required'})
        if not data.get('email'):
            raise serializers.ValidationError({'email': 'This field is required'})
        return data

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['orgId', 'name', 'description']

    def validate_name(self, value):
        # Add custom validation for the 'name' field if needed
        if len(value) < 1:
            raise serializers.ValidationError("Required and cannot be null")
        return value

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')


        if email and password:
            user = authenticate(username=email, password=password)
            data['user'] = user
        else:
            raise serializers.ValidationError('Must include "email" and "password"')
        
        return data