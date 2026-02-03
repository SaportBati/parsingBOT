import discord
from discord.ext import tasks, commands
import pandas as pd
import base64

# Закодированный токен (обязательно смените его в панели разработчика, так как он был засвечен!)
ENCODED_TOKEN = "TVRRd05VYzVNVEk0T0RRNE9UWTNNRGd4LkdRWm1TTS45U25GNXhkTEc1eU1lbU9pTFVNDTN3UlhLS1RvZlNDZUp5R3ZCd00="
CHANNEL_ID = 1224805068423954574

URLS = [
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQtWLuvwe2dUH7gG3otl_GyEh-8-vAo9OKI3qWGgdvkd3SQ3a-bDN4nL7Ii5PJXqH7YCp-VgH8dSwqM/pubhtml?gid=746705175&single=true",
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQtWLuvwe2dUH7gG3otl_GyEh-8-vAo9OKI3qWGgdvkd3SQ3a-bDN4nL7Ii5PJXqH7YCp-VgH8dSwqM/pubhtml?gid=1097564074&single=true"
]

class SheetBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="/", intents=intents)
        self.last_rows = [0] * len(URLS)

    async def setup_hook(self):
        self.check_sheets_loop.start()

    async def fetch_updates(self):
        updates = []
        for i, url in enumerate(URLS):
            try:
                # Читаем таблицу
                df_list = pd.read_html(url, header=1)
                if not df_list:
                    continue
                
                df = df_list[0]
                current_rows = len(df)
                
                # Проверка новых строк
                if self.last_rows[i] != 0 and current_rows > self.last_rows[i]:
                    new_data = df.iloc[-1].to_dict()
                    msg = f"🔔 **Новый отчет (Таблица {i+1})!**\n" + \
                          "\n".join([f"**{k}**: {v}" for k, v in new_data.items() if "Unnamed" not in str(k)])
                    updates.append(msg)
                
                self.last_rows[i] = current_rows
            except Exception as e:
                print(f"Ошибка таблицы {i+1}: {e}")
        return updates

    @tasks.loop(seconds=60)
    async def check_sheets_loop(self):
        channel = self.get_channel(CHANNEL_ID)
        if not channel: 
            return
        
        updates = await self.fetch_updates()
        for m in updates:
            await channel.send(m)

bot = SheetBot()

@bot.command(name="check")
async def check(ctx):
    messages = await bot.fetch_updates()
    if messages:
        for m in messages: 
            await ctx.send(m)
    else:
        await ctx.send("✅ Изменений в таблицах нет.")

# Декодирование с очисткой от лишних символов
try:
    token = base64.b64decode(ENCODED_TOKEN).decode('utf-8').strip()
    bot.run(token)
except Exception as e:
    print(f"Критическая ошибка при запуске: {e}")
