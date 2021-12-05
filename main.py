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
import json
import os


def main():
    credentials_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "credentials.json")
    with open(credentials_file) as f:
        cfg = json.load(f)
        token = cfg["token"]
        zone_name = cfg["zone"]

    cfd = CloudflareDNS.CloudflareDNS(token)

    try:
        response = requests.get("https://api.ipify.org?format=json")
    except Exception as e:
        raise e

    public_ip = None
    if response.status_code == 200:
        public_ip = response.json()["ip"]

    dns_record = None
    if public_ip:
        records = cfd.get_records(zone_name)
        dns_record = records[zone_name, 'A']

    if dns_record:
        if dns_record["content"] != public_ip:
            dns_record["content"] = public_ip
            cfd.update_record(zone_name, dns_record)


if __name__ == "__main__":
    main()

