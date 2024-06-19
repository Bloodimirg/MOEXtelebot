import requests


class MoexAPI:
    """Класс для работы с API Мосбиржи"""

    def __init__(self):
        self.url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities/"
        self.headers = {'User-Agent': 'HH-User-Agent'}

    def get_trading_status(self, ticker):
        """Метод для проверки статуса торгов."""
        url = self.url + f"{ticker}.json"
        response = requests.get(url, headers=self.headers)
        data = response.json()
        stock_data = data.get('marketdata', {}).get('data', [])

        if not stock_data:
            return None, f"Акция {ticker} не найдена или торги закрыты."

        columns = data['marketdata']['columns']
        try:
            tradingstatus_index = columns.index('TRADINGSTATUS')
            boardid_index = columns.index('BOARDID')
        except ValueError:
            return None, f"Акция {ticker}: одна из необходимых колонок не найдена в данных."

        for entry in stock_data:
            if len(entry) > tradingstatus_index and entry[boardid_index] == "TQRB":
                return entry[tradingstatus_index], None
            elif len(entry) > tradingstatus_index and entry[boardid_index] == "SMAL":
                return entry[tradingstatus_index], None
            elif len(entry) > tradingstatus_index and entry[boardid_index] == "SPEQ":
                return entry[tradingstatus_index], None

        return None, f"Акция {ticker}: не найдено ни одного режима торгов из TQRB, SMAL, SPEQ."

    def get_last_price(self, ticker):
        """Метод для получения последней цены (LAST)."""
        url = self.url + f"{ticker}.json"
        response = requests.get(url, headers=self.headers)
        data = response.json()
        stock_data = data.get('marketdata', {}).get('data', [])

        if not stock_data:
            return None, f"Акция {ticker} не найдена или торги закрыты."

        columns = data['marketdata']['columns']
        try:
            last_index = columns.index('LAST')
            boardid_index = columns.index('BOARDID')
        except ValueError:
            return None, f"Акция {ticker}: одна из необходимых колонок не найдена в данных."

        for entry in stock_data:
            if len(entry) > last_index and entry[boardid_index] == "TQBR" and entry[last_index] is not None:
                return entry[last_index], None
            elif len(entry) > last_index and entry[boardid_index] == "SMAL" and entry[last_index] is not None:
                return entry[last_index], None
            elif len(entry) > last_index and entry[boardid_index] == "SPEQ" and entry[last_index] is not None:
                return entry[last_index], None

        return None, f"Акция {ticker}: цена LAST не найдена."

    def get_close_price(self, ticker):
        """"Метод для получения цены закрытия (CLOSE)."""
        url = self.url + f"{ticker}.json"
        response = requests.get(url, headers=self.headers)
        data = response.json()
        stock_data = data.get('marketdata', {}).get('data', [])

        if not stock_data:
            return None, f"Акция {ticker} не найдена."

        columns = data['marketdata']['columns']
        try:
            close_index = columns.index('CLOSEPRICE')
            boardid_index = columns.index('BOARDID')
        except ValueError:
            return None, f"Акция {ticker}: одна из необходимых колонок не найдена в данных."

        for entry in stock_data:
            if len(entry) > close_index and entry[boardid_index] == "TQBR" and entry[close_index] is not None:
                return entry[close_index], None
            if len(entry) > close_index and entry[boardid_index] == "SMAL" and entry[close_index] is not None:
                return entry[close_index], None
            if len(entry) > close_index and entry[boardid_index] == "SPEQ" and entry[close_index] is not None:
                return entry[close_index], None

        return None, f"Акция {ticker}: цена CLOSE не найдена."

    def get_stock_info(self, ticker):
        """Метод собирающий информацию о статусе торгов, текущей цене, названии компании."""
        status, status_error = self.get_trading_status(ticker)  # Получаем статус торгов
        name_company = self.get_name_company(ticker)

        if status_error:
            return status_error

        if status == "N":
            last_price, last_error = self.get_last_price(ticker)
            close_price, close_error = self.get_close_price(ticker)

            if last_error and close_error:
                return f"{name_company}: цена отсутствует."
            elif not last_error:
                return f"{name_company} | торги ⛔️: последняя цена {last_price} руб."
            elif not close_error:
                return f"{name_company} | торги ⛔️: цена закрытия {close_price} руб."
        if status != "N":
            last_price, last_error = self.get_last_price(ticker)
            close_price, close_error = self.get_close_price(ticker)
            if last_error and close_error:
                return f"{name_company} | торги 👍: ни LAST, ни CLOSE цена не найдены."
            elif not last_error:
                return f"{name_company} | торги 👍: последняя цена {last_price} руб."
            elif not close_error:
                return f"{name_company} | торги 👍: цена закрытия {close_price} руб."

    def get_name_company(self, ticker):
        """Метод получающий название компании"""
        url = self.url + f"{ticker}.json"
        response = requests.get(url, headers=self.headers)
        data = response.json()
        stock_data = data.get('securities', {}).get('data', [])
        if not stock_data:
            return None, f"Акция {ticker} не найдена."

        columns = data['securities']['columns']
        try:
            name_index = columns.index('SHORTNAME')
            boardid_index = columns.index('BOARDID')
        except ValueError:
            return None, f"Акция {ticker}: одна из необходимых колонок не найдена в данных."

        for entry in stock_data:

            if len(entry) > name_index and entry[boardid_index] == "TQBR" and entry[name_index] is not None:
                return entry[name_index]
            elif len(entry) > name_index and entry[boardid_index] == "TQBR" and entry[name_index] is not None:
                return entry[name_index]
            elif len(entry) > name_index and entry[boardid_index] == "TQBR" and entry[name_index] is not None:
                return entry[name_index]

        return None, f"Акция {ticker}: название не найдено."

    def get_all_stocks_info(self, tickers):
        """Метод для получения информации по всем тикерам."""
        messages = []
        for ticker in tickers:
            stock_info = self.get_stock_info(ticker)
            messages.append(stock_info)
        return '\n'.join(messages)


if __name__ == "__main__":
    tiker = MoexAPI()
    print(tiker.get_all_stocks_info(["MTSS", "TATN", "SNGSP", "SBER", "GAZP"]))
