
import json
import random
from datetime import datetime
import pandas as pd
import telebot
import os
import shutil

# Токен бота
API_TOKEN = os.getenv('API_TOKEN', 'YOUR_BOT_TOKEN_HERE')
bot = telebot.TeleBot(API_TOKEN)

# === БЭКАП ===
original_file = 'debank_snapshot_today.json'
date_tag = datetime.utcnow().strftime('%Y%m%d_%H%M')
backup_file = f'backup/debank_snapshot_{date_tag}.json'
os.makedirs('backup', exist_ok=True)
shutil.copyfile(original_file, backup_file)

# ЛОГ
log_entry = f"{datetime.utcnow().isoformat()} — Скопирован файл в {backup_file}\n"
with open('backup/backup_log.txt', 'a') as log:
    log.write(log_entry)

# Уведомление о бэкапе
bot.send_message(chat_id=1900314873, text=f"✅ Бэкап создан: {backup_file}")

# === ОБНОВЛЕНИЕ ТВЛ ===
# Загрузка старого снимка
with open(original_file, 'r') as f:
    old_snapshot = json.load(f)

# Генерация нового TVL со случайным приростом 5-25%
new_wallets = []
alerts = []
for w in old_snapshot['wallets']:
    base = w['TVL_usd']
    growth_factor = 1 + random.uniform(0.05, 0.25)
    new_balance = round(base * growth_factor, 2)
    diff = round(new_balance - base, 2)
    pct = round((diff / base) * 100, 2)
    new_wallets.append({
        "address": w['address'],
        "TVL_usd": new_balance
    })
    if pct >= 15:
        alerts.append((w['address'], diff, pct, new_balance))

# Сохраняем новый снимок
new_snapshot = {
    "timestamp": datetime.utcnow().isoformat(),
    "wallets": new_wallets
}

with open(original_file, "w") as f:
    json.dump(new_snapshot, f, indent=2)

# Отправка уведомлений
for addr, diff, pct, total in alerts:
    msg = (f"⚡ Кошелёк {addr[:10]}... вырос на +${diff} ({pct}%)\n"
           f"Новый TVL: ${total}")
    bot.send_message(chat_id=1900314873, text=msg)

print("Обновление завершено. Уведомления отправлены. Бэкап сохранён.")
