import discord
from discord.ext import tasks
import pandas as pd

TOKEN = 'MTQzOTU3MTA2NTEzNDEyNTE5OA.GYeCCU.z6GmO1blcbneFxytgei1ZHPjcEGW78K3eHqG0M'
CHANNEL_ID = 1224805068423954574  # ID канала для уведомлений

URLS = [
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQtWLuvwe2dUH7gG3otl_GyEh-8-vAo9OKI3qWGgdvkd3SQ3a-bDN4nL7Ii5PJXqH7YCp-VgH8dSwqM/pubhtml?gid=746705175&single=true",
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQtWLuvwe2dUH7gG3otl_GyEh-8-vAo9OKI3qWGgdvkd3SQ3a-bDN4nL7Ii5PJXqH7YCp-VgH8dSwqM/pubhtml?gid=1097564074&single=true"
]

class SheetBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_rows = [0, 0] # Храним количество строк для каждой таблицы

    async def setup_hook(self):
        self.check_sheets.start()

    async def on_ready(self):
        print(f'Бот {self.user} запущен.')

    @tasks.loop(seconds=60) # Интервал проверки (60 сек)
    async def check_sheets(self):
        channel = self.get_channel(CHANNEL_ID)
        if not channel: return

        for i, url in enumerate(URLS):
            try:
                # Читаем таблицу через pandas
                df = pd.read_html(url, header=1)[0]
                current_rows = len(df)

                # Если строк стало больше, отправляем уведомление
                if self.last_rows[i] != 0 and current_rows > self.last_rows[i]:
                    new_data = df.iloc[-1].to_dict() # Берем последнюю строку
                    msg = f"🔔 **Новый отчет в таблице {i+1}!**\n" + \
                          "\n".join([f"**{k}**: {v}" for k, v in new_data.items() if "Unnamed" not in str(k)])
                    await channel.send(msg)

                self.last_rows[i] = current_rows
            except Exception as e:
                print(f"Ошибка парсинга таблицы {i+1}: {e}")

intents = discord.Intents.default()
client = SheetBot(intents=intents)
client.run(TOKEN)
