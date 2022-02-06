from prometheus_client import CollectorRegistry, PlatformCollector, start_http_server
import metric_air
import threading
import logging

logging.basicConfig(level=logging.DEBUG)

registry = CollectorRegistry(auto_describe=True)
PlatformCollector(registry=registry)
metric_air.Collector(registry=registry, room='atlantica_main')

if __name__ == '__main__':
    import time

    logging.info('Starting a server on 9081...')
    start_http_server(9081, addr='0.0.0.0', registry=registry)
    logging.info('OK')

    thread = [t for t in threading.enumerate() if t.isDaemon()][0]
    thread.join()
