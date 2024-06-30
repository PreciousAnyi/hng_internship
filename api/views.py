from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import HelloSerializer
import requests

def get_location(ip):
    """Retrieve location information based on the IP address."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving location: {e}")
        return {}
    
    
def get_temperature(city):
    """Retrieve temperature information for the specified city."""
    api_key =settings.OPENWEATHERMAP_API_KEY
    response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}")
    data = response.json()
    if response.status_code == 200:
        return data['main']['temp']
    return None


@api_view(['GET'])
def hello(request):
    visitor_name = request.GET.get('visitor_name', 'Guest')
    client_ip = request.META.get('REMOTE_ADDR', '8.8.8.8')

    location = get_location(client_ip)
    city = location.get('city', 'Unknown')

    temperature = get_temperature(city)
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