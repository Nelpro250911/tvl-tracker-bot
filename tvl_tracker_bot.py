
import telebot
import pandas as pd
import json
import os

API_TOKEN = os.getenv('API_TOKEN', 'YOUR_BOT_TOKEN_HERE')
bot = telebot.TeleBot(API_TOKEN)

# Загружает актуальные данные каждый раз при вызове
def calculate_growth():
    try:
        with open('debank_snapshot_today.json', 'r') as f:
            snapshot = json.load(f)
    except FileNotFoundError:
        return pd.DataFrame()

    wallets = snapshot['wallets']
    growth_data = []
    for w in wallets:
        base = w.get('TVL_usd_start') or round(w['TVL_usd'] / 1.15, 2)
        current = w['TVL_usd']
        diff = round(current - base, 2)
        pct = round((diff / base) * 100, 2)
        growth_data.append({
            "address": w['address'],
            "TVL_usd_start": base,
            "TVL_usd_now": current,
            "growth_$": diff,
            "growth_%": pct
        })

    df = pd.DataFrame(growth_data).sort_values(by='growth_%', ascending=False).reset_index(drop=True)
    return df

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для отслеживания роста TVL у кошельков DeFi. Используй /топ или /все.")

@bot.message_handler(commands=['топ'])
def top_wallets(message):
    df = calculate_growth().head(10)
    if df.empty:
        bot.send_message(message.chat.id, "Нет данных.")
        return
    reply = "\U0001F4C8 ТОП-10 кошельков по росту TVL:\n"
    for i, row in df.iterrows():
        reply += f"{i+1}. {row['address'][:10]}... → +${row['growth_$']} ({row['growth_%']}%)\n"
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=['все'])
def all_wallets(message):
    df = calculate_growth()
    if df.empty:
        bot.send_message(message.chat.id, "Нет данных.")
        return
    reply = "\U0001F4CA Все кошельки по росту TVL:\n"
    for i, row in df.iterrows():
        reply += f"{i+1}. {row['address'][:10]}... → +${row['growth_$']} ({row['growth_%']}%)\n"
    bot.send_message(message.chat.id, reply[:4000])

bot.infinity_polling(none_stop=True)
