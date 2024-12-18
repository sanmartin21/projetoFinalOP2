import os
import json
import requests
import time
from prometheus_client import start_http_server, Gauge

# Função para medir tempo de resposta e status
def measure_response_time(url, session=None):
    try:
        session = session or requests.Session()
        start_time = time.perf_counter()
        response = session.get(url, timeout=5)
        response_time = time.perf_counter() - start_time
        return response.status_code, response_time
    except requests.exceptions.RequestException:
        return None, None

# Função principal para checar status
def check_status(config, metrics):
    """
    Checa status e tempo de resposta de uma URL.
    """
    session = requests.Session()

    # Monitoramento da URL (seja de login ou protegida)
    status_code, response_time = measure_response_time(config['login_url'], session=session)
    metrics['page_up'].set(1 if status_code == 200 else 0)
    metrics['page_time'].set(response_time if response_time else 0)

    # Caso haja uma URL protegida, mede também
    if config.get('monitored_url'):
        status_code, response_time = measure_response_time(config['monitored_url'], session=session)
        metrics['page_up'].set(1 if status_code == 200 else 0)
        metrics['page_time'].set(response_time if response_time else 0)

if __name__ == '__main__':
    # Carrega configurações das URLs
    with open('urls.json') as f:
        URLS = json.load(f)

    # Criação das métricas 
    metrics = {}
    for url in URLS:
        name = url['name']
        metrics[name] = {
            'page_up': Gauge(f'{name}_page_up', f'Status da página {name}'),
            'page_time': Gauge(f'{name}_page_response_time', f'Tempo de resposta da página {name}')
        }

    # Inicia o servidor Prometheus
    start_http_server(8000)

    while True:
        for url_config in URLS:
            check_status(url_config, metrics[url_config['name']])
        time.sleep(30)  # Intervalo de 30 segundos
