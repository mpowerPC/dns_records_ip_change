# -*- coding: utf-8 -*-
"""
dns_records_ip_change.main
~~~~~~~~~~~~~
@author: mpowerPC

A simple script to update dns records for a website that has a dynamic ip. Uses
https://github.com/mpowerPC/cloudflare_dns_api to change the DNS records on Cloudflare and ipify.org to get the public
ip address.

Too run, a file named credentials.json must be placed in the folder with a working Cloudflare API token in it. The
associated account must also have a zone to test adding and removing dns records.

EXAMPLE "credentials.json" FILE:
{
    "token": "YQSn-xWAQiiEh9qM58wZNnyQS7FUdoqGIUAbrh7T",
    "zone": "example.com"
}
"""
import cloudflare_dns_api.CloudflareDNS as CloudflareDNS
import requests
import logging.config
import json
import os


def main():
    directory = os.path.dirname(os.path.realpath(__file__))

    logging_file = os.path.join(directory, "logging.ini")
    if os.path.exists(logging_file):
        logging.config.fileConfig(logging_file)

    logger = logging.getLogger(__name__)

    logger.debug("Initialized: dns_records_ip_change.py")

    credentials_file = os.path.join(directory, "credentials.json")
    try:
        with open(credentials_file) as f:
            cfg = json.load(f)
            token = cfg["token"]
            zone_name = cfg["zone"]
    except Exception as e:
        logger.exception("File not found: credentials.json")
        raise e

    cfd = CloudflareDNS.CloudflareDNS(token)

    try:
        response = requests.get("https://api.ipify.org?format=json")
    except Exception as e:
        logger.exception("Issue with connection to api.ipify.org.")
        raise e

    public_ip = None
    if response.status_code == 200:
        public_ip = response.json()["ip"]

    logger.debug("Public IP: " + public_ip)

    dns_record = None
    if public_ip:
        records = cfd.get_records(zone_name)
        dns_record = records[zone_name, 'A']

    logger.debug("DNS Record: " + json.dumps(dns_record))

    if dns_record:
        if dns_record["content"] != public_ip:
            logger.info("DNS record updating from " + dns_record["content"] + " to " + public_ip + ".")
            dns_record["content"] = public_ip

            try:
                cfd.update_record(zone_name, dns_record)
            except Exception as e:
                logger.exception("Issue updating DNS record.")
                raise e

    logger.debug("Success: dns_records_ip_change")


if __name__ == "__main__":
    main()

