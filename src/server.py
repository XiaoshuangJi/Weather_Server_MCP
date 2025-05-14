import requests
import json
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv()
mcp = FastMCP('WeatherServer')

def get_adcode(city):
    url = os.getenv('gaode_adcode_url')
    params = {
        'address': city,
        'key': os.getenv('gaode_api_key')
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return "Request failed"
    else:
        response = response.json()
    if response['status'] == '0':
        return 'Request failed'
    return response['geocodes'][0]['adcode']

def get_weather(city):
    adcode = get_adcode(city)
    if adcode == 'Request failed':
        return 'Request failed'
    url = os.getenv('gaode_weather_url')
    params = {
        'city': adcode,
        'key': '0c8f1b0eae0efe43c8e37ef38c6f400d',
    }
    response = requests.get(url, params=params).json()
    if response['status'] == '0':
        return 'Request failed'
    lives = response['lives'][0]
    return (f"🌍 城市：{lives['province'] + lives['city']}\n"
        f"🌤 天气：{lives['weather']}，\n"
        f"🌡 温度：{lives['temperature']}°C\n"
        f"💧 湿度: {lives['humidity']}，\n"
        f"风向：{lives['winddirection']}，风速：{lives['windpower']}级"
    )

@mcp.tool()
def query_weather(city):
    data = get_weather(city)
    return data


if __name__ == '__main__':
    mcp.run(transport='stdio')