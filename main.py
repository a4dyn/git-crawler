# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import argparse
import requests
import re
import warnings

# 无视bs4的UserWarning
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

# 默认搜索组
search_list = ['在这里', '输入', '你想查找的', '字符串']

# 用以发送请求的header
# 注意：在使用时请重新填写使用者的cookie等信息！
headers = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
'Cache-Control': 'no-cache',
'Connection': 'keep-alive',
'Cookie': '_octo=GH1.1.19******38.159******64; _ga=GA1.2.93******46.15******36; _device_id=37******ed; user_session=Qp******Kq; __Host-user_session_same_site=Qp******Rj-0T******Kq; logged_in=yes; dotcom_user=D******n; _gid=GA1.2.7******5.16******72; has_recent_activity=1; tz=A******%2FS******; _gh_sess=ep******3D',
'DNT': '1',
'Host': 'github.com',
'Pragma': 'no-cache',
'Referer': 'https://github.com/',
'Sec-Fetch-Dest': 'document',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-Site': 'same-origin',
'Sec-Fetch-User': '?1',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
}

# ArgumentParser
args = argparse.ArgumentParser(description='Enter the keywords, divided by comma, that you want to search within GitHub. If no \'-s\' is specified, the default list will be used.')
args.add_argument('-s', metavar='Search_List', type=str, dest='search_string', help='enter the search list, divided by comma')
args = args.parse_args()

# 如果-s被输入，则替换掉原先的list
if args.search_string is not None:
    search_list = args.search_string.split(',')

# 创建并写入file
f = open('Result.txt', 'w', encoding='utf-8')

print('\nSearching from the list: ' + str(search_list), flush=True)
f.write('Searching from the list: ' + str(search_list))

for keyword in search_list:

    # 跳过空白字符
    if keyword == '':
        continue

    print('Writing the result of:', keyword, flush=True)
    f.write('\n\nShowing the result of: ' + keyword + '\n')

    # 爬取前200页的搜索结果
    for i in range(1,200):

        print('Writing page', i, '...', flush=True)

        url = 'https://github.com/search?p=' + str(i) + '&q=' + keyword + '&type=code'

        try:
            _request = requests.get(url = url, headers = headers)
            text_raw = _request.text

        except Exception as e: print(e)

        # 用以支持汉字和特殊字符的输出
        soup = BeautifulSoup(text_raw, 'lxml', from_encoding='gb18030')

        # URL不正确或碰到了底端，则会显示404
        if '404 “This is not the web page you are looking for”' in text_raw:
            print('Meet 404, current keyword has reached the end.', flush=True)
            break

        # Fetch出有用的信息
        else:
            for box in soup.find_all('div', {'class': 'width-full'}):
                valid = False

                for href in box.find_all('a', title=True, href=True):
                    if href['href'] == 'https://github.com' or (not (box.find('a', title=True, href=True))):
                        break
                    else:
                        valid = True
                        # 分割线
                        f.write('-----------------------------------\n')
                        f.write('URL: \n\thttps://github.com' + href['href'] + '\n')
                        f.write('\nCode:')
                        f.flush()

                if valid:
                    # print在Windows环境下会出错，故使用write-to-file
                    for divs in box.find_all('div', {'class': 'file-box blob-wrapper my-1'}):
                        ncount = 0
                        for code in divs.strings:
                            if code.isnumeric():
                                continue
                            if code == '\n':
                                ncount += 1
                            elif code == '\t':
                                f.write('\t')
                                f.flush()
                                ncount = 0
                            elif ncount == 0:
                                f.write(code)
                                f.flush()
                                ncount = 0
                            else:
                                f.write('\n\t' + code)
                                f.flush()
                                ncount = 0
                    # 分割线
                    f.write('\n-----------------------------------\n')
                    f.flush()

f.close()
