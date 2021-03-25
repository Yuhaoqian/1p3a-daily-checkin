import requests
import re
from io import BytesIO
from PIL import Image, ImageFilter
from collections import defaultdict
import pytesseract
import json
import logging
import sys

logging.basicConfig(level=logging.INFO,
        format='%(asctime)s - %(message)s',
        filename='log.txt',
        filemode='a')

HEADERS = {
    'origin': 'https://www.1point3acres.com',
    'referer': 'https://www.1point3acres.com/bbs/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
}

URL_LOGIN = 'https://www.1point3acres.com/bbs/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
URL_CHECK_IN_PAGE = 'https://www.1point3acres.com/bbs/dsu_paulsign-sign.html'
URL_CHECK_IN = 'https://www.1point3acres.com/bbs/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=0&inajax=0'
URL_VERIFY_IMAGE = 'https://www.1point3acres.com/bbs/misc.php?mod=seccode&update={}&idhash=S00'
URL_UPDATE_NUM = 'https://www.1point3acres.com/bbs/misc.php?mod=seccode&action=update&idhash=S00&inajax=1&ajaxtarget=seccode_S00'

def login(username, password):
    ''' Login
        return Session
    '''
    session = requests.session()

    data = {
        'username': username,
        'password': password,
        'quickforward': 'yes',
        'handlekey': 'ls'
    }

    session.post(
        URL_LOGIN,
        headers=HEADERS,
        data=data)
    print('---------Welcome to 1p3a-----------')
    logging.info('---------Welcome to 1p3a-----------')
    return session

def logout(session):
    ''' Logout '''
    session.cookies.clear()
    print('---------Bye Bye-----------')
    logging.info('---------Bye Bye-----------')


def get_formhash(session):
    resp = session.get(URL_CHECK_IN_PAGE, headers=HEADERS)
    try:
        formhash = re.search('name="formhash" value="(.*?)"', resp.text).group(1)
    except:
        formhash = re.search('formhash=(.*?)', resp.text).group(1)
    return formhash

def get_update_num(session):
    resp = session.get(URL_UPDATE_NUM, headers=HEADERS)
    update_num = re.search('&update=(.*)&', resp.text).group(1)
    return update_num

def get_verify_image(session):
    resp = session.get(URL_VERIFY_IMAGE, headers=HEADERS)
    verify_gif = Image.open(BytesIO(resp.content))
    durations = []
    try:
        while True:
            durations.append(verify_gif.info['duration'])
            verify_gif.seek(verify_gif.tell() + 1)
    except EOFError:
        pass
    verify_gif.seek(durations.index(max(durations)))
    verify_image = Image.new('RGBA', verify_gif.size)
    verify_image.paste(verify_gif)
    return verify_image

def checkin(username, password):
    # 1. login
    session = login(username, password)

    resp = session.get(URL_CHECK_IN_PAGE, headers=HEADERS)
    have_checked = re.search('您今天已经签到过了', resp.text)
    if have_checked:
        print('You have already checked in today!')
        logging.info('You have already checked in today!')
        return
    # 2. get formhash
    formhash = get_formhash(session)

    while True:
        # 3. get update num
        update_num = get_update_num(session)
        URL_VERIFY_IMAGE.format(update_num)
        # 4. get verfify image
        verify_image = get_verify_image(session)
        # 5. get verify code
        try:
            verify_code = _recognize_verify(verify_image)
            print(f'Verification code prediction: {verify_code}')
            logging.info(f'Verification code prediction: {verify_code}')
        except Exception as e:
            print("An exception occurred")
            logging.error("An exception occurred")
            print(e)
            logging.error(e)
            continue

        body = {
            'formhash': formhash,
            'qdxq': 'kx',
            'qdmode': 2,
            'todaysay': 'check in',
            'fastreply': 0,
            'sechash': 'S00',
            'seccodeverify': verify_code
        }
        resp = session.post(URL_CHECK_IN, headers=HEADERS, data=body)

        is_succeed = re.search('恭喜你签到成功', resp.text)
        if is_succeed:
            print('Check in successfully!')
            logging.info('Check in successfully!')
            break
        else:
            print('Fail! Wrong Verification code!')
            logging.warning('Fail! Wrong Verification code!')
            continue

    # 7. logout
    logout(session)


def _recognize_verify(img):
    """
    Recognize the verify code image to string
    """
    # Initialize
    rgb_dict = defaultdict(int)
    ans = ""
    # Remove background color
    pix = img.load()
    width = img.size[0]
    height = img.size[1]
    for x in range(width):
        for y in range(height):
            res_code = _validate_img(width, height, x, y, pix)
            if res_code == 1:
                for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    nx, ny = x+dx, y+dy
                    rgb_dict[pix[nx, ny]] += 10
                rgb_dict[pix[x, y]] += 10
            elif res_code == 3:
                rgb_dict[pix[x, y]] += 1
            else:
                img.putpixel((x,y),(255, 255, 255))
    # Remove noise lines and color verify code in black
    rank = sorted(rgb_dict.items(), key = lambda k_v : k_v[1])
    color_set = set([colr[0] for colr in rank[-4:]])
    pix = img.load()
    for x in range(width):
        for y in range(height):
            p = (255, 255, 255) if pix[x, y] not in color_set else (0, 0, 0)
            img.putpixel((x, y), p)
    # Cut image vertically for recognition
    left = right = top = 0
    bottom = height - 1
    is_white = True
    is_char = False
    for x in range(width):
        for y in range(height):
            rgb = pix[x, y][:3]
            if y == 0:
                is_white = True
            elif rgb == (0, 0, 0):
                is_white = False
            if not is_white and not is_char:
                is_char = True
                left = x - 3
        if is_char and is_white:
            is_char = False
            right = x + 3
            c_img = img.crop((left, top, right, bottom))
            c_img = c_img.resize((c_img.size[0]*2, c_img.size[1]*2))

            char = pytesseract.image_to_string(c_img, lang='verify-codes', config='--psm 10')

            for i in char:
                if i.isalnum:
                    ans += i
                    break

    return ans

def _validate_img(width, height, x, y, pix):
    direct = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    diff = same = 0
    for dx, dy in direct:
        nx, ny = x+dx, y+dy
        if 0 <= nx and nx < width and 0 <= ny and ny < height:
            if  pix[x, y] == pix[nx, ny]:
                same += 1
            else:
                diff += 1
        else:
            diff += 1
    if diff == 4:
        # Invalid case
        return 0
    elif same == 4:
        # Full valid case
        return 1
    else:
        # Partial valid case
        return 3










