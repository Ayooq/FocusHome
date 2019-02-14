from flask import render_template
from app import app

from app import fld, temp, banka

def mk_templ_data():
    # На всех устройствах обновляем состояние:
    for s in fld.keys():
        fld[s].state

    for s in temp.keys():
        temp[s].temperature

    # Шаблоны будет обрабатывать irons как словарь устройств
    tdic = {
      'irons': fld.sub,
      'tdata': temp.sub,
      'base' : banka
      }
    return tdic

@app.route('/')
@app.route('/index')
def main():
    # На всех устройствах обновляем состояние:
    # for s in fld.keys():
        # fld[s].state

    # for s in temp.keys():
        # temp[s].temperature

    # Шаблон main.html будет обрабатывать irons как словарь устройств
    # templatedata = {
      # 'irons': fld.sub,
      # 'tdata': temp.sub,
      # 'base' : banka
      # }
    templatedata = mk_templ_data()
    return render_template('index.html', **templatedata)
    # return render_template('main.html', **templatedata

@app.route('/control/')
def cntrl():
    templatedata = mk_templ_data()
    return render_template('cntrl.html', **templatedata)

'''
Функция выполняется по запросу URL с идентификатором PIN и действием
'''

@app.route("/<whochange>/<action>")
def action(whochange, action):
    message = " "
    id = whochange
    if whochange in fld.keys():
        id = whochange
        device = fld[id]

        if action == "on":
            device.on()
            message = "Включаю " + device.ident
        if action == "off":
            device.off()
            message = "Отключаю " + device.ident
        if action == "toggle":
            device.toggle()
            message = "Переключаю " + device.ident
    

    templatedata = mk_templ_data()
    return render_template('cntrl.html', **templatedata)

if __name__ == "__main__":
    main()
