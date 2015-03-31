import os
import logging
from configparser import ConfigParser
from configparser import ParsingError
from base64 import b64encode

import requests
from bs4 import BeautifulSoup


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

class AberSites(object):
    def __init__(self, user, passw):
        pass

def get_int_usage(user, passw):
    page_url = 'https://myaccount.aber.ac.uk/protected/traffic/'
    #Steps to login Shibolleth/SAML
    s1 = 'https://shibboleth.aber.ac.uk/idp/AuthnEngine'
    s2 = 'https://shibboleth.aber.ac.uk/idp/Authn/RemoteUser'
    s3 = 'https://shibboleth.aber.ac.uk/idp/profile/Shibboleth/SSO'
    s4 = 'https://myaccount.aber.ac.uk/Shibboleth.sso/SAML/POST'

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36"

    session = requests.session()
    session.headers.update({'User-Agent': user_agent})
    auth = (user, passw)

    r = session.get(page_url, allow_redirects=False)
    location = r.headers['location']
    session.headers.update({'Host': 'shibboleth.aber.ac.uk',
                            'Referer': 'https://myaccount.aber.ac.uk/'})
    r = session.get(location, auth=auth, allow_redirects=False)
    r = session.get(s1, auth=auth , allow_redirects=False)
    r = session.get(s2, auth=auth , allow_redirects=False)
    r = session.get(s3, auth=auth , allow_redirects=False)
    # Retrieving the SAMLResponse and target
    soup = BeautifulSoup(r.content)
    target = soup.find('input', {'name': 'TARGET'}).get('value')
    SAMLResponse = soup.find('input', {'name': 'SAMLResponse'}).get('value')
    payload = {'SAMLResponse':SAMLResponse, 'TARGET': target}
    session.headers.update({'Host':'myaccount.aber.ac.uk',
                            'Origin':'https://shibboleth.aber.ac.uk',
                            'Referer':'https://shibboleth.aber.ac.uk/idp/profile/Shibboleth/SSO'})

    r = session.post(s4, data=payload)

    
    print(r.text)
    #print(request.__dict__)
    #print(session.headers)
    print(requests.utils.dict_from_cookiejar(session.cookies))
    #for h in r.history:
    #    print(h.url)
    # print(request.headers)
    # print(b64_p)
    # print(session.headers)


def get_timetable(user, passw):
    login_url = 'https://studentrecord.aber.ac.uk/en/index.php'
    page_url = 'https://studentrecord.aber.ac.uk/en/timetable.php'
    session = requests.session()
    login_data = dict(username=user, password=passw, doLogin='doLogin')
    session.post(login_url, data=login_data)
    request = session.get(page_url)
    print(request.content)


def main():
    config_dir = os.path.expanduser('~/.aberquota/')
    config_file = 'config.ini'

    logging.basicConfig(
        format='%(levelname)s:%(message)s',
        level=logging.DEBUG)

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

    get_int_usage(user, passw)


if __name__ == '__main__':
    main()
