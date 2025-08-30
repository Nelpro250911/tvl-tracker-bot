
import telebot
import pandas as pd
import json
import os

API_TOKEN = os.getenv('API_TOKEN', 'YOUR_BOT_TOKEN_HERE')
bot = telebot.TeleBot(API_TOKEN, parse_mode='HTML')

def calculate_growth():
    try:
        with open('debank_snapshot_today.json', 'r') as f:
            snapshot = json.load(f)
    except FileNotFoundError:
        return pd.DataFrame()

    wallets = snapshot['wallets']
    growth_data = []
    for w in wallets:
        current = w.get('TVL_usd', 0)
        base = round(current / 1.15, 2)

        # Фильтрация
        if base < 100 or current < 100:
            continue
        diff = round(current - base, 2)
        if diff < 100:
            continue

        pct = round((diff / base) * 100, 2)
        growth_data.append({ "address": w['address'], "TVL_usd_start": base,
                             "TVL_usd_now": current, "growth_$": diff, "growth_%": pct })

    df = pd.DataFrame(growth_data).sort_values(by='growth_$', ascending=False).reset_index(drop=True)
    return df


def format_wallet_line(i, row):
    link = f"https://debank.com/profile/{row['address']}"
    color_emoji = "🟢" if row['growth_$'] >= 0 else "🔴"
    return f"{color_emoji} <b><a href='{link}'>{row['address'][:10]}...</a></b> → {row['growth_$']:+.2f}$ ({row['growth_%']:+.2f}%)"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для отслеживания роста TVL у кошельков DeFi. Используй /топ или /все.")

@bot.message_handler(commands=['топ'])
def top_wallets(message):
    df = calculate_growth().head(10)
    if df.empty:
        bot.send_message(message.chat.id, "Нет данных.")
        return
    reply = "<b>📈 ТОП-10 кошельков по росту TVL:</b>\n\n"
    for i, row in df.iterrows():
        reply += format_wallet_line(i, row) + "\n"
    bot.send_message(message.chat.id, reply, disable_web_page_preview=True)

@bot.message_handler(commands=['все'])
def all_wallets(message):
    df = calculate_growth()
    if df.empty:
        bot.send_message(message.chat.id, "Нет данных.")
        return
    reply_lines = [format_wallet_line(i, row) for i, row in df.iterrows()]
    for chunk_start in range(0, len(reply_lines), 50):  # делим на части по 50 записей
        chunk = reply_lines[chunk_start:chunk_start+50]
        reply = "<b>📊 Кошельки по росту TVL:</b>\n\n" + "\n".join(chunk)
        bot.send_message(message.chat.id, reply, disable_web_page_preview=True)

bot.remove_webhook()
bot.infinity_polling()
