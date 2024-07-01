from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import HelloSerializer
import requests

def get_city_from_ip(ip):
    """Retrieve city name based on the IP address."""
    try:
        response = requests.get(f"https://api.weatherapi.com/v1/ip.json?key={settings.WEATHERAPI_KEY}&q={ip}")
        response.raise_for_status()
        data = response.json()
        city = data['city']
        return city
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving city from IP: {e}")
        return 'Lagos'


def get_weather_and_location(ip):
    """Retrieve weather and location information based on the IP address."""
    city = get_city_from_ip(ip)
    api_key = settings.WEATHERAPI_KEY
    try:
        response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no")
        response.raise_for_status()
        data = response.json()
        temperature = data['current']['temp_c']
        return city, temperature
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving weather and location data: {e}")
        return 'Unknown', None

@api_view(['GET'])
def hello(request):
    visitor_name = request.GET.get('visitor_name', 'Guest')
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '8.8.8.8')).split(',')[0].strip()

    city, temperature = get_weather_and_location(client_ip)
    if temperature is None:
        temperature = "unknown"
    
    greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {city}"

    data = {
        "client_ip": client_ip,
        "location": city,
        "greeting": greeting
    }

    # Serialize data using the HelloSerializer
    serializer = HelloSerializer(data=data)
    serializer.is_valid() 

    return Response(serializer.data, status=status.HTTP_200_OK)