from flask import render_template, redirect, url_for

from . import app, c
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


@app.route('/control/<id_>/<action>')
def action(id_, action):
    units = c.complects

    if id_ in units.keys():
        complect = units[id_]

        if action == 'on':
            complect.on()

        elif action == 'off':
            complect.off()

    return redirect(url_for('control'))


@app.route('/log')
def log():
    log = get_log()

    return render_template('log.html', **log)
