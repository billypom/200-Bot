# format_list = [1, 2, 3, 5, 5]

# max_val = max(format_list)
# ind = [i for i, v in enumerate(format_list) if v == max_val]

# print(ind)

import requests
import secrets
import re
from bs4 import BeautifulSoup as Soup
# try:
# mkcresponse = requests.get("https://www.mariokartcentral.com/forums/index.php?members/popuko.154/user-ips")
# print(mkcresponse.status_code)
# mkc_data = mkcresponse.json()
# buh = json.dumps(mkc_data)
# mkc_data_dict = json.loads(buh)
# return_value = mkc_data_dict[field_name]
# return return_value

# tonola.37179
# Get shared ips
login_url = 'https://www.mariokartcentral.com/forums/index.php?login/login'
data_url = 'https://www.mariokartcentral.com/forums/index.php?members/tonola.37179/shared-ips'
with requests.Session() as s:
    html = s.get(login_url).content
    soup = Soup(html, 'html.parser')
    token = soup.select_one('[name=_xfToken]').attrs['value']
    payload = {
    'login': str(secrets.mkc_name),
    'password': str(secrets.mkc_password),
    '_xfToken': str(token),
    '_xfRedirect': 'https://www.mariokartcentral.com/mkc/'
    }
    response = s.post(login_url, data=payload)
    response = s.get(data_url)
    response_string = str(response.content)
    response_lines = response_string.split('\\n')
    for line in response_lines:
        # this h3 div is only used to show shared ips. so it works as a unique identifier
        if '<h3 class="contentRow-header"><a href="/forums/index.php?members/' in line:
            regex_pattern = 'members/.*\.\d*'
            # if the regex pattern is found in the line
            if re.search(regex_pattern, line):
                # find the exact place (index-characters of string or w/e) where the pattern matches
                regex_group = re.search(regex_pattern, line)
                # get the string from that exact place
                x = regex_group.group()
                # split on a slash (its always slash)
                reg_array = re.split('/', x)
                print(reg_array)

data_url = 'https://www.mariokartcentral.com/forums/index.php?members/popuko.154'
with requests.Session() as s:
    html = s.get(login_url).content
    soup = Soup(html, 'html.parser')
    token = soup.select_one('[name=_xfToken]').attrs['value']
    payload = {
    'login': str(secrets.mkc_name),
    'password': str(secrets.mkc_password),
    '_xfToken': str(token),
    '_xfRedirect': 'https://www.mariokartcentral.com/mkc/'
    }
    response = s.post(login_url, data=payload)
    response = s.get(data_url)
    response_string = str(response.content)
    response_lines = response_string.split('\\n')
    # \t\t\t\t\t\t\t\t\t\t\t<time  class="u-dt" dir="auto" datetime="2022-07-30T11:07:30-0400" data-time="1659193650" data-date-string="Jul 30, 2022" data-time-string="11:07 AM" title="Jul 30, 2022 at 11:07 AM">A moment ago</time> <span role="presentation" aria-hidden="true">&middot;</span> Viewing member profile <em><a href="/forums/index.php?members/popuko.154/" dir="auto">popuko</a></em>
    for idx, line in enumerate(response_lines):
        # print(line)
        if 'Last seen' in line:
            last_seen_string = response_lines[idx+2]
            regex_pattern = 'data-time="\d*"'
            if re.search(regex_pattern, last_seen_string):
                # find the exact place (index-characters of string or w/e) where the pattern matches
                regex_group = re.search(regex_pattern, last_seen_string)
                # get the string from that exact place
                x = regex_group.group()
                # split on a slash (its always slash)
                reg_array = re.split('"', x)
                print(reg_array)
                last_seen_unix_timestamp = reg_array[1]
                break