# Stage One Task - Backend Track API Documentation

## Overview

This API provides a simple endpoint to greet a visitor and provide weather-related information based on their IP address.

## Endpoint

- **URL**: `GET /api/hello`
- **Base URL**: Replace `https://preciousanyi.pythonanywhere.com/api/hello/` with your server origin.

## Parameters

- `visitor_name` (optional): Specifies the name of the visitor. If not provided, defaults to "Guest".

## Response

```json
{
  "client_ip": "127.0.0.1",
  "location": "New York",
  "greeting": "Hello, Mark!, the temperature is 11 degrees Celcius in New York"
}
