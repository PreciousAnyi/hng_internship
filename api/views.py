from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .serializers import HelloSerializer
import requests


def get_weather_and_location(ip):
    """Retrieve weather and location information based on the IP address."""
    api_key = settings.WEATHERAPI_KEY
    try:
        response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={ip}")
        response.raise_for_status()
        data = response.json()
        city = data['location']['name']
        temperature = data['current']['temp_c']
        return city, temperature
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving weather and location data: {e}")
        return 'Unknown', None

@api_view(['GET'])
def hello(request):
    visitor_name = request.GET.get('visitor_name', 'Guest')
    client_ip = request.META.get('REMOTE_ADDR', '8.8.8.8')

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