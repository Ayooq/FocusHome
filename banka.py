import logging
from app import app

if __name__ == "__main__":
    from logger import create_2_logger

    logger = create_2_logger(logging.DEBUG)
    logger.info('Banka start []')
    app.run(host='127.0.0.1', port=5000, debug=False)
    logger.info('Bankа stop []')
    # app.run(host='0.0.0.0', port=80, debug=True)
