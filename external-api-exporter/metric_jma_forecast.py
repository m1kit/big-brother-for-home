import requests
from prometheus_client.core import REGISTRY, GaugeMetricFamily, InfoMetricFamily

AREA_CODE = '130010'
AREA_CODE_SUB = '44132'
codes = {
    '100': '晴', '101': '晴時々曇', '102': '晴一時雨', '103': '晴時々雨', '104': '晴一時雪', '105': '晴時々雪', '106': '晴一時雨か雪', '107': '晴時々雨か雪', '108': '晴一時雨か雷雨', 
    '110': '晴後時々曇', '111': '晴後曇', '112': '晴後一時雨', '113': '晴後時々雨', '114': '晴後雨', '115': '晴後一時雪', '116': '晴後時々雪', '117': '晴後雪', '118': '晴後雨か雪', '119': '晴後雨か雷雨', 
    '120': '晴朝夕一時雨', '121': '晴朝の内一時雨', '122': '晴夕方一時雨', '123': '晴山沿い雷雨', '124': '晴山沿い雪', '125': '晴午後は雷雨', '126': '晴昼頃から雨', '127': '晴夕方から雨', '128': '晴夜は雨', 
    '130': '朝の内霧後晴', '131': '晴明け方霧', '132': '晴朝夕曇', '140': '晴時々雨で雷を伴う', '160': '晴一時雪か雨', '170': '晴時々雪か雨', '181': '晴後雪か雨', 
    '200': '曇', '201': '曇時々晴', '202': '曇一時雨', '203': '曇時々雨', '204': '曇一時雪', '205': '曇時々雪', '206': '曇一時雨か雪', '207': '曇時々雨か雪', '208': '曇一時雨か雷雨', '209': '霧', 
    '210': '曇後時々晴', '211': '曇後晴', '212': '曇後一時雨', '213': '曇後時々雨', '214': '曇後雨', '215': '曇後一時雪', '216': '曇後時々雪', '217': '曇後雪', '218': '曇後雨か雪', '219': '曇後雨か雷雨', 
    '220': '曇朝夕一時雨', '221': '曇朝の内一時雨', '222': '曇夕方一時雨', '223': '曇日中時々晴', '224': '曇昼頃から雨', '225': '曇夕方から雨', '226': '曇夜は雨', '228': '曇昼頃から雪', '229': '曇夕方から雪', 
    '230': '曇夜は雪', '231': '曇海上海岸は霧か霧雨', '240': '曇時々雨で雷を伴う', '250': '曇時々雪で雷を伴う', '260': '曇一時雪か雨', '270': '曇時々雪か雨', '281': '曇後雪か雨', 
    '300': '雨', '301': '雨時々晴', '302': '雨時々止む', '303': '雨時々雪', '304': '雨か雪', '306': '大雨', '308': '雨で暴風を伴う', '309': '雨一時雪', 
    '311': '雨後晴', '313': '雨後曇', '314': '雨後時々雪', '315': '雨後雪', '316': '雨か雪後晴', '317': '雨か雪後曇', 
    '320': '朝の内雨後晴', '321': '朝の内雨後曇', '322': '雨朝晩一時雪', '323': '雨昼頃から晴', '324': '雨夕方から晴', '325': '雨夜は晴', '326': '雨夕方から雪', '327': '雨夜は雪', '328': '雨一時強く降る', '329': '雨一時みぞれ',
    '340': '雪か雨', '350': '雨で雷を伴う', '361': '雪か雨後晴', '371': '雪か雨後曇', 
    '400': '雪', '401': '雪時々晴', '402': '雪時々止む', '403': '雪時々雨', '405': '大雪', '406': '風雪強い', '407': '暴風雪', '409': '雪一時雨',
    '411': '雪後晴', '413': '雪後曇', '414': '雪後雨',
    '420': '朝の内雪後晴', '421': '朝の内雪後曇', '422': '雪昼頃から雨', '423': '雪夕方から雨', '425': '雪一時強く降る', '426': '雪後みぞれ', '427': '雪一時みぞれ', '450': '雪で雷を伴う',
}
weather_names = ['jma_forecast_weather_today', 'jma_forecast_weather_next_day', 'jma_forecast_weather_next_next_day']
weather_descriptions = ['今日の天気', '明日の天気', '明後日の天気']
rain_names = [f'jma_forecast_rain_{i*6}hr' for i in range(7)]
rain_descriptions = [f'{i*6}時間後の降水確率' for i in range(7)]

class Collector:
    def __init__(self, registry=REGISTRY):
        if registry:
            registry.register(self)

    def collect(self):
        # Forecast metrics
        resp = requests.get('https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json')
        weather, rain, temp = resp.json()[0]['timeSeries']
        
        # Weather forecast
        weather_ts = weather['timeDefines']
        weather_tokyo = [w for w in weather['areas'] if w['area']['code'] == AREA_CODE][0]
        for i in range(len(weather_ts)):
            yield InfoMetricFamily(weather_names[i], weather_descriptions[i], {
                'date': weather_ts[i],
                'weather': codes[weather_tokyo['weatherCodes'][i]],
                'weatherDetailed': weather_tokyo['weathers'][i],
            })

        # Rainfall forecast
        rain_ts = rain['timeDefines']
        rain_tokyo = [w for w in rain['areas'] if w['area']['code'] == AREA_CODE][0]
        for i in range(len(rain_ts)):
            gauge = GaugeMetricFamily(rain_names[i], rain_descriptions[i], labels=['date'])
            gauge.add_metric([rain_ts[i]], int(rain_tokyo['pops'][i]))
            yield gauge

        # Temperature forecast
        temp_ts = temp['timeDefines']
        temp_tokyo = [w for w in temp['areas'] if w['area']['code'] == AREA_CODE_SUB][0]
        gauge = GaugeMetricFamily('jma_forecast_temp_lo', '今日の最低気温', labels=['date'])
        gauge.add_metric([temp_ts[0]], int(temp_tokyo['temps'][0]))
        yield gauge
        gauge = GaugeMetricFamily('jma_forecast_temp_hi', '今日の最高気温', labels=['date'])
        gauge.add_metric([temp_ts[0]], int(temp_tokyo['temps'][1]))
        yield gauge
