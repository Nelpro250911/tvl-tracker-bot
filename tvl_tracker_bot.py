import telebot
import pandas as pd
import json

API_TOKEN = '8020814659:AAH01nN7XntKmXMLzzCa3onTqqThyq1PIKc'
bot = telebot.TeleBot(API_TOKEN)

# Загрузка текущих данных роста TVL
with open('debank_snapshot_today.json', 'r') as f:
    snapshot = json.load(f)

# Эмуляция прироста на основе сохранённого файла (можно заменить реальной базой)
def calculate_growth():
    wallets = snapshot['wallets']
    growth_data = []
    for w in wallets:
        base = w['TVL_usd']
        growth = round(base * 1.15, 2)  # 15% прирост эмуляция
        diff = round(growth - base, 2)
        pct = round((diff / base) * 100, 2)
        growth_data.append({
            "address": w['address'],
            "TVL_usd_start": base,
            "TVL_usd_now": growth,
            "growth_$": diff,
            "growth_%": pct
        })
    df = pd.DataFrame(growth_data).sort_values(by='growth_%', ascending=False).reset_index(drop=True)
    return df

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для отслеживания роста TVL у кошельков DeFi. Используй /топ чтобы увидеть лучших за неделю, /все чтобы увидеть всех, или /адрес <кошелек> для анализа.")

@bot.message_handler(commands=['топ'])
def top_wallets(message):
    df = calculate_growth().head(10)
    reply = "\U0001F4C8 ТОП-10 кошельков по росту TVL:\n"
    for i, row in df.iterrows():
        reply += f"{i+1}. {row['address'][:10]}... → +${row['growth_$']} ({row['growth_%']}%)\n"
    bot.send_message(message.chat.id, reply)

@bot.message_handler(commands=['все'])
def all_wallets(message):
    df = calculate_growth()
    reply = "\U0001F4CA Все кошельки по росту TVL:\n"
    for i, row in df.iterrows():
        reply += f"{i+1}. {row['address'][:10]}... → +${row['growth_$']} ({row['growth_%']}%)\n"
    bot.send_message(message.chat.id, reply[:4000])  # ограничение Telegram

@bot.message_handler(commands=['адрес'])
def address_info(message):
    parts = message.text.strip().split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Используй: /адрес <кошелек>")
        return
    addr = parts[1].lower()
    df = calculate_growth()
    row = df[df['address'].str.lower() == addr]
    if row.empty:
        bot.send_message(message.chat.id, "Адрес не найден в базе")
    else:
        r = row.iloc[0]
        msg = (f"Анализ {r['address'][:12]}...\n"
               f"Начальный TVL: ${r['TVL_usd_start']}\n"
               f"Текущий TVL: ${r['TVL_usd_now']}\n"
               f"Рост: +${r['growth_$']} ({r['growth_%']}%)")
        bot.send_message(message.chat.id, msg)

bot.polling(none_stop=True)
