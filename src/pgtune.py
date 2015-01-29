#!/usr/bin/env python2.7
# encoding: utf-8

'''
pgtune -- postgresql.conf performance tuner

pgtune prints generalized performance optimizations for postgresql.conf
given the optional inputs max_connections and allocated memory fraction. The
values can be saved to a file which can be used by postgresql.conf with the
include directive, as for example:
  include 'postgresql.conf.custom'

For usage help:
  $ pgtune -h

https://github.com/impredicative/pgtune
'''

from __future__ import print_function
import argparse
import collections
import math
import os

MEM_TOTAL = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')  # bytes


def format_bytes(n):

    units = ('', 'KB', 'MB', 'GB')  # Restricted per section 18.1.1 in v9.2.
    base = 1024
    decrement_threshold = 0.2  # Experimental
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
                        type=int, default=100,
                        help="minimally necessary maximum connections (default: %(default)s)")

    mem_str = format_bytes(MEM_TOTAL)
    parser.add_argument('-f', '--mem_fraction', dest='mem_fraction',
                        type=float, default=1.0,
                        help="fraction of total physical memory ({}) to use (default: %(default)s)".format(mem_str))

#     parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
#     parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
#     parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
#     parser.add_argument("-i", "--include", dest="include", help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="RE" )
#     parser.add_argument("-e", "--exclude", dest="exclude", help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="RE" )
#     parser.add_argument('-V', '--version', action='version', version=program_version_message)
#     parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')

    return parser.parse_args()


def tune_conf(args):

    mem_fractional = int(MEM_TOTAL * args.mem_fraction)  # floor is implicit
    conf = c = collections.OrderedDict()

    c['max_connections'] = args.max_connections

    return conf


def print_conf(conf):

    for i in conf.items():
        print('{} = {}'.format(*i))


def main():

    args = parse_args()
    conf = tune_conf(args)
    print_conf(conf)


if __name__ == "__main__":
    main()
