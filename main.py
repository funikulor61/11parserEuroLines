import time
from itertools import cycle
from pars import euroLines


PROXIES = [
    "http://109.199.119.160:80",
    "http://185.199.229.156:7492",
]
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Mozilla/5.0 (Macintosh; Intel Win98 X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0'
]
count_change = 3
proxy_cycle = cycle(PROXIES)
ua_cycle = cycle(USER_AGENTS)


def rotate(parser, k):
    if k > 0 and k % count_change == 0:
        parser.changeProxyAndUA(next(proxy_cycle), next(ua_cycle))


def main():
    parser = euroLines(
        'https://www.eurolines.lt/ru',
        'Минск',
        'Вильнюс',
        '2026',
        '11',
        '01',
        next(proxy_cycle),
        next(ua_cycle)
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
            rotate(parser, k)
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
            rotate(parser, k)               #<-- смена прокси/UA по кругу

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
