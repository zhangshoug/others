# coding = utf-8
''' 巨潮资讯网-爬取公告对应的下载地址

'''
import csv
import math
import os
import time
import requests
import pandas as pd

START_DATE = '2016-12-31'  # 搜索的起始日期
END_DATE = str(time.strftime('%Y-%m-%d'))  # 默认当前提取，可设定为固定值
OUT_DIR = '{}tmp{}2019年'.format(os.sep, os.sep)
OUTPUT_FILENAME = '2019年度报告'
# 板块类型：沪市：shmb；深市：szse；深主板：szmb；中小板：szzx；创业板：szcy；
PLATE = 'szse;'
# 公告类型：category_scgkfx_szsh（首次公开发行及上市）、category_ndbg_szsh（年度报告）、category_bndbg_szsh（半年度报告）
# CATEGORY = 'category_ndbg_szsh;'
CATEGORY = ''

url = 'http://www.cninfo.com.cn/new/fulltextSearch/full?searchkey=&sdate=&edate=&isfulltext=false&sortName=nothing&sortType=desc&pageNum=1'
# http://www.cninfo.com.cn/new/fulltextSearch/full?searchkey=&sdate=&edate=&isfulltext=false&sortName=nothing&sortType=desc&pageNum=1&pageSize=500
url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
MAX_PAGESIZE = 50
MAX_RELOAD_TIMES = 5
RESPONSE_TIMEOUT = 10


def standardize_dir(dir_str):
    # assert (os.path.exists(dir_str)), 'Such directory \"' + str(dir_str) + '\" does not exists!'
    if not os.path.exists(dir_str):
        os.mkdir(dir_str)
    if dir_str[len(dir_str) - 1] != os.sep:
        return dir_str + os.sep
    else:
        return dir_str


# 参数：页面id(每页条目个数由MAX_PAGESIZE控制)，是否返回总条目数(bool)
def get_response(url, page_num, return_total_count=False, stock_code=''):
    query = {
        'stock': stock_code,
        'searchkey': '',
        'plate': PLATE,
        'category': CATEGORY,
        'trade': '',
        'column': 'szse',  # 注意沪市为sse
        #        'columnTitle': '历史公告查询',
        'pageNum': page_num,
        'pageSize': MAX_PAGESIZE,
        'tabName': 'fulltext',
        'sortName': '',
        'sortType': '',
        'limit': '',
        'showTitle': '',
        'seDate': START_DATE + '~' + END_DATE,
    }
    result_list = []
    reloading = 0
    while True:
        #        reloading += 1
        #        if reloading > MAX_RELOAD_TIMES:
        #            return []
        #        elif reloading > 1:
        #            __sleeping(random.randint(5, 10))
        #            print('... reloading: the ' + str(reloading) + ' round ...')
        try:
            r = requests.post(url, query, HEADER, timeout=RESPONSE_TIMEOUT)
        except Exception as e:
            print(e)
            time.sleep(0.5)
            continue
        if r.status_code == requests.codes.ok and r.text != '':
            break
    my_query = r.json()
    try:
        r.close()
    except Exception as e:
        print(e)
    if return_total_count:
        return my_query['totalRecordNum']
    else:
        for each in my_query['announcements']:
            announcementId = str(each['announcementId'])
            file_link = 'http://static.cninfo.com.cn/' + str(each['adjunctUrl'])
            file_name = __filter_illegal_filename(
                str(each['secCode']) + str(each['secName']) + str(
                    each['announcementTitle']) + '.' + '(' + str(
                    each['adjunctSize']) + 'k)' +
                file_link[-file_link[::-1].find('.') - 1:]  # 最后一项是获取文件类型后缀名
            )
            result_list.append([announcementId, file_name, file_link])
        return result_list


def __log_error(err_msg):
    err_msg = str(err_msg)
    print(err_msg)
    with open(error_log, 'a', encoding='gb18030') as err_writer:
        err_writer.write(err_msg + '\n')


def __filter_illegal_filename(filename):
    illegal_char = {
        ' ': '',
        '*': '',
        '/': '-',
        '\\': '-',
        ':': '-',
        '?': '-',
        '"': '',
        '<': '',
        '>': '',
        '|': '',
        '－': '-',
        '—': '-',
        '（': '(',
        '）': ')',
        'Ａ': 'A',
        'Ｂ': 'B',
        'Ｈ': 'H',
        '，': ',',
        '。': '.',
        '：': '-',
        '！': '_',
        '？': '-',
        '“': '"',
        '”': '"',
        '‘': '',
        '’': ''
    }
    for item in illegal_char.items():
        filename = filename.replace(item[0], item[1])
    return filename

