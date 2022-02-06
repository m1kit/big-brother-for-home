from prometheus_client import CollectorRegistry, PlatformCollector, start_http_server
import metric_jma_warnings
import metric_jma_forecast
import metric_tokyu
import threading
import logging

logging.basicConfig(level=logging.DEBUG)

registry = CollectorRegistry(auto_describe=True)
PlatformCollector(registry=registry)
metric_jma_warnings.Collector(registry=registry)
metric_jma_forecast.Collector(registry=registry)
metric_tokyu.Collector(registry=registry)

if __name__ == '__main__':
    import time

    logging.info('Starting a server on 9082...')
    start_http_server(9082, addr='0.0.0.0', registry=registry)
    logging.info('OK')

    thread = [t for t in threading.enumerate() if t.isDaemon()][0]
    thread.join()
