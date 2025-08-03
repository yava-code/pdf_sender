# ежедневная отправка
import aiogram
import os
from dotenv import load_dotenv
load_dotenv()
token = int(os.getenv('BOT_TOKEN'))
time = int(os.getenv('TIME')) #in hours
