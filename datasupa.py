import os
import pandas as pd
import asyncio
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_GID = os.getenv("SHEET_GID")
SERVICE_LINE = os.getenv("SERVICE_LINE")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_IDS = os.getenv("CHAT_IDS").split(",")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"

print(f"Monitoring sheet: {SHEET_URL}", flush=True)

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Convert column index → Excel-style letter
def col_to_letter(col_index):
    letter = ""
    while col_index >= 0:
        letter = chr(col_index % 26 + 65) + letter
        col_index = col_index // 26 - 1
    return letter


async def check_sheet():
    print(f"Checking sheet at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    try:
        df = pd.read_csv(SHEET_URL)
    except Exception as e:
        print(f"Failed to read sheet: {e}", flush=True)
        return

    print(f"Total rows in sheet: {len(df)}", flush=True)

    # Filter NRA rows
    nra_rows = df[
        (df["Status"].astype(str).str.strip() == "NRA") &
        (df["Service Line"].astype(str).str.strip() == SERVICE_LINE)
    ]

    print(f"Found {len(nra_rows)} NRA rows for {SERVICE_LINE}", flush=True)

    bot = Bot(token=TELEGRAM_TOKEN)

    status_col_index = df.columns.get_loc("Status")
    status_col_letter = col_to_letter(status_col_index)

    for index, row in nra_rows.iterrows():
        unique_id = str(row.get("Order Id")).strip()

        if not unique_id or unique_id.lower() == "none":
            continue

        # Try inserting into Supabase
        # If it fails (duplicate), skip
        try:
            supabase.table("notified_orders").insert({
                "order_id": unique_id
            }).execute()
        except Exception:
            # Already exists (duplicate primary key)
            continue

        # If insert succeeded → send Telegram
        row_number = index + 2  # header + 1-based index
        cell = f"{status_col_letter}{row_number}"

        sheet_link = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{SPREADSHEET_ID}/edit#gid={SHEET_GID}&range={cell}"
        )

        message = (
            f"⚠ NRA Found ({SERVICE_LINE})\n"
            f"Order Id: {unique_id}\n"
            f"Row: {row_number}\n"
            f"Open Sheet: {sheet_link}"
        )

        for chat_id in CHAT_IDS:
            try:
                await bot.send_message(
                    chat_id=chat_id.strip(),
                    text=message
                )
            except Exception as e:
                print(f"Failed to send to {chat_id}: {e}", flush=True)

    print("Done checking.", flush=True)


async def runner():
    await check_sheet()


if __name__ == "__main__":
    asyncio.run(runner())
