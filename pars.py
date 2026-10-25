import os
import sys
import csv
import time
import getpass
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
from urllib.parse import urlparse


logging.basicConfig(                            #настройка логера
    filename='app_execution.log',
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True,
    encoding='utf-8'
)

DAYS = ["понедельник", "вторник", "среда", "четверг","пятница", "суббота", "воскресенье"]


class euroLines:
    def __init__(self, link, go_from , go_to , year, month , day , proxy, user_agent):      #задаем переменные для класса
        self.link = link
        self.options = Options()
        self.proxy = proxy
        self.parsed = urlparse(self.proxy)  #разбить ссылку на hostname и port
        self.proxy_host = self.parsed.hostname
        self.proxy_port = self.parsed.port
        self.options.set_preference("general.useragent.override", user_agent)
        self.options.set_preference("network.proxy.type", 1)                            
        self.options.set_preference("network.proxy.http", self.proxy_host)
        self.options.set_preference("network.proxy.http_port", int(self.proxy_port))
        self.options.set_preference("network.proxy.ssl", self.proxy_host)
        self.options.set_preference("network.proxy.ssl_port", int(self.proxy_port))
        self.options.set_capability("pageLoadStrategy", "eager")                    #ждем только DOM
        self.driver = webdriver.Firefox(options = self.options)
        self.driver.set_page_load_timeout(60)       #ожидание в 60 секунд
        self.driver.get(self.link)
        self.links_list = []
        self.go_from = go_from
        self.go_to = go_to
        self.date_list = []
        self.date_list_future = []
        self.end_date = datetime(int(year), int(month), int(day)).date()
        self.current_date = datetime.today().date()
        self.username = getpass.getuser()
        self.script_name = os.path.basename(sys.argv[0])    #чтобы узнать какая функция выполняется
        self.rows = []
        self.boundaries = []

    def acceptCockie(self):                 #принятие куки
        logging.info(f"Начало | Пользователь: {self.username} | Скрипт: {self.script_name}")
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/a[2]"))
            ).click()
            time.sleep(2)
            logging.info(f"cookie-баннер закрыт")
        except TimeoutException:            #если куки не появилось
            logging.info(f"cookie-баннер не найден, пропускаю")

    def generateDates(self):            #создать списки и txt файлы(для наглядности дат)
        logging.info(f"Начало | Пользователь: {self.username} | Скрипт: {self.script_name}")
        d = self.current_date
        while d <= self.end_date:
            self.date_list.append(d.strftime('%Y-%m-%d'))
            future_date = d + timedelta(days=7)
            self.date_list_future.append(future_date.strftime('%Y-%m-%d'))
            d += timedelta(days=1)

        with open('dateList.txt', 'w', encoding='utf-8') as f:      #создаем txt файл дат 
            f.write('\n'.join(self.date_list) + '\n')

        with open('dateListFuture.txt', 'w', encoding='utf-8') as f:    #создаем txt файл будущих дат
            f.write('\n'.join(self.date_list_future) + '\n')

        logging.info(f"Скрипт {self.script_name} успешно завершил работу.")
        return self.date_list , self.date_list_future

    def enterDataFirstAddress(self, i, j):              #функция заполнения полей на главной странице(через аэропорт)
        logging.info(f"Начало | Пользователь: {self.username} | Скрипт: {self.script_name}")
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, 'route-from')))

        inputFrom = self.driver.find_element(By.ID , 'route-from')
        inputFrom.send_keys(self.go_from)
        inputFrom.send_keys(Keys.ENTER)
        time.sleep(2)
        inputTo = self.driver.find_element(By.ID , 'route-to')
        inputTo.send_keys(self.go_to)
        time.sleep(2)
        inputTo.send_keys(Keys.ENTER)

        departureDate = self.driver.find_element(By.ID , 'depart-date')
        departureDate.send_keys(Keys.CONTROL, "a")
        departureDate.send_keys(Keys.BACKSPACE)
        departureDate.send_keys(i)
        time.sleep(1)

        checkbox = self.driver.find_element(By.ID, "ticket-backward-checkbox")
        self.driver.execute_script("arguments[0].click();", checkbox)
        returnDate = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, 'return-date')))
        returnDate.send_keys(Keys.CONTROL, "a")
        returnDate.send_keys(Keys.BACKSPACE)
        returnDate.send_keys(j)
        time.sleep(2)

        btn_find = self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Искать поездку"]')
        btn_find.click()
        time.sleep(4)
        logging.info(f"Скрипт {self.script_name} успешно завершил работу.")

    def enterDataSecondAddress(self, i, j):                         #функция заполнения полей на главной странице(через автовокзал)
        logging.info(f"Начало | Пользователь: {self.username} | Скрипт: {self.script_name}")
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, 'route-from')))

        inputFrom = self.driver.find_element(By.ID , 'route-from')
        inputFrom.send_keys(self.go_from)
        inputFrom.send_keys(Keys.ENTER)
        time.sleep(2)
        inputTo = self.driver.find_element(By.ID , 'route-to')
        inputTo.send_keys(self.go_to)
        time.sleep(2)
        inputTo.send_keys(Keys.ARROW_DOWN)
        inputTo.send_keys(Keys.ENTER)

        departureDate = self.driver.find_element(By.ID , 'depart-date')
        departureDate.send_keys(Keys.CONTROL, "a")
        departureDate.send_keys(Keys.BACKSPACE)
        departureDate.send_keys(i)
        time.sleep(1)

        checkbox = self.driver.find_element(By.ID, "ticket-backward-checkbox")
        self.driver.execute_script("arguments[0].click();", checkbox)
        returnDate = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, 'return-date')))
        returnDate.send_keys(Keys.CONTROL, "a")
        returnDate.send_keys(Keys.BACKSPACE)
        returnDate.send_keys(j)
        time.sleep(2)

        btn_find = self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Искать поездку"]')
        btn_find.click()
        time.sleep(4)
        logging.info(f"Скрипт {self.script_name} успешно завершил работу.")

    def rezdelForBus1(self):                       #функция раздела в csv файле для наглядности (с начала идут маршруты до аэропорта, после идет автовокзал)
        self.rows.append(['=========================================== Аэропорт ВИЛЬНЮС ========================='])
        self.boundaries.append(len(self.rows))
        logging.info("РАЗДЕЛИТЕЛЬ добавлен")
    def rezdelForBus2(self):                       #функция раздела в csv файле для наглядности 2 части  (с начала идут маршруты до аэропорта, после идет автовокзал)
        self.rows.append(['=========================================== Автовокзал ВИЛЬНЮС ========================='])
        self.boundaries.append(len(self.rows))
        logging.info("РАЗДЕЛИТЕЛЬ добавлен")

    def parseResults(self, i, j):
        logging.info(f"Начало | Пользователь: {self.username} | Скрипт: {self.script_name}")
        try:
            WebDriverWait(self.driver, 30).until(       #ожидание прогрузки карточек рейсов
                EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-route")))
        except TimeoutException:                #обработка возможной ошибки из за плохого прокси    
            logging.info(f"{i}: рейсов не найдено, пропускаю")
            self.boundaries.append(len(self.rows))
            self.driver.get(self.link)
            time.sleep(3)
            return
        self.findRoutes(i, f"{self.go_from} - {self.go_to}")
        choose_btn = None           #переменная чтобы после нажать на кнопку выбрать , и перейти на маршруты обратно
        all_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button") #если на нужную дату есть хоть одна кнопка выбрать , то мы сохраняем ее в переменную(сказано выше)
        for b in all_buttons:
            if b.text.strip() == "Выбрать":
                choose_btn = b
                break
        if choose_btn:
            self.driver.execute_script("arguments[0].click();", choose_btn)
            time.sleep(4)
            self.findRoutes(j, f"{self.go_to} - {self.go_from}")
        else:           #если нет рейсов туда , то нет и смылса брать обратные билеты
            logging.info(f"{i}: нет рейсов с кнопкой 'Выбрать', обратные пропущены")
        self.boundaries.append(len(self.rows))
        self.saveCsv()
        self.driver.get(self.link)
        time.sleep(3)
        logging.info(f"{i} -> {j}: собрано всего строк {len(self.rows)}")

    def findRoutes(self, date_str, route_txt):
        day = DAYS[datetime.strptime(str(date_str), "%Y-%m-%d").weekday()]
        cards = self.driver.find_elements(By.CSS_SELECTOR, ".search-results-route.is-desktop")
        for card in cards:  
            try:            #сбор информации с карточки(С ловлей возможной ошибки)
                time_ = card.find_element(
                    By.CSS_SELECTOR, ".search-results-route-time__value").get_attribute("textContent").strip()
            except NoSuchElementException:
                time_ = ""
            try:              #сбор информации с карточки(С ловлей возможной ошибки)
                carrier = card.find_element(
                    By.CSS_SELECTOR, ".search-results-route-features-carrier-text").get_attribute("textContent").strip()
            except NoSuchElementException:
                carrier = ""
            prices = card.find_elements(By.CSS_SELECTOR, ".search-results-route-purchase-price")
            if prices:
                price = prices[0].get_attribute('textContent').strip()
            else:
                price = "нет билетов"
            self.rows.append([date_str, day, time_, route_txt, carrier, price])
        logging.info(f"{date_str} | {route_txt}: собрано рейсов — {len(cards)}")

    def saveCsv(self, filename='eurolines_minsk_vilnius.csv'):          #запись в файл csv
        logging.info(f"Начало | Пользователь: {self.username} | Скрипт: {self.script_name}")
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['дата', 'день_недели', 'время', 'откуда-куда', 'перевозчик', 'цена'])
            for row in self.rows:
                writer.writerow(row)
        logging.info(f"CSV сохранён: {filename} | строк: {len(self.rows)}")