import argparse
import os
import logging
from base64 import b64decode
from configparser import ConfigParser
from configparser import ParsingError

import requests
from bs4 import BeautifulSoup

def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sentence', help="internet usage as it appears on the website", action='store_true')
    parser.add_argument('-s', '--string', help="internet usage including units", action='store_true')
    parser.add_argument('-i', '--int', help="internet usage without units", action='store_true')
    parser.add_argument('-p','--percent', help="internet usage as a percentage", action='store_true')
    parser.add_argument('-f','--fraction', help="internet usage as a fraction", action='store_true')
    parser.add_argument('--image', help="downloads and saves Internet usage chart", action='store_true')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action='store_true')
    parser.add_argument("--debug", help="prints debug info", action='store_true')
    return parser

def check_config(dir_path, file):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    if not os.path.isfile(os.path.join(dir_path, file)):
        return False
    return True


def create_config(path, user='user', passw='pass', exit=True):
    config = ConfigParser()
    config['ACCOUNT'] = {'username': user,
                         'password': passw}
    with open(path, 'w') as configfile:
        config.write(configfile)
        logging.warning("Config file created at {}\n"
                        "Replace username and password".format(path))
    if exit:
        raise SystemExit(0)


def load_config(path):
    config = ConfigParser()
    try:
        config.read(path)
    except ParsingError as e:
        logging.error("Problem parsing config file")
        logging.debug(e)
        raise SystemExit(0)
    except:
        raise
    return config


class OutputHandler(object):
    def __init__(self, string, b64_img=None):
        self.string = string
        if b64_img:
            self.b64_img = b64_img

    def as_sentence(self):
        return self.string

    def as_string(self):
        msg = self.string.split(' ')[-1]
        return msg

    def as_int(self):
        msg = self.string.split(' ')[-1][:-2]
        return msg

    def as_fraction(self, denominator=12000, unit='MB', str_fmt="{}/{}"):
        numerator = self.as_int()
        n = ''.join((str(int(numerator)), unit))
        d = ''.join((str(int(denominator)), unit))
        msg = str_fmt.format(n, d)
        return msg

    def as_percentage(
            self,
            denominator=12000,
            calculated=None,
            symbol=''):
        if calculated:
            msg = str(calculated)
        else:
            numerator = self.as_int()
            msg = str(int(int(numerator) / int(denominator) * 100))
        if symbol:
            ''.join((msg, symbol))
        return msg

    def save_b64_to_png(self, dir_path, file_name):
        if not file_name.endswith('.png'):
            file_name = ''.join((file_name, '.png'))
        img = open(os.path.join(dir_path, file_name), 'wb')
        img.write(b64decode(self.b64_img))
        img.close()
        logging.info("Image saved to {}".format(os.path.join(dir_path, file_name)))


class AberSites(object):

    def __init__(self, user, passw):
        self.session_setup(user, passw)
        self.shib_auth()

    def session_setup(self, user, passw):
        user_agent = ("Mozilla/5.0 (X11; Linux x86_64)"
                      " AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/41.0.2272.101 Safari/537.36")

        session = requests.session()
        session.headers.update({'User-Agent': user_agent})
        session.auth = (user, passw)
        self.session = session

    def shib_auth(self):
        login_url = 'https://myaccount.aber.ac.uk/protected/'

        # Steps to authenticate with Shibolleth/SAML
        s1 = 'https://shibboleth.aber.ac.uk/idp/AuthnEngine'
        s2 = 'https://shibboleth.aber.ac.uk/idp/Authn/RemoteUser'
        s3 = 'https://shibboleth.aber.ac.uk/idp/profile/Shibboleth/SSO'
        s4 = 'https://myaccount.aber.ac.uk/Shibboleth.sso/SAML/POST'

        r = self.session.get(login_url, allow_redirects=False)
        location = r.headers['location']
        self.session.headers.update(
            {'Host': 'shibboleth.aber.ac.uk', 'Referer': 'https://myaccount.aber.ac.uk/'})

        r = self.session.get(location, allow_redirects=False)
        r = self.session.get(s1, allow_redirects=False)
        r = self.session.get(s2, allow_redirects=False)
        # Retrieving the SAMLResponse and target
        r = self.session.get(s3, allow_redirects=False)
        soup = BeautifulSoup(r.content)
        target = soup.find('input', {'name': 'TARGET'}).get('value')
        SAMLResponse = soup.find(
            'input', {
                'name': 'SAMLResponse'}).get('value')
        payload = {'SAMLResponse': SAMLResponse, 'TARGET': target}
        self.session.headers.update(
            {
                'Host': 'myaccount.aber.ac.uk',
                'Origin': 'https://shibboleth.aber.ac.uk',
                'Referer': 'https://shibboleth.aber.ac.uk/idp/profile/Shibboleth/SSO'})
        r = self.session.post(s4, data=payload)

    def get_int_usage(self):
        page_url = 'https://myaccount.aber.ac.uk/protected/traffic/'
        r = self.session.get(page_url)

        soup = BeautifulSoup(r.text)
        content = soup.find('div', {'id': 'webapp'})
        usage = content.find('p').getText()
        string = ''.join(usage.split('\n'))

        b64_img = content.find('img')['src'].split(',')[1]
        return (string, b64_img)

    def get_timetable(self):
        login_url = 'https://studentrecord.aber.ac.uk/en/index.php'
        page_url = 'https://studentrecord.aber.ac.uk/en/timetable.php'
        session = requests.session()
        login_data = dict(username=user, password=passw, doLogin='doLogin')
        session.post(login_url, data=login_data)
        request = session.get(page_url)
        print(request.content)


def main():
    parser = arg_parser()
    args = parser.parse_args()

    config_dir = os.path.expanduser('~/.aberquota/')
    config_file = 'config.ini'

    level = logging.WARNING
    if args.verbose:
        level = logging.INFO
    if args.debug:
        level = logging.DEBUG

    logging.getLogger('requests').setLevel(level)
    logging.basicConfig(
        format='%(message)s',
        level=level)

    if not check_config(config_dir, config_file):
        create_config(os.path.join(config_dir, config_file))
    config = load_config(os.path.join(config_dir, config_file))
    user, passw = ('', '')
    try:
        user = config['ACCOUNT']['username']
        passw = config['ACCOUNT']['password']
    except KeyError as e:
        logging.error("Problem parsing config file")
        logging.debug(e)
        raise SystemExit(0)

    site = AberSites(user, passw)
    string, b64_img = site.get_int_usage()
    oh = OutputHandler(string, b64_img)    
    
    if args.string:
        print(oh.as_string())
    if args.int:
        print(oh.as_int())
    if args.sentence:
        print(oh.as_sentence())
    if args.percent:
        print(oh.as_percentage())
    if args.fraction:
        print(oh.as_fraction())
    if args.image:
        oh.save_b64_to_png(config_dir, 'usage.png')


