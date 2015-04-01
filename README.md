# Description
Python3 tool for getting internet usage off the Aberystwyth University network.

# Config
The config.ini file found in __/home/{your-user}/.aberquota/config.ini__ needs to be edited to contain your username and password.


Downloaded images are placed in the same directory.
# Installation
A Python3 interpreter must be used.

Using setup.py:
```
  python3 setup.py install
```
Using pip:
```
  pip/pip3 install aberquota
```
### Dependencies
1. BeautifulSoup4
2. Requests

# Usage
```
usage: aberquota [-h] [--sentence] [-s] [-i] [-p] [-f] [--image] [-v]
                 [--debug]

optional arguments:
  -h, --help      show this help message and exit
  --sentence      internet usage as it appears on the website
  -s, --string    internet usage including units
  -i, --int       internet usage without units
  -p, --percent   internet usage as a percentage
  -f, --fraction  internet usage as a fraction
  --image         downloads and saves Internet usage chart
  -v, --verbose   increase output verbosity
  --debug         prints debug info
```