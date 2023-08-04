import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup, any_state


# Conversation states
class FormStates(StatesGroup):
    SELECT_NETWORK = State()
    TOKEN_ADDRESS = State()
    DESCRIPTION = State()


dict_network = {
    'ETH': 'ethereum',
    'BSC': 'bsc'
}

bot_token = '6668255939:AAGx4pw4yzpQbLqD-PgakV-laF2NhMJWc84'
bot = Bot(token=bot_token)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


async def start(message: types.Message):
    reply_keyboard = [['ETH', 'BSC']]
    await message.reply(
        "Hello! I am TokenInfoBot. Send /cancel at any time to stop.\n"
        "Please select the network:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    await FormStates.SELECT_NETWORK.set()


async def received_network(message: types.Message, state: FSMContext):
    user_choice = message.text
    await state.update_data(network=user_choice)
    await message.reply(
        f"Great! You selected {user_choice}. Now, please enter the token address:"
    )
    await FormStates.TOKEN_ADDRESS.set()


async def received_token_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['token_address'] = message.text

    await message.reply("Thanks! Now, please enter the token description:")
    await FormStates.DESCRIPTION.set()


async def received_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

    chat_id = message.chat.id
    async with state.proxy() as data:
        network = data['network']
        token_address = data['token_address']
        description = data['description']

    # Store the chat_id and relevant data in job context for each group
    context_data = (chat_id, network, token_address, description)

    # Schedule sending token info every 60 seconds, passing context as a whole
    dp.loop.create_task(send_token_info(context_data))

    await message.reply_text("You will now receive token info every 60 seconds. "
                             "Send /cancel to stop receiving updates.")
    await state.finish()


async def process_get_transaction_by_token(network, token_address, description):
    pass


async def send_token_info(context_data):
    chat_id, network, token_address, description = context_data

    token_info_1 = "First piece of token info."
    token_info_2 = "Second piece of token info."

    # Compose the response message
    response_message = (
        f"Network: {network}\n"
        f"Token Address: {token_address}\n"
        f"Description: {description}\n"
        f"Info 1: {token_info_1}\n"
        f"Info 2: {token_info_2}"
    )

    await bot.send_message(chat_id=chat_id, text=response_message, parse_mode=ParseMode.MARKDOWN)


async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply_text("You have unsubscribed from token info updates.", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['start'], state=any_state)
async def start_handler(message: types.Message, state: FSMContext):
    await start(message)


@dp.message_handler(lambda message: message.text in ['ETH', 'BSC'], state=FormStates.SELECT_NETWORK)
async def received_network_handler(message: types.Message, state: FSMContext):
    await received_network(message, state)


@dp.message_handler(state=FormStates.TOKEN_ADDRESS, content_types=types.ContentTypes.TEXT)
async def received_token_address_handler(message: types.Message, state: FSMContext):
    await received_token_address(message, state)


@dp.message_handler(state=FormStates.DESCRIPTION, content_types=types.ContentTypes.TEXT)
async def received_description_handler(message: types.Message, state: FSMContext):
    await received_description(message, state)


@dp.message_handler(commands=['cancel'], state=any_state)
async def cancel_handler(message: types.Message, state: FSMContext):
    await cancel(message, state)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
