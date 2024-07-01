from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import HelloSerializer
import geocoder
import requests
import urllib.parse

def sanitize_input(input_string):
    """Sanitize and clean user input."""
    # Decode URL-encoded characters
    input_string = urllib.parse.unquote(input_string)
    # Remove surrounding quotes if they exist
    if input_string.startswith('"') and input_string.endswith('"'):
        input_string = input_string[1:-1]
    return input_string

def get_weather_and_location(ip):
    """Retrieve weather and location information based on the IP address."""
    try:
        location = geocoder.ip(ip)
        if location.city:
            city = location.city
        else:
            city = "unknown"
        api_key = settings.WEATHERAPI_KEY
        response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no")
        response.raise_for_status()
        data = response.json()
        temperature = data['current']['temp_c']
        return city, temperature
    
    except (requests.exceptions.RequestException, KeyError, ValueError) as e:
        print(f"Error retrieving weather and location data: {e}")
        return 'Unknown', None

@api_view(['GET'])
def hello(request):
    visitor_name = request.GET.get('visitor_name', 'Guest')
    visitor_name = sanitize_input(visitor_name)
    
    # Determine client IP using geocoder
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

    city, temperature = get_weather_and_location(client_ip)
    if temperature is None:
        temperature = "unknown"
    
    greeting = f"Hello, {visitor_name}! The temperature is {temperature} degrees Celsius in {city}."

    data = {
        "client_ip": client_ip,
        "location": city,
        "greeting": greeting
    }

    # Serialize data using the HelloSerializer
    serializer = HelloSerializer(data=data)
    serializer.is_valid()

    return Response(serializer.data, status=status.HTTP_200_OK)
