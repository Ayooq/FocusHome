from flask import redirect, render_template, url_for

from . import app, focus_pro
from .models import get_data, get_log

data = {}


@app.route('/')
def index():
    data = get_data()

    return render_template('index.html', **data)


@app.route('/management/')
def management():
    data = get_data()

    return render_template('management.html', **data)


@app.route('/management/<id_>/<action>')
def action(id_, action):
    complect = focus_pro.complects.get(id_)

    if complect and action == 'on':
        complect.on()

    elif complect and action == 'off':
        complect.off()

    return redirect(url_for('management'))


@app.route('/log')
def log():
    log = get_log()

    return render_template('log.html', **log)
