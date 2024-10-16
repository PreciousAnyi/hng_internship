from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import HelloSerializer
import requests
import urllib.parse
from ipinfo import getHandler

def sanitize_input(input_string):
    """Sanitize and clean user input."""
    input_string = urllib.parse.unquote(input_string)
    if input_string.startswith('"') and input_string.endswith('"'):
        input_string = input_string[1:-1]
    return input_string

def get_city_from_ip(ip):
    """Retrieve city name based on the IP address using ipinfo."""
    handler = getHandler(settings.IPINFO_API_KEY)
    try:
        details = handler.getDetails(ip)
        return details.city
    except Exception as e:
        print(f"Error retrieving city from IP: {e}")
        return 'Unknown'

def get_weather_and_location(city):
    """Retrieve weather information based on the city using WeatherAPI."""
    api_key = settings.WEATHERAPI_KEY
    try:
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
    
    # Determine client IP
    client_ip = request.META.get('HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR'))
    if isinstance(client_ip, list):
        client_ip = client_ip[0].strip()
    elif client_ip:
        client_ip = str(client_ip).strip()
    else:
        client_ip = '8.8.8.8'  # Fallback to a default IP if not found

    # Log the client IP for debugging
    print(f"Client IP: {client_ip}")
    
    # Handle local testing scenario
    if client_ip == '127.0.0.1':
        client_ip = '102.91.93.2'  # Use an external IP for testing

    city = get_city_from_ip(client_ip)
    city, temperature = get_weather_and_location(city)
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
