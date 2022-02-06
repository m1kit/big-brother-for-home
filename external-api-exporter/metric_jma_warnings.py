import requests
from prometheus_client.core import REGISTRY, GaugeMetricFamily, StateSetMetricFamily

AREA_CODE = '1310900'
warning_levels = [
    '発表なし',
    '注意報',
    '警報',
    '特別警報',
]
warning_types = [{
    'id': 'jma_warning_rain',
    'key': '大雨',
    'description': '大雨による土砂災害や浸水害が発生するおそれ',
    'levels': ['10', '03', '33',],
}, {
    'id': 'jma_warning_snow',
    'key': '大雪',
    'description': '降雪や積雪による住家等の被害や交通障害など、大雪により災害が発生するおそれ',
    'levels': ['12', '06', '36',],
}, {
    'id': 'jma_warning_thunder',
    'key': '雷',
    'description': '落雷のほか、急な強い雨、竜巻等の突風、降ひょうといった積乱雲の発達に伴い発生する激しい気象現象による人や建物への被害が発生するおそれ',
    'levels': ['14',],
}, {
    'id': 'jma_warning_wind',
    'key': '暴風',
    'description': '強風により災害が発生するおそれ',
    'levels': ['15', '05', '35',],
}, {
    'id': 'jma_warning_flood',
    'key': '洪水',
    'description': '河川の上流域での大雨や融雪によって下流で生じる増水により洪水災害が発生するおそれ',
    'levels': ['18', '04',],
}, {
    'id': 'jma_warning_wind_snow',
    'key': '風雪',
    'description': '雪を伴う強風により災害が発生するおそれ',
    'levels': ['13', '02', '32',],
}, {
    'id': 'jma_warning_cold',
    'key': '低温',
    'description': '低温により災害が発生するおそれ',
    'levels': ['23',],
}, {
    'id': 'jma_warning_dry',
    'key': '乾燥',
    'description': '空気の乾燥により災害が発生するおそれ',
    'levels': ['21',],
}]

class Collector:
    def __init__(self, registry=REGISTRY):
        if registry:
            registry.register(self)

    def collect(self):
        # Warning metrics
        resp = requests.get('https://www.jma.go.jp/bosai/warning/data/warning/130000.json')
        data = resp.json()
        entries = [e for e in data['areaTypes'][1]['areas'] if e['code'] == AREA_CODE]
        result = {w['id']: warning_levels[0] for w in warning_types}
        if entries:
            warnings = entries[0]['warnings']
            warnings = [w for w in warnings if w['status'] != '解除']
            if len(warnings) != 1 or warnings[0]['status'] != '発表警報・注意報はなし':
                for wtype in warning_types:
                    for w in warnings:
                        wcode = w['code']
                        if wcode not in wtype['levels']:
                            continue
                        result[wtype['id']] = warning_levels[wtype['levels'].index(wcode) + 1]
        for wtype in warning_types:
            m = StateSetMetricFamily(
                wtype['id'], 
                wtype['description'],
            )
            val = {key: key == result[wtype['id']] for key in warning_levels}
            m.add_metric([], val)
            yield m

    def describe(self):
        # Warnings
        for warning_type in warning_types:
            yield StateSetMetricFamily(
                warning_type['id'], 
                warning_type['description'],
                labels=warning_levels
            )
