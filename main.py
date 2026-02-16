import asyncio
from telegram import Bot

async def send_notification():
    # Replace with your actual token
    bot = Bot("8583248099:AAFk3mWlLP3GrsrlYAyKEs8mJIJgzAjdsus")
    
    # Replace with YOUR numerical User ID
    USER_ID = 7366298774 

    try:
        await bot.send_message(
            chat_id=USER_ID, 
            text="normal cinta dharay thakai jabe na",
            disable_notification=False # This ensures the phone vibrates/sounds
        )
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have messaged the bot first and the ID is correct.")

if __name__ == "__main__":
    asyncio.run(send_notification())




# 8583248099:AAFk3mWlLP3GrsrlYAyKEs8mJIJgzAjdsus