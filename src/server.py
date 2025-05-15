import requests
import json
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


load_dotenv()
mcp = FastMCP('WeatherServer')

def get_adcode(city: str) -> str:
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

def query_live_weather(city: str) -> str:
    adcode = get_adcode(city)
    if adcode == 'Request failed':
        return 'Request failed'
    url = os.getenv('gaode_weather_url')
    params = {
        'city': adcode,
        'key': os.getenv('gaode_api_key'),
        'extensions': 'base'
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

def query_forecast_weather(city: str) -> str:
    adcode = get_adcode(city)
    if adcode == 'Request failed':
        return 'Request failed'
    url = os.getenv('gaode_weather_url')
    params = {
        'city': adcode,
        'key': os.getenv('gaode_api_key'),
        'extensions': 'all'
    }
    response = requests.get(url, params=params).json()
    if response['status'] == '0':
        return 'Request failed'
    forecasts = response['forecasts'][0]['casts']
    data = ''
    for cast in forecasts[:-1]:
        data += (f"白天天气：{cast['dayweather']}，温度：{cast['daytemp']}°C，风向：{cast['daywind']}，风速：{cast['daypower']}级；" 
                f"夜间天气：{cast['nightweather']}, 温度：{cast['nighttemp']}°C，风向：{cast['nightwind']}, 风速：{cast['nightpower']}级。")
    data = '未来三天天气情况为：' + data
    return data




@mcp.tool()
def get_live_weather_by_cityname(city: str) -> str:
    return query_live_weather(city)

@mcp.tool()
def get_forecast_weather_by_cityname(city: str) -> str:
    return query_forecast_weather(city)


if __name__ == '__main__':
    mcp.run(transport='stdio')
