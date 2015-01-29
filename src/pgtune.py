#!/usr/bin/env python2.7
# encoding: utf-8

'''
pgtune -- postgresql.conf tuner

pgtune prints generalized performance optimizations for postgresql.conf
given the optional inputs max_connections and allocated memory fraction. The
values can be saved to a file which can be used by postgresql.conf with the
include directive, as for example:
  include 'postgresql.conf.custom'

For help:
  $ ./pgtune.py -h

https://github.com/impredicative/pgtune
'''

from __future__ import print_function
import argparse
import collections
import math
import os

K = 1024**1
M = 1024**2
G = 1024**3

settings = {
'mem_total': os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')  # bytes
}


def format_bytes(n):

    units = ('', 'kB', 'MB', 'GB')  # Restricted per section 18.1.1 in v9.2.
    base = 1024
    decrement_threshold = 0.2  # experimental
    divisor_max = len(units) - 1

    exponent = math.log(n, base) if n > 0 else 0
    remainder = exponent % 1
    exponent = int(exponent)  # implicit floor

    decrement = int(0 < remainder < decrement_threshold)
    divisor = max(0, exponent - decrement)
    divisor = min(divisor, divisor_max)

    quotient = int(n/(base**divisor))  # implicit floor
    unit = units[divisor]
    return "{}{}".format(quotient, unit)


def parse_args():

    parser = argparse.ArgumentParser(description='postgresql.conf tuner')

    parser.add_argument('-c', '--max_connections', dest='max_connections',
                        type=lambda s: max(1, int(s)),
                        default=100,
                        help='minimally necessary maximum connections '
                             '(default: %(default)s)')

    mem_str = format_bytes(settings['mem_total'])
    parser.add_argument('-f', '--mem_fraction', dest='mem_fraction',
                        type=lambda s: max(0, float(s)),
                        default=1.0,
                        help=('fraction (>0 to 1.0) of total physical memory '
                              '({}) to consider '
                              '(default: %(default)s)').format(mem_str))

    args = parser.parse_args()
    for k, v in args._get_kwargs():
        settings[k] = v

    settings['mem_fractional'] = int(settings['mem_total'] *
                                     settings['mem_fraction']) # implicit floor
    settings['mem_fractional'] = max(1, settings['mem_fractional'])


def tune_conf():

    m = settings['mem_fractional']
    conf = c = collections.OrderedDict()
    fb = format_bytes

    c['max_connections'] = settings['max_connections']

    c['shared_buffers'] = fb(m*.25)  # Not restricted to 8G.
    c['effective_cache_size'] = fb(m*.625)

    return conf


def print_conf(conf):

    print('# pgtune configuration for connections={} and memory={}.\n'
          .format(settings['max_connections'],
                  format_bytes(settings['mem_fractional'])))

    for i in conf.items():
        print('{} = {}'.format(*i))


def main():

    parse_args()
    conf = tune_conf()
    print_conf(conf)


if __name__ == "__main__":
    main()
