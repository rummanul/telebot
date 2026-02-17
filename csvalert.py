import os
import pandas as pd
from telegram import Bot
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_GID = os.getenv("SHEET_GID")

SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS").split(",")
print(f"Monitoring sheet: {SHEET_URL}", flush=True)
print(f"Service Line: {os.getenv('SERVICE_LINE')}", flush=True)

STATE_FILE = "notified.json"

# Extract from your sheet URL



def load_notified():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return set()
                return set(json.loads(content))
        except:
            return set()
    return set()


def save_notified(data):
    with open(STATE_FILE, "w") as f:
        json.dump(list(data), f)


# Convert column index → Excel-style letter
def col_to_letter(col_index):
    letter = ""
    while col_index >= 0:
        letter = chr(col_index % 26 + 65) + letter
        col_index = col_index // 26 - 1
    return letter


async def check_sheet():
    print(f"Checking sheet at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)  

    df = pd.read_csv(SHEET_URL)

    print(f"Total rows in sheet: {len(df)}", flush=True)

    nra_rows = df[
        (df["Status"].astype(str).str.strip() == "NRA") &
        (df["Service Line"].astype(str).str.strip() == os.getenv("SERVICE_LINE"))
    ]

    print(f"Found {len(nra_rows)} NRA rows for {os.getenv('SERVICE_LINE')}", flush=True)

    bot = Bot(token=TELEGRAM_TOKEN)
    notified = load_notified()

    status_col_index = df.columns.get_loc("Status")
    status_col_letter = col_to_letter(status_col_index)

    for index, row in nra_rows.iterrows():
        unique_id = str(row.get("Order Id"))

        if unique_id not in notified:
            row_number = index + 2  # header + 1-based index
            cell = f"{status_col_letter}{row_number}"

            sheet_link = (
                f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={SHEET_GID}&range={cell}"
            )

            message = (
                f"⚠ NRA Found ({os.getenv("SERVICE_LINE")})\n"
                f"Order Id: {row.get('Order Id', 'Unknown')}\n"
                f"Row: {row_number}\n"
                f"Open Sheet: {sheet_link}"
            )

            for chat_id in CHAT_IDS:
                try:
                    await bot.send_message(chat_id=chat_id.strip(), text=message)
                except Exception as e:
                    print(f"Failed to send to {chat_id}: {e}", flush=True)
            if unique_id and str(unique_id).strip().lower() != "none":
                notified.add(unique_id)

    save_notified(notified)
    print("Done checking.", flush=True)

async def runner():
    while True:
        await check_sheet()
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(runner())
