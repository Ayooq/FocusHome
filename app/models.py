from app import irn, banka

# fldo = fldx.sub.item().switch
# fldc = fldx.sub.recept


def mk_templ_data():
    # На всех устройствах обновляем состояние:

    for s in irn.complects.keys():
        irn.complects[s].state

    for s in irn.inputs.keys():
        irn.inputs[s].state

    for s in irn.temp.keys():
        irn.temp[s].temperature

    # Шаблоны будет обрабатывать irons как словарь устройств
    tdic = {
      'tdata': irn.temp,
      'complects': irn.complects,
      'inputs': irn.inputs,
      'base': banka
      }
    return tdic


def mk_templ_log():
    events = []

    logfile = open('candle.log', 'r')
    content = logfile.readlines()
    logfile.close()
    for line in content:
        event = {}
        item = line.split(' ')
        try:
            event['date'] = item[0]
            event['time'] = item[1]
            event['type'] = item[3]
            infa = ' '.join(item[4:])
            event['info'] = infa
        except Exception:
            event[type] = 'Плохой log'
            event['info'] = line
        events.append(event)
    tdic = {
      'logdata': events,
      'base': banka
      }
    return tdic
