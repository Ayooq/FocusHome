from zconnector import Connector


if __name__ == '__main__':

    import sys
    from logger import create_logger

    try:
        symbol = sys.argv[1]
    except Exception:
        symbol = 'd'

    # Это общий сигнальный обмен PUSH/POOL
    connecta = {  # Привязка к аргументам ZSink (zservice.py)
        'publish': 'ipc:///tmp/banka-order.ipc',   # Распоряжения
        'sink': 'ipc:///tmp/banka-report.ipc'  # Отчеты
    }

    banka_address = {  # демон ПРИБОРА  ЗАПРОС/ОТВЕТ
        'address': "ipc:///tmp/banka-instrument1.ipc"
    }
    '''Для прибора полный адрес'''
    banka_address.update(connecta)

    logger = create_logger('DEBUG')

    if 'd' in symbol:
        logger.info('start demon')
        prb = Connector('fedor', **banka_address)
        # prb.worker_easy()
        prb.worker()
        prb.subscribe(prb.name)
        logger.info('finish demon')
    else:
        pass
