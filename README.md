# discordBotWithStats

Python Discord bot that scrapes data from [FiveThirtyEight's 2024 Election Forecast](https://projects.fivethirtyeight.com/2024-election-forecast/) and updates the bot's nickname with election statistics.

## Prerequisites

When creating a Discord bot through the [Discord Developer Portal](https://discord.com/developers/applications), make sure you enable both **SERVER MEMBERS INTENT** and **MESSAGE CONTENT INTENT**.

![image](https://github.com/user-attachments/assets/24208756-290a-480c-9c85-7e8d690ae890)

### Required Libraries
You'll need to install:
- `beautifulsoup4`
- `requests`
- `discord.py`

### Bot Invitation
To invite the bot to a server:
1. Select "bot" under scopes.
2. Under Bot Permissions, enable:
   - View Channels
   - Send Messages
   - Read Message History
   - Change Nickname

### Environment Variables
I used PyCharm to store my environment variables, but you can create an `.env` file if you prefer. Never share your token with anyone. The `.env` file should include:

```plaintext
AUTHORIZED_USER_ID=<YOUR_USER_ID>
TOKEN=<DISCORD_BOT_TOKEN>
```
## Notes

As of October 27, 2024, this program scrapes data successfully. However, future changes to the website's layout or structure may prevent successful scraping.

### Website Screenshot

![Website Screenshot](https://github.com/user-attachments/assets/5ed60aad-9273-4bd6-868e-109920a93ed2)

### Python Program Screenshot

![Python Program Screenshot](https://github.com/user-attachments/assets/17b656f7-4ee3-4abd-b26c-64d4d2353ba8)

---

Special thanks to [FiveThirtyEight](https://projects.fivethirtyeight.com) for collecting and providing election data. This bot relies on manual calls to scrape data to avoid overloading the website. Please use it responsibly.
