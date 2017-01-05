#!/usr/bin/env python3

import os
import argparse

from http.cookiejar import CookieJar
from urllib.parse import urlencode
import urllib.request
import configparser

def setup_argument_parser():
    """Set up command line options.  -h or --help for help is automatic"""
    test_url = "http://e4ftl01.cr.usgs.gov/MOLA/MYD17A3H.006/2009.01.01/MYD17A3H.A2009001.h12v05.006.2015198130546.hdf.xml"
    p = argparse.ArgumentParser()
    p.add_argument('-o', '--outfile', help='Output file name')
    p.add_argument('-u', '--url', default=test_url,  help='URL of desired data file')
    p.add_argument('-q', '--quiet',   action='store_true', default=False, help="Quiet mode.  Don't print status messages")
    # nargs can be '+' for "one or more"
    return(p)


def main():

    p = setup_argument_parser()
    args = p.parse_args()

    if not args.quiet:
        print("Reading credentials")

    configfile = os.path.join(os.environ['HOME'], '.earthdata_get_data.ini')
    config = configparser.RawConfigParser()
    config.read(configfile)

    username = config.get('credentials', 'username')
    password = config.get('credentials', 'password')

    url = args.url

    if not args.quiet:
        dest = args.outfile or 'standard output'
        print("Fetching ", url)
        print("Sending to", dest)

    # Create a password manager to deal with the 401 reponse that is returned from
    # Earthdata Login

    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, "https://urs.earthdata.nasa.gov", username, password)
    password_manager.add_password(None, "https://cdn.earthdata.nasa.gov", username, password)
    password_manager.add_password(None, "https://n5eil01u.ecs.nsidc.org", username, password)

    # Create a cookie jar for storing cookies. This is used to store and return
    # the session cookie given to use by the data server (otherwise it will just
    # keep sending us back to Earthdata Login to authenticate).  Ideally, we
    # should use a file based cookie jar to preserve cookies between runs. This
    # will make it much more efficient.

    cookie_jar = CookieJar()


    # Install all the handlers.

    opener = urllib.request.build_opener(
        urllib.request.HTTPBasicAuthHandler(password_manager),
        #urllib.request.HTTPHandler(debuglevel=1),    # Uncomment these two lines to see
        #urllib.request.HTTPSHandler(debuglevel=1),   # details of the requests/responses
        urllib.request.HTTPCookieProcessor(cookie_jar))
    urllib.request.install_opener(opener)


    # Create and submit the request. There are a wide range of exceptions that
    # can be thrown here, including HTTPError and URLError. These should be
    # caught and handled.

    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)


    # Print out the result (not a good idea with binary data!)

    body = response.read()
    if args.outfile:
        with open(args.outfile, 'wb') as fp:
            fp.write(body)
    else:
        print(body)


if __name__ == '__main__':
    main()
