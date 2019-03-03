# focusPro

WEB interface устройств GPIO на Raspberry Pi. Базовый язык разработки python 3
Обмен данными по протоколу MQTT

## Статус

Рабочий Макет

## Основное 

- Работает на Raspberry Pi 3В+ и ОС Raspbian
- Интерфейс управления устройств GPIO основан на библиотеке gpiozero
- Фреймворк веб-приложение flask 
- Запуск приложение WSGI Python на основе gunicorn
- Развертка - nginx
- Обмен с внешней средой на основе протокола MQTT:
    клиентская часть paho-mqtt
    посредник mosquitto

## Состав

- каталог app - все для работы flask
- banka.py- головная для запуска
- banka.yaml - конфигурация оборудования
- iron.py - организация управления по GPIO
- logger.py - регистраторы
- report.py - сообщения
- requirements.txt - список дополнительных пакетов
