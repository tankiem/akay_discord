import os
import discord
import requests
from discord.ext import tasks
from discord import app_commands
from discord.ui import Select, View

TOKEN = os.getenv("DISCORD_TOKEN")
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Thành phố Việt Nam (label hiển thị: giá trị API)
CITIES = {
    "Hà Nội": "Hanoi",
    "TP. Hồ Chí Minh": "Ho Chi Minh",
    "Đà Nẵng": "Da Nang",
    "Huế": "Hue",
    "Cần Thơ": "Can Tho"
}

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},vn&appid={WEATHER_API_KEY}&units=metric&lang=vi"
    try:
        res = requests.get(url)
        data = res.json()

        if res.status_code != 200:
            return f"❌ Không thể lấy thời tiết cho **{city}**."

        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        return (
            f"🌤️ **Thời tiết tại {city}**:\n"
            f"- Trạng thái: {weather.capitalize()}\n"
            f"- Nhiệt độ: {temp}°C\n"
            f"- Độ ẩm: {humidity}%\n"
            f"- Gió: {wind} m/s"
        )
    except Exception as e:
        return "❌ Lỗi khi truy cập API thời tiết."

class CitySelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for label, value in CITIES.items()
        ]
        super().__init__(placeholder="Chọn thành phố...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        city = self.values[0]
        weather_report = get_weather(city)
        await interaction.response.send_message(weather_report, ephemeral=True)

class CityView(View):
    def __init__(self):
        super().__init__()
        self.add_item(CitySelect())

@tree.command(name="weather", description="Xem thời tiết tại thành phố")
async def weather_command(interaction: discord.Interaction):
    await interaction.response.send_message("🌍 Chọn thành phố để xem thời tiết:", view=CityView(), ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"🤖 Bot đã sẵn sàng với tên: {bot.user}")

bot.run(TOKEN)
