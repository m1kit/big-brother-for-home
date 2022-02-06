import requests
from prometheus_client.core import REGISTRY, InfoMetricFamily, StateSetMetricFamily

delay_levels = [
    '平常運転',
    '遅延',
    '運転見合わせ',
]
lines = {
    'ty': '東急東横線',
    'mg': '東急目黒線',
    'dt': '東急田園都市線',
    'om': '東急大井町線',
    'ik': '東急池上線',
    'tm': '東急多摩川線',
    'sg': '東急世田谷線',
    'kd': '東急こどもの国線',
}

class Collector:
    def __init__(self, registry=REGISTRY):
        if registry:
            registry.register(self)

    def collect(self):
        # Tokyu Lines Info
        resp = requests.get('https://www.tokyu.co.jp/unten/unten2.json')
        resp.encoding='utf-8-sig'
        data = resp.json()

        for key, name in lines.items():
            status = int(data[f"check_{key}"][2])
            value = {delay_levels[i]: i == status for i in range(len(delay_levels))}
            yield StateSetMetricFamily(f"tokyu_{key}_status", f"{name}の運行状態", value=value)
            yield InfoMetricFamily(f"tokyu_{key}_info", f"{name}の運行状況", {
                'message': data[f"unten_{key}"],
            })
