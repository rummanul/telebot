import asyncio
from telegram import Bot

async def main():
    # Note: Keep your token private! 
    bot = Bot("8583248099:AAFk3mWlLP3GrsrlYAyKEs8mJIJgzAjdsus")

    await bot.delete_webhook(drop_pending_updates=True) # Changed to True to clear old junk
    
    print("Waiting for messages...")
    offset = 0  # Initialize offset

    while True:
        # Pass the offset to only get NEW messages
        updates = await bot.get_updates(offset=offset, timeout=30)

        for u in updates:
            if u.message:
                print("Chat ID:", u.message.chat.id)
                print("Text:", u.message.text)
            
            # Update the offset to the latest update_id + 1
            offset = u.update_id + 1

asyncio.run(main())