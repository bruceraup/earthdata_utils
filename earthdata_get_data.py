#!/usr/bin/env python

import os
import argparse
from cookielib import CookieJar
from urllib import urlencode
import urllib2
import ConfigParser

def setup_argument_parser():
    """Set up command line options.  -h or --help for help is automatic"""
    test_url = "http://e4ftl01.cr.usgs.gov/MOLA/MYD17A3H.006/2009.01.01/MYD17A3H.A2009001.h12v05.006.2015198130546.hdf.xml"
    p = argparse.ArgumentParser()
    p.add_argument('-o', '--outfile', default='earthdata_outfile.xml',  help='Output file name')
    p.add_argument('-u', '--url', default=test_url,  help='URL of desired data file')
    p.add_argument('-q', '--quiet',   action='store_true', default=False, help="Quiet mode.  Don't print status messages")
    # nargs can be '+' for "one or more"
    return(p)


def main():

    p = setup_argument_parser()
    args = p.parse_args()

    if not args.quiet:
        print "Reading credentials"

    configfile = os.path.join(os.environ['HOME'], '.earthdata_get_data.ini')
    config = ConfigParser.RawConfigParser()
    config.read(configfile)

    username = config.get('credentials', 'username')
    password = config.get('credentials', 'password')

    url = args.url

    if not args.quiet:
        print "Fetching ", url

    # Create a password manager to deal with the 401 reponse that is returned from
    # Earthdata Login

    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, "https://urs.earthdata.nasa.gov", username, password)


    # Create a cookie jar for storing cookies. This is used to store and return
    # the session cookie given to use by the data server (otherwise it will just
    # keep sending us back to Earthdata Login to authenticate).  Ideally, we
    # should use a file based cookie jar to preserve cookies between runs. This
    # will make it much more efficient.

    cookie_jar = CookieJar()


    # Install all the handlers.

    opener = urllib2.build_opener(
        urllib2.HTTPBasicAuthHandler(password_manager),
        #urllib2.HTTPHandler(debuglevel=1),    # Uncomment these two lines to see
        #urllib2.HTTPSHandler(debuglevel=1),   # details of the requests/responses
        urllib2.HTTPCookieProcessor(cookie_jar))
    urllib2.install_opener(opener)


    # Create and submit the request. There are a wide range of exceptions that
    # can be thrown here, including HTTPError and URLError. These should be
    # caught and handled.

    request = urllib2.Request(url)
    response = urllib2.urlopen(request)


    # Print out the result (not a good idea with binary data!)

    body = response.read()
    print body


if __name__ == '__main__':
    main()
