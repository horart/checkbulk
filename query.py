import json
import requests
from datetime import datetime
import crypto
import io


def query(s):
    data_in = dict(i.split('=') for i in s.split('&'))
    data_in['t'] = datetime.strptime(data_in['t'], '%Y%m%dT%H%M').strftime('%d.%m.%Y %H:%M')


    r = requests.post('https://proverkacheka.com/api/v1/check/get',
                files={
                    'fn': (None, data_in['fn']),
                    'fd': (None, data_in['i']),
                    'fp': (None, data_in['fp']),
                    't': (None, data_in['t']),
                    'n': (None, data_in['n']),
                    'qr': (None, '0'),
                    's': (None, data_in['s']),
                    'token': (None, crypto.get_token(data_in['fn'], data_in['i'], data_in['fp'], data_in['n'], data_in['s'], data_in['t'], '0')), # 0.16
                },
                headers={
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0',
                    'Sec-Fetch-Mode': 'same-origin',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Site': 'same-origin',
                    'Origin': 'https://proverkacheka.com',
                    'Referer': 'https://proverkacheka.com',
                    'Accept-Encoding': 'gzip, deflate, br, zstd',
                    'Accept-Language': 'en-US,en;q=0.5',
                }
    )
    try:
        j = json.loads(crypto.decrypt(r.content))['data']['json']
    except json.decoder.JSONDecodeError:
        c = crypto.decrypt(r.content)
        c = c.split('"')
        c[-1] = '}}}}'
        c = '"'.join(c)
        j = json.loads(c)
    items = j['items']
    store = j['user']
    date = datetime.strptime(j['dateTime'], '%Y-%m-%dT%H:%M:%S')
    items_out = []
    for item in items:
        items_out.append({
            'name': item['name'],
            'quantity': item['quantity'],
            'price': item['price'] / 100,
        })
        # product + category

    return store, date, items_out

def pretty_print(store, date, items):
    return store + '\n' + date.strftime('%d.%m.%y %H:%M') + '\n\n' + \
        '\n'.join(f'{i['name']}\n {i['price']}*{i['quantity']}={round(i['price']*i['quantity'], 2)}' for i in items) + \
            f'\nИТОГО: {sum(round(i['price']*i['quantity'], 2) for i in items)}'