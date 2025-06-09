import os
import sys
import time
from dotenv import load_dotenv
from imapclient import IMAPClient
from telegram import Bot

# 載入環境變數
for env_file in ('config.env', 'telegram.env', 'account.env'):
    if not os.path.isfile(env_file):
        print(f"缺少環境檔: {env_file}，請填入必要參數後再試。")
        sys.exit(1)

load_dotenv('config.env')
load_dotenv('telegram.env')
load_dotenv('account.env')

# 讀取設定
MODE = os.getenv('MODE', 'UNSEEN')
INTERVAL = int(os.getenv('INTERVAL_MIN', 3)) * 60
ENABLE_TELEGRAM = os.getenv('ENABLE_TELEGRAM', 'true').lower() == 'true'
SAVE_EML = os.getenv('SAVE_EML', 'true').lower() == 'true'
EML_DIR = os.getenv('EML_DIR', './eml_storage')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

EMAIL = os.getenv('ACCOUNT_EMAIL')
PASSWORD = os.getenv('ACCOUNT_PASSWORD')
IMAP_HOST = os.getenv('IMAP_HOST')

# 如果 Telegram 配置不完整，關閉推播
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    ENABLE_TELEGRAM = False

# 檢查帳號設定
if not (EMAIL and PASSWORD and IMAP_HOST):
    print("請確認 account.env 已設定 ACCOUNT_EMAIL、ACCOUNT_PASSWORD、IMAP_HOST。")
    sys.exit(1)

# 建立資料夾
if SAVE_EML and not os.path.isdir(EML_DIR):
    os.makedirs(EML_DIR)

# 初始化 Telegram Bot
bot = Bot(token=TELEGRAM_TOKEN) if ENABLE_TELEGRAM else None


def fetch_and_process():
    with IMAPClient(IMAP_HOST) as client:
        client.login(EMAIL, PASSWORD)
        client.select_folder('INBOX')
        criteria = 'ALL' if MODE == 'ALL' else 'UNSEEN'
        messages = client.search(criteria)
        for uid, message_data in client.fetch(messages, ['RFC822']).items():
            raw = message_data[b'RFC822']
            # 存檔
            if SAVE_EML:
                path = os.path.join(EML_DIR, f'{uid}.eml')
                with open(path, 'wb') as f:
                    f.write(raw)
            # 推播
            if ENABLE_TELEGRAM:
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f'New mail UID: {uid}')
            # 如果只抓 UNSEEN，可以標記為已讀
            if MODE != 'ALL':
                client.set_flags(uid, '\\Seen')


if __name__ == '__main__':
    while True:
        fetch_and_process()
        time.sleep(INTERVAL)
