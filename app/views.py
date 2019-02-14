from flask import render_template
from app import app
from app import irn

from .models import mk_templ_data
from .models import mk_templ_log


@app.route('/')
@app.route('/index')
def main():
    templatedata = mk_templ_data()
    return render_template('index.html', **templatedata)


@app.route('/control/')
def cntrl():
    templatedata = mk_templ_data()
    return render_template('cntrl.html', **templatedata)


@app.route('/log/')
def viewlog():
    templatedata = mk_templ_log()
    return render_template('log.html', **templatedata)


@app.route("/<whochange>/<action>")
def action(whochange, action):
    message = " "
    id = whochange
    fldx = irn.complects
    if whochange in fldx.keys():
        id = whochange
        device = fldx[id].switch
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
    templatedata['message'] = message
    return render_template('cntrl.html', **templatedata)


if __name__ == "__main__":
    main()
