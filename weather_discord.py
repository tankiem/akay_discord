import os
import requests
import discord
import time
from dotenv import load_dotenv
from discord.ext import tasks

# Load biến môi trường
load_dotenv("bot_discord.env")

TOKEN = os.getenv("DISCORD_TOKEN")
channel_id_str = os.getenv("CHANNEL_ID")
if not channel_id_str:
    raise ValueError("❌ Không tìm thấy CHANNEL_ID.")
CHANNEL_ID = int(channel_id_str)
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

intents = discord.Intents.default()
intents.message_content = True  # Cho phép đọc nội dung tin nhắn
client = discord.Client(intents=intents)

# Hàm lấy thời tiết
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Hanoi,vn&appid={WEATHER_API_KEY}&units=metric&lang=vi"
    try:
        res = requests.get(url)
        data = res.json()

        description = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        weather_report = f"""🌤️ **Thời tiết Hà Nội:**
- Trạng thái: {description.capitalize()}
- Nhiệt độ: {temp}°C
- Độ ẩm: {humidity}%
- Gió: {wind} m/s
"""
        return weather_report
    except Exception as e:
        print("Lỗi khi lấy thời tiết:", e)
        return "⚠️ Không lấy được thông tin thời tiết."

# Gửi thời tiết tự động lúc 7h sáng
@client.event
async def on_ready():
    print(f'✅ Bot đang chạy với tài khoản: {client.user}')
    send_weather.start()

@tasks.loop(minutes=1)
async def send_weather():
    now = time.localtime()
    if now.tm_hour == 7 and now.tm_min == 0:
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            report = get_weather()
            await channel.send(report)
        else:
            print("❌ Không tìm thấy kênh!")

# Gửi thời tiết khi người dùng gõ !weather
@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Không trả lời chính mình

    if message.content.lower().startswith("!weather"):
        report = get_weather()
        await message.channel.send(report)

client.run(TOKEN)
