'''
Точка подключения  проекта
'''

from app import app

if __name__ == "__main__":
    '''
    Действительно только при отладки flask приложений
    '''
    # Если есть проблемы с отображением страниц - установи debug в True
    # app.run(host='127.0.0.1', port=5000, debug=False)
    app.run(host='0.0.0.0', port=80, debug=False)
