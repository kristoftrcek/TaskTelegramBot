import typing, random
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

class Client:
    def __init__(self, username: str, bal: int):
        self.username = username
        self.balance = bal
        self.bet = 0
    
    def setterBalance(self, bal: int) -> None:
        self.balance = bal

    def setterUsername(self, username: str) -> None:
        self.username = username
    
    def setterBet(self, bet: int) -> None:
        self.bet = bet

TOKEN = "7264668247:AAGCI-ZoxNxNl7OpYsSrZGTRwGwJgjJ87Vc"
BOT_USERNAME = "@hiringTaskGamblingBot"
client = Client("No username", 0)

CHOOSING, VERIFY = range(2)
GET_BALANCE = range(1)
CHOOSE_AMT, CHOOSE_SIDE, PLAY_AGAIN = range(3)


# Choosing username commands
async def start_command(update, context):
    await update.message.reply_text("This is a gambling bot!\Please, choose your username.")
    return CHOOSING

async def setusername_state(update, context):
    pendingUsername: str = update.message.text
    client.setterUsername(pendingUsername)
    await update.message.reply_text("Are you sure you want to choose this username?", reply_markup=ReplyKeyboardMarkup([["Yes!", "No."]], one_time_keyboard=True))
    return VERIFY

async def verifyusername_state(update, context):
    response: str = update.message.text
    if response == "Yes!":
        await update.message.reply_text(f"Hello {client.username}. You can now play /coinflip game.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        client.setterUsername("")
        await update.message.reply_text("Type your username again.", reply_markup=ReplyKeyboardRemove())
        return CHOOSING


async def setbalance_command(update, context):
    await update.message.reply_text("Tell me your balance.")
    return GET_BALANCE

async def getbalance_command(update, context):
    bal: str = update.message.text
    if bal.isnumeric():
        client.setterBalance(int(bal))
        await update.message.reply_text(f"You have now {client.balance}€ on your account.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Balance must be an integer.")
        return GET_BALANCE


async def balance_command(update, context):
    await update.message.reply_text(f"You have {client.balance}€ on your account.")


async def coinflip_command(update, context):
    await update.message.reply_text("How much would you like to bet?")
    return CHOOSE_AMT

async def chooseamt_state(update, context):
    response: str = update.message.text
    if response.isnumeric():
        amt = int(response)
        if amt > client.balance:
            await update.message.reply_text(f"You only have {client.balance}€. Choose different amount.")
            return CHOOSE_AMT
        else:
            client.setterBet(amt)
            await update.message.reply_text("Do you bet on 0 or 1?", reply_markup=ReplyKeyboardMarkup([["0", "1"]], one_time_keyboard=True))
            return CHOOSE_SIDE
    else:
        await update.message.reply_text("You have to specify your amount in positive integer.")
        return CHOOSE_AMT

async def chooseside_state(update, context):
    response = int(update.message.text)
    coin = random.randrange(0,1)
    if response == coin:
        client.setterBalance(client.balance + client.bet)
        await update.message.reply_text(f"Congratulations! You guessed correctly. You get {client.bet}€.\nDo you want to play again?",  reply_markup=ReplyKeyboardMarkup([["Yes!", "No."]], one_time_keyboard=True))
        client.setterBet(0)
        return PLAY_AGAIN
    else:
        client.setterBalance(client.balance - client.bet)
        await update.message.reply_text(f"Sorry. You guessed incorrectly. You lost {client.bet}€.\nDo you want to play again?",  reply_markup=ReplyKeyboardMarkup([["Yes!", "No."]], one_time_keyboard=True))
        client.setterBet(0)
        return PLAY_AGAIN

async def playagain_state(update, context):
    response = update.message.text
    if response == "No.":
        await update.message.reply_text("Ok, maybe next time...", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text("How much would you like to bet?", reply_markup=ReplyKeyboardRemove())
        return CHOOSE_AMT

# Conversations
username_conv = ConversationHandler(
    entry_points=[CommandHandler("start", start_command)],
    states={
        CHOOSING: [MessageHandler(filters.TEXT, setusername_state)],
        VERIFY: [MessageHandler(filters.TEXT, verifyusername_state)]
    },
    fallbacks=[CommandHandler("start", start_command)]
)

setbalance_conv = ConversationHandler(
    entry_points=[CommandHandler("setbalance", setbalance_command)],
    states={
        GET_BALANCE: [MessageHandler(filters.TEXT, getbalance_command)],
    },
    fallbacks=[CommandHandler("setbalance", setbalance_command)]
)

coinflip_conv = ConversationHandler(
    entry_points=[CommandHandler("coinflip", coinflip_command)],
    states={
        CHOOSE_AMT: [MessageHandler(filters.TEXT, chooseamt_state)],
        CHOOSE_SIDE: [MessageHandler(filters.Regex("^(0|1)$"), chooseside_state)],
        PLAY_AGAIN: [MessageHandler(filters.Regex("^(Yes!|No.)$"), playagain_state)]
    },
    fallbacks=[CommandHandler("coinflip", coinflip_command)]
)

print("Starting GamblingBot...")
app = Application.builder().token(TOKEN).build()
app.add_handler(username_conv)
app.add_handler(setbalance_conv)
app.add_handler(CommandHandler("balance", balance_command))
app.add_handler(coinflip_conv)

print("Polling...")
app.run_polling(poll_interval=3, allowed_updates=Update.ALL_TYPES)
