from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from src.moex_API import MoexAPI


class CashBot(MoexAPI):
    def __init__(self, token):
        super().__init__()
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.tickets = []  # Список для хранения текстов
        self.init_handlers()

    def init_handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        addtext_handler = CommandHandler('addtext', self.add_text)
        self.dispatcher.add_handler(addtext_handler)

        showtexts_handler = CommandHandler('showtexts', self.show_texts)
        self.dispatcher.add_handler(showtexts_handler)

        prices_handler = CommandHandler('showprices', self.show_prices)
        self.dispatcher.add_handler(prices_handler)

        message_handler = MessageHandler(None, self.handle_message)
        self.dispatcher.add_handler(message_handler)

    def add_text(self, update: Update, context: CallbackContext):
        """Начало процесса добавления текста"""
        context.user_data['adding_text'] = True
        update.message.reply_text('Введите тикер компании, которую вы хотите добавить:')

    def start(self, update: Update, context: CallbackContext):
        """Начало работы с ботом"""
        keyboard = [
            [KeyboardButton("Добавить акцию")],
            [KeyboardButton("Удалить акцию")],
            [KeyboardButton("Показать акции")],
            [KeyboardButton("Узнать цены")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            'Добро пожаловать! Бот добавляет акции московской биржи в избранное для отслеживания цен',
            reply_markup=reply_markup)

    def handle_message(self, update: Update, context: CallbackContext):
        """Обработка текстовых сообщений"""
        keyboard = [
            [KeyboardButton("Добавить акцию")],
            [KeyboardButton("Удалить акцию")],
            [KeyboardButton("Показать акции")],
            [KeyboardButton("Узнать цены")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        text = update.message.text.strip().upper()

        if text == 'ДОБАВИТЬ АКЦИЮ':
            context.user_data['action'] = 'add'
            update.message.reply_text("Введите тикер акции для добавления например mtss или MTSS",
                                      reply_markup=reply_markup)
        elif text == 'УДАЛИТЬ АКЦИЮ':
            context.user_data['action'] = 'remove'
            update.message.reply_text("Введите тикер акции для удаления:", reply_markup=reply_markup)
        elif text == 'ПОКАЗАТЬ АКЦИИ':
            self.show_texts(update, context)
        elif text == 'УЗНАТЬ ЦЕНЫ':
            self.show_prices(update, context)
        elif 'action' in context.user_data:
            action = context.user_data['action']

            if action == 'add':
                if text not in self.tickets:
                    self.tickets.append(text)
                    update.message.reply_text(f"Акция {text} добавлена.", reply_markup=reply_markup)
                else:
                    update.message.reply_text(f"Акция {text} уже есть в списке.", reply_markup=reply_markup)
            elif action == 'remove':
                if text in self.tickets:
                    self.tickets.remove(text)
                    update.message.reply_text(f"Акция {text} удалена.", reply_markup=reply_markup)
                else:
                    update.message.reply_text(f"Акция {text} нет в списке.", reply_markup=reply_markup)

            del context.user_data['action']
        else:
            update.message.reply_text("Используйте кнопки для добавления или удаления акций.",
                                      reply_markup=reply_markup)

    def show_texts(self, update: Update, context: CallbackContext):
        """Отображение всех добавленных текстов"""
        keyboard = [
            [KeyboardButton("Добавить акцию")],
            [KeyboardButton("Удалить акцию")],
            [KeyboardButton("Показать акции")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        if self.tickets:
            texts_str = '\n'.join(self.tickets)
            update.message.reply_text(f"Добавленные акции:\n{texts_str}", reply_markup=reply_markup)
        else:
            update.message.reply_text("Нет добавленных акций.", reply_markup=reply_markup)

    def show_prices(self, update: Update, context: CallbackContext):
        """Отображение текущих цен всех добавленных акций"""
        if self.tickets:
            prices_message = self.get_all_stocks_info(self.tickets)
            update.message.reply_text(prices_message)
        else:
            update.message.reply_text("Нет добавленных акций.")

    def run(self):
        self.updater.start_polling()
        self.updater.idle()
