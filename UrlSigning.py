#!/usr/bin/env python

import md5
import base64
from optparse import OptionParser
import os


# Example: Generate url signed link for resource https://www.example.com/images/photo.png
# python UrlSigning.py -r example.com -p images/photo.png -k abc123 -s https
def sign_url(resource, path, key, scheme, expires, ip):
    """
    Generate URL signed CDN resource
    :param resource: The CDN resource (without scheme). e.g. "cdn.yourdomain.com"
    :param path: File path of the CDN resource as part of token key. e.g. "/", "/files", "/files/file.html"
                 **note: for HLS, it is better to put path instead of .m3u8 file, so that all the chunk of the hls will be authenticated as well.
    :param key: The URL signing key
    :param scheme: The scheme for CDN Resource URL. e.g. "http" or "https"
    :param expires: The expiration of the URL. This is in Unix timestamp format. This is optional.
    :param ip: The IPs that allow to access. This is optional.
    :return: string URL with generated token
    """

    #  1. Setup Token Key
    #  1.1 Prepend leading slash if missing
    path = os.path.join("/", path) if path[0] != "/" else path

    # 1.2 Extract uri, ignore query string arguments
    url = resource.split("?")[0]

    # 1.3 Formulate the token key
    token = expires + path + key + ip

    # 2. Setup URL
    # 2.1 Append argument - secure (compulsory)
    url_secures = ''.join(["?secure=", base64.encodestring(md5.md5(token).digest()).replace("+","-").replace("/","_").replace("=","").split("\n")[0]])

    # 2.2 Append argument - expires
    url_expires = "&expires=" + expires if expires else ""

    # 2.3 Append argument - ip
    url_ip = "&ip=" + ip if ip else ""

    return scheme + "://" + url + path + url_secures + url_expires + url_ip


def main():
    parser = OptionParser()
    parser.add_option("-r", "--resource", dest="resource")
    parser.add_option("-e", "--expires", dest="expires", default="")
    parser.add_option("-p", "--path", dest="path", default="/")
    parser.add_option("-k", "--key", dest="key", default="")
    parser.add_option("-i", "--ip", dest="ip", default="")
    parser.add_option("-s", "--scheme", dest="scheme", default="http")

    (option, args) = parser.parse_args()

    if not option.key:
        parser.error("Key not given")

    if not option.resource:
        parser.error("Resource hostname not given")

    if not option.path:
        parser.error("Path not given")

    print sign_url(resource=option.resource, path=option.path, key=option.key, scheme=option.scheme, expires=option.expires, ip=option.ip)


if __name__ == '__main__':
    main()
