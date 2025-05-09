# 🧠 Telegram Bot: Coaching Test

This Telegram bot was created as a test tool for practicing coach, its main purpose is to lead users through a **funnel** and collect the data for further work / analysis. It logs all user actions and contacts into CSV files, provides clear statistics, and includes an admin panel for managing user data.

---

## 🔧 Tools Used

- **[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)** — asynchronous bot framework built on `asyncio`, providing full Telegram Bot API support
- **Python 3.10+** — supports `match-case` and `async/await` syntax
- **`dotenv`** — to load API tokens securely from `.env` files
- **`csv` module** — built-in module for logging structured user data
- **ConversationHandler** — state-driven dialog logic for multi-step interaction
- **Inline & Reply Keyboards** — both inline buttons (admin panel) and reply keyboards (user choices) are used
- **MarkdownV2** — Telegram’s extended markdown is used for styling bot messages with proper escaping
- **pytest** and **unittest.mock** for basic testing and mocks

### Architecture Highlights
- **State tracking** via `ConversationHandler` with named states: `WELCOME`, `QUESTION`, `RESULT`, etc.
- Custom **step priority system** to track user progress accurately in logs
- **Fallback-friendly logic** for missing phone numbers or early exits
- **CSV updates** are non-destructive and avoid overwriting key user data
- **Admin commands** with per-user access control using `ADMIN_IDS`
- **Basic tests** for start, survey, logging and utility sections
- Modular layout using **code folding** (`# <editor-fold>`) for clarity in large scripts

---

## 🔍 Features

### ✅ User Flow
1. **Welcome Message**
2. **Phone Number Request** — optional but encouraged
3. **10 Questions** — 4 answers each with a score
4. **Result Based on Score**:
5. **Funnel Stages**:
   - Personalized stage message based on score
   - CBC (Cognitive Behavioral Coaching) offer
   - Pricing options
   - Final contact + CTA for consultation

### 📦 Data Logging
- `final_signups.csv` — name, phone, score, source, status
- `user_action_log.csv` — step-by-step interaction trail
- Users inactive >24h are marked as **dropped**

### 🔐 Admin Panel
Command: `/admin_panel`

Options:
- 📄 Export Signups CSV  
- 📝 Export Action Log  
- 🕵️ Check Dropped Users  
- 📊 View Stats  

> Only available to user IDs listed in `ADMIN_IDS`

---

## 🧰 How to Set Up

### 1. Clone this repository

```bash
git clone https://github.com/Subsistance/tg-coaching-bot.git
```

### 2. Create .env file

```bash
BOT_TOKEN=your_telegram_bot_token
```
    Get your token from @BotFather

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Main packages used:

    python-telegram-bot

    python-dotenv

### 4. Run the bot

```
python bot.py
```
Requires: Python 3.10+

### 5. Run tests
```
pytest test/
```

## 📊 CSV Format

### final_signups.csv
```
| Timestamp | Username | User ID | Phone | Score | Source | Last Step | Status
```

### user_action_log.csv
```
| Timestamp | User ID | Username | Action | Extra Info |
```