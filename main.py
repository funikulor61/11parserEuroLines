import time
from pars import euroLines
from selenium.common.exceptions import TimeoutException


def main():
    parser = euroLines(
        'https://www.eurolines.lt/ru',
        'Минск',
        'Вильнюс',
        '2026',
        '11',
        '01',
        "http://109.199.119.160:80",
        'Mozilla/5.0 (Windows NT 10.0; Win98; x64; rv:130.0) Gecko/20100101 Firefox/130.0'
    )
    date1, date2_future = parser.generateDates()
    time.sleep(5)

    try:
        parser.acceptCockie()
    except Exception as e:
        print(f"cookie-баннер не найден: {e}")

    try:
        parser.rezdelForBus1()
        for k, (i, j) in enumerate(zip(date1, date2_future)):
        
            if k > 0:                   #запуск ввода и парсинга картчек
                parser.rows.append(['========================= СЛЕДУЮЩАЯ ДАТА ========================='])
                parser.boundaries.append(len(parser.rows))
            parser.enterDataFirstAddress(i, j)
            parser.parseResults(i, j)
        parser.rezdelForBus2()
        parser.driver.get(parser.link)
        time.sleep(3)
        try:
            parser.acceptCockie()
        except Exception:
            pass
        for k, (i, j) in enumerate(zip(date1, date2_future)): #запуск ввода и парсинга картчек
            if k > 0:   #enumerate делает счетчик k для отслеживания текущей итерации
                parser.rows.append(['========================= СЛЕДУЮЩАЯ ДАТА ========================='])
                parser.boundaries.append(len(parser.rows))
            parser.enterDataSecondAddress(i, j)
            parser.parseResults(i, j)
    finally:
        if getattr(parser, 'rows', None):       #проверка успел ли парсер собрать инфу , после запись
            parser.saveCsv()
        parser.driver.quit()


if __name__ == "__main__":
    main()