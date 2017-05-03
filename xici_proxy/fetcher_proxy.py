# -*- coding: utf-8 -*-
import argparse
import codecs
import sqlite3
from datetime import datetime

import logging
import requests
from bs4 import BeautifulSoup

from proxy_handler import ProxyHandler


error_content = ['Access Denied', 'Unauthorized ...', '500 Internal Server Error', 'HTTP Status 500']

logging.basicConfig()
logger = logging.getLogger()


def get_page_content(start_date, end_date, page_no, proxy=False):
    url = "http://datacenter.mep.gov.cn:8099/ths-report/report%21list.action"

    payload = "page.pageNo={}&xmlname=1462259560614&queryflag=open&isdesignpatterns=false&V_DATE={}&E_DATE={}"\
        .format(page_no, start_date, end_date)
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    while True:
        proxies = None
        if proxy:
            proxy_handler = ProxyHandler.instance()
            proxy_host = proxy_handler.get_proxy_host()
            proxies = {'http': 'http://' + proxy_host}
            logger.debug( "fetch page {} with proxy host {}".format(page_no, proxy_host))
        try:
            response = requests.request("POST", url, data=payload, headers=headers, proxies=proxies, timeout=20)
            response_content = response.text
            for ec in error_content:
                if ec in response_content:
                    raise Exception(ec)

            if 'class="report-table"' not in response_content:
                logger.warn(u"未找到数据， page {}".format(response_content))
                raise Exception(u"未找到数据")

            return response_content
        except Exception, e:
            if proxy:
                proxy_handler.remove_host(proxy_host)
                logger.debug(u"ERR: {} , change proxy host, rm host {}".format(e, proxy_host))
            else:
                logger.debug(u"ERR: {}".format(e))
        else:
            break


def parse_page(content):
    document = BeautifulSoup(content, 'lxml')
    table = document.find_all(onmouseover=True)
    result = []
    for t in table:
        tds = t.select('td')
        area = tds[2].text
        value = tds[3].text
        pollute = tds[4].text
        record_date = tds[6].text
        result.append((area, value, pollute, record_date))
    return result


def get_db_conn():
    return sqlite3.connect('/data/aqi/aqi.sqlite')


def save_record(area, value, pollutant, record_date):
    if not value:
        logger.warn(u"{} 没有 AQI 值".format(area))
        return

    pollutant = '' if not pollutant else pollutant
    crt_date = datetime.strftime(datetime.now(), '%Y-%m-%d')

    conn = get_db_conn()
    exist_query = u"SELECT * FROM aqi_data where area = '{}'  " \
                  u"and datetime(record_date, 'unixepoch') = '{} 00:00:00'".format(area, record_date)
    logger.debug(exist_query)
    c = conn.execute(exist_query)
    record = c.fetchone()

    if not record:  # 插入新数据
        insert_stat = u"insert into aqi_data (area, `value`, pollutant, record_date, fetch_date)" \
                      u"VALUES ('{}', {}, '{}', strftime('%s', '{}'), strftime('%s', '{}'))" \
            .format(area, value, pollutant, record_date, crt_date)
        logger.debug(insert_stat)
        conn.execute(insert_stat)
    else:
        update_stat = u"update aqi_data set `value` = {}, pollutant = '{}', fetch_date=strftime('%s', '{}') " \
                      u"where id = area = '{}' and datetime(record_date, 'unixepoch') = '{} 00:00:00'" \
            .format(value, pollutant, crt_date, area, record_date)
        logger.debug(update_stat)
        conn.execute(update_stat)

    conn.commit()
    conn.close()


def page_content_to_db(content):
    records = parse_page(content)
    for r in records:
        save_record(*r)


def process_exists_page():
    for i in range(12401):
        logger.info('process page: {}'.format(i))
        f = codecs.open('/data/aqi/{}.html'.format(i+1), 'r', 'utf-8')
        content = "".join(f.readlines())
        page_content_to_db(content)


def get_total_page_count(start_date, end_date):
    content = get_page_content(start_date, end_date, 1)
    document = BeautifulSoup(content, 'lxml')
    line = document.select_one('.report_page')
    for l in line.text.split("\n"):
        if u"总页数" in l:
            return int(l.split(u"：")[1])
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy', action='store_true')
    parser.add_argument('--start-date', required=True)
    parser.add_argument('--end-date', required=True)
    parser.add_argument('--log-level', default='INFO', choices=['NOTEST', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    args = parser.parse_args()

    logger.setLevel(args.log_level)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    proxy = args.proxy
    proxy = True
    start_date = args.start_date
    end_date = args.end_date
    s_date = datetime.strptime(start_date, '%Y-%m-%d')
    e_date = datetime.strptime(end_date, '%Y-%m-%d')

    if e_date < s_date:
        logger.error(u"data format 2000-01-01 & START_DATE<= END_DATE")
        exit(1)

    total_page = get_total_page_count(start_date, end_date)
    if not total_page:
        logger.error(u"no page info founded")
        exit(1)

    logger.info(u"总页数 {}".format(total_page))
    for i in range(total_page):
        p = i + 1
        logger.info(u"总页数 {}, 处理第 {} 页".format(total_page, p))
        content = get_page_content(start_date, end_date, p, proxy)
        page_content_to_db(content)
