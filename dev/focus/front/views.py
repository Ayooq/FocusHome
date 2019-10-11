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


@app.route('/management/<unit>/<action>')
def action(unit, action):
    cout = focus_pro.couts.get(unit)

    if cout and action == 'on':
        cout.on()
    elif cout and action == 'off':
        cout.off()
    elif cout and action == 'toggle':
        cout.toggle()

    return redirect(url_for('management'))


@app.route('/log')
def log():
    log = get_log()

    return render_template('log.html', **log)
