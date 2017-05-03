# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import random
from threading import Thread
from time import sleep

import logging
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger()


def proxy_health_check(host):
    proxies = {'http': 'http://{}'.format(host)}
    try:
        requests.request('GET', 'http://www.baidu.com/img/baidu.svg',
                         timeout=1, proxies=proxies)
    except Exception:
        return False

    return True


class ProxyHandler(object):
    _instance = None

    @staticmethod
    def instance():
        if not ProxyHandler._instance:
            ProxyHandler._instance = ProxyHandler()
        return ProxyHandler._instance

    def __init__(self):
        self.api_url = 'http://api.xicidaili.com/free2016.txt'
        self.delta_min = 10
        self.refresh_time = datetime.now()
        self.proxy_hosts = set()
        self.health_proxy_hosts = set()
        self._init_finished = False
        self._init_proxy_fetcher()

    def get_proxy_host(self, block=True):
        result = self._get_random_from_hosts()
        if not block or result:
            return result

        while True:
            sleep(1)
            result = self._get_random_from_hosts()
            if result:
                return result

    def remove_host(self, host):
        self.health_proxy_hosts.discard(host)

    def _get_random_from_hosts(self):
        if not self.health_proxy_hosts:
            return None

        return list(self.health_proxy_hosts)[random.randint(0, len(self.health_proxy_hosts) - 1)]

    def _init_proxy_fetcher(self):
        def proxy_fetcher():
            if self.refresh_time + timedelta(minutes=self.delta_min) < datetime.now() or not self._init_finished:
                self._init_finished = True
                self.refresh_time = datetime.now()
                response = requests.request('GET', self.api_url)
                self.proxy_hosts.update(set(map(lambda x: x.strip(), response.text.split('\n'))))

            for h in self.proxy_hosts:
                logger.debug("check " + h)
                if proxy_health_check(h):
                    logger.debug("{} is ok".format(h))
                    logger.info("current available proxy host count {} ...".format(len(self.health_proxy_hosts)))
                    self.health_proxy_hosts.add(h)

            self.proxy_hosts.clear()

        def proxy_fetcher_loop():
            while True:
                proxy_fetcher()
                sleep(10)

        t = Thread(target=proxy_fetcher_loop)
        t.setDaemon(1)
        t.start()

        def check_ip_from_page_loop():
            i = 0
            max_i = 100
            while True:
                i += 1
                page = i % max_i
                for type in ['nn', 'nt', 'wt']:
                    sleep(10)
                    self.check_ip_from_page(type, page)

        tt = Thread(target=check_ip_from_page_loop)
        tt.setDaemon(1)
        tt.start()

    def check_ip_from_page(self, type, page):
        # type in ['wt', 'nt', 'nn']
        res = requests.get('http://www.xicidaili.com/{}/{}'.format(type, page), timeout=5,
                           headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'})
        doc_str = res.text
        document = BeautifulSoup(doc_str, 'lxml')
        ip_list = document.select_one("#ip_list")
        ips = [item.text.strip() for item in ip_list.select('tr > td:nth-of-type(2)')]
        ports = [item.text.strip() for item in ip_list.select('tr > td:nth-of-type(3)')]
        locations = [item.text.strip() for item in ip_list.select('tr > td:nth-of-type(4)')]
        anonymous = [item.text.strip() for item in ip_list.select('tr > td:nth-of-type(5)')]
        httptypes = [item.text.strip() for item in ip_list.select('tr > td:nth-of-type(6)')]
        http_ips = []
        for tp in zip(ips, ports, locations, anonymous, httptypes):
            if tp[-1] == 'HTTP':
                http_ips.append("{}:{}".format(tp[0].strip(), tp[1].strip()))
        for i in http_ips:
            logger.debug("check ip from page: {}".format(i))
            if proxy_health_check(i):
                logger.info("current available proxy host count {} ...".format(len(self.health_proxy_hosts)))
                self.health_proxy_hosts.add(i)

if __name__ == '__main__':
    h = ProxyHandler()
    logging.basicConfig()
    logging.getLogger("requests").setLevel(logging.WARNING)
    logger.setLevel('DEBUG')
    for i in range(20):
        sleep(1)
        print u"=======>{}<".format(h.get_proxy_host())