def read_zxg(fname='zxg.txt'):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if not fname.find(os.sep) > -1:
        fname = os.path.join(dir_path, fname)
    resultList = []
    if os.path.isfile(fname):
        with open(fname, 'r', encoding='UTF-8') as zxg:
            alist =zxg.readlines()
    for a in alist:
        resultList.append(a[0:6])
    return resultList


def get_cninfo(stockCode=''):
    if stockCode[0] == '6':
        PLATE = 'shmb;'
    else:
        # 板块类型：沪市：shmb；深市：szse；深主板：szmb；中小板：szzx；创业板：szcy；
        PLATE = 'szse;'
    # 获取记录数、页数
    item_count = get_response(url, 1, True, stock_code=stockCode)
    assert (item_count != []), 'Please restart this script!'
    begin_pg = 1
    end_pg = int(math.ceil(item_count / MAX_PAGESIZE))
    print(
        'Page count: ' + str(end_pg) + '; item count: ' + str(item_count) + '.')
    time.sleep(0.5)
    resultList = []
    # 逐页抓取
    for i in range(begin_pg, end_pg + 1):
        row = get_response(url, i, stock_code=stockCode)
        if not row:
            __log_error('Failed to fetch page #' + str(i) +
                        ': exceeding max reloading times (' + str(
                MAX_RELOAD_TIMES) + ').')
            continue
        else:
            resultList.extend(row)
            last_item = i * MAX_PAGESIZE if i < end_pg else item_count
            print('Page ' + str(i) + '/' + str(
                end_pg) + ' fetched, it contains items: (' +
                  str(1 + (i - 1) * MAX_PAGESIZE) + '-' + str(
                last_item) + ')/' + str(item_count) + '.')
        time.sleep(0.4)
    return resultList

def save_cninfo(filename, stockCode=''):
    # 获取记录数、页数
    item_count = get_response(url, 1, True, stock_code=stockCode)
    assert (item_count != []), 'Please restart this script!'
    begin_pg = 1
    end_pg = int(math.ceil(item_count / MAX_PAGESIZE))
    print(
        'Page count: ' + str(end_pg) + '; item count: ' + str(item_count) + '.')
    print('保存文件名：{}'.format(filename))
    time.sleep(1)
    # 逐页抓取
    with open(filename, 'w', newline='', encoding='UTF-8') as csv_out:
        writer = csv.writer(csv_out)
        # todo 出错后，续传
        for i in range(begin_pg, end_pg + 1):
            row = get_response(url, i, stock_code=stockCode)
            if not row:
                __log_error('Failed to fetch page #' + str(i) +
                            ': exceeding max reloading times (' + str(
                    MAX_RELOAD_TIMES) + ').')
                continue
            else:
                writer.writerows(row)
                last_item = i * MAX_PAGESIZE if i < end_pg else item_count
                print('Page ' + str(i) + '/' + str(
                    end_pg) + ' fetched, it contains items: (' +
                      str(1 + (i - 1) * MAX_PAGESIZE) + '-' + str(
                    last_item) + ')/' + str(item_count) + '.')
            if i % 5 == 4:
                print('sleeping ...')
                time.sleep(1)


if __name__ == '__main__':

    codeList = read_zxg()
    # 初始化重要变量
    out_dir = standardize_dir(OUT_DIR)
    error_log = out_dir + 'error.log'
    output_csv_file = '{}.csv'.format(os.path.join(out_dir, OUTPUT_FILENAME))
    # output_csv_file = out_dir + OUTPUT_FILENAME.replace(os.sep,
    #                                                     '') + '_' + START_DATE.replace(
    #     '-', '') + '-' + END_DATE.replace('-',
    #                                       '') + '.csv'
    try:
        df=pd.read_csv(output_csv_file, header=None, usecols=[0,1,2])
    except Exception as e:
        df = pd.DataFrame()
    for code in codeList:
        print(code)
        if len(code) != 6:
            print('股票代码长度错误：{} 长度：{}'.format(code, len(code)))
            continue
        alist = get_cninfo(stockCode=code)
        # print(pd.DataFrame(alist))
        df = pd.concat([df, pd.DataFrame(alist)], ignore_index=True)
        # save_cninfo(output_csv_file, stockCode=code)
    # print(df)
    df.drop_duplicates(subset=[1,2], keep="first", inplace=True)

    # os.remove(output_csv_file)
    df.to_csv(output_csv_file, index=False, header=False)