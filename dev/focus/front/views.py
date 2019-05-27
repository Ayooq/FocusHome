from flask import render_template, redirect, url_for

from . import app, conn
from .models import get_data, get_log


data = {}


@app.route('/')
def index():
    data = get_data()

    return render_template('index.html', **data)


@app.route('/control/')
def control():
    data = get_data()

    return render_template('control.html', **data)


@app.route('/control/<ident>/<action>')
def action(ident, action):
    units = conn.complects

    if ident in units.keys():
        complect = units[ident]

        if action == 'on':
            complect.on()

        elif action == 'off':
            complect.off()

    return redirect(url_for('control'))


@app.route('/log')
def log():
    log = get_log()

    return render_template('log.html', **log)
