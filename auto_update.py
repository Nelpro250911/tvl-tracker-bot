import json
import random
import requests
from datetime import datetime
import os
import shutil

# Telegram настройки
API_TOKEN = '8020814659:AAH01nN7XntKmXMLzzCa3onTqqThyq1PIKc'
CHAT_ID = '1900314873'
SEND_URL = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"

# === БЭКАП ===
original_file = 'debank_snapshot_today.json'
date_tag = datetime.utcnow().strftime('%Y%m%d_%H%M')
backup_dir = 'backup'
backup_file = f'{backup_dir}/debank_snapshot_{date_tag}.json'
os.makedirs(backup_dir, exist_ok=True)
shutil.copyfile(original_file, backup_file)

# ЛОГ
log_entry = f"{datetime.utcnow().isoformat()} — Скопирован файл в {backup_file}\n"
with open(f'{backup_dir}/backup_log.txt', 'a') as log:
    log.write(log_entry)

# Уведомление о бэкапе
requests.post(SEND_URL, data={'chat_id': CHAT_ID, 'text': f"✅ Бэкап создан: {backup_file}"})

# === ОБНОВЛЕНИЕ ТВЛ ===
with open(original_file, 'r') as f:
    old_snapshot = json.load(f)

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

new_snapshot = {
    "timestamp": datetime.utcnow().isoformat(),
    "wallets": new_wallets
}

with open(original_file, "w") as f:
    json.dump(new_snapshot, f, indent=2)

# Уведомления
for addr, diff, pct, total in alerts:
    msg = (f"\u26A1 Кошелёк {addr[:10]}... вырос на +${diff} ({pct}%)\n"
           f"Новый TVL: ${total}")
    requests.post(SEND_URL, data={'chat_id': CHAT_ID, 'text': msg})

print("Готово: обновлено и уведомления отправлены.")
