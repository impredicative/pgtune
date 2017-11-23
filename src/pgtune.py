#!/usr/bin/env python2.7
# encoding: utf-8

'''
pgtune -- postgresql.conf tuner

See README.md.
'''

from __future__ import print_function
import argparse
import collections
import math
import os

K, M, G = (1024**i for i in range(1, 4))
settings = {
'bulk_load': False,
'max_connections': 100,
'mem_fraction': 1.0,
'mem_total': os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'),  # Bytes
'autovacuum_max_workers': 3  # Default value in postgresql.conf.
}


def format_bytes(n):

    units = ('', 'kB', 'MB', 'GB')  # Restricted per section 18.1.1 in v9.3.
    base = 1024
    decrement_threshold = 0.2  # Value is experimental.
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


def _parse_args():

    parser = argparse.ArgumentParser(description='postgresql.conf tuner')

    parser.add_argument('-b', '--bulk-load', dest='bulk_load',
                        action='store_true',
                        help='for temporary use while bulk loading '
                             '(default: false)')

    parser.add_argument('-c', '--max-connections', dest='max_connections',
                        type=lambda s: max(1, int(s)),
                        default=settings['max_connections'],
                        help='minimally necessary maximum connections '
                             '(default: %(default)s) (min: 1)')

    mem_str = format_bytes(settings['mem_total'])
    parser.add_argument('-f', '--mem-fraction', dest='mem_fraction',
                        type=lambda s: max(0, float(s)),
                        default=settings['mem_fraction'],
                        help=('fraction (>0 to 1.0) of total physical memory '
                              '({}) to consider '
                              '(default: %(default)s)').format(mem_str))

    args = parser.parse_args()

    for k, v in args._get_kwargs():
        settings[k] = v


def _parse_settings():

    settings['mem_fractional'] = int(settings['mem_total'] *
                                     settings['mem_fraction']
                                     )  # implicit floor


def _conf_dict():

    _parse_settings()

    mem = settings['mem_fractional']
    bulk_load = settings['bulk_load']
    autovac_workers = 0 if bulk_load else settings['autovacuum_max_workers']
    used_connections = settings['max_connections'] * 0.8

    conf = collections.OrderedDict()
    # Note: Parameters below match the category and order in postgresql.conf.

    conf['CONNECTIONS AND AUTHENTICATION'] = s = collections.OrderedDict()
    s['max_connections'] = settings['max_connections']

    conf['RESOURCE USAGE (except WAL)'] = s = collections.OrderedDict()
    s['shared_buffers'] = format_bytes(min(mem*.25, 16*G))
    effective_cache_size = mem*.625
    s['temp_buffers'] = format_bytes(effective_cache_size /
                                     used_connections)  # Unsure.
    s['work_mem'] = format_bytes(effective_cache_size /
                    (used_connections * 2  # x by num active tables.
                     + autovac_workers))
    s['maintenance_work_mem'] = format_bytes((mem*.25) /  # No hard limit.
                                     (autovac_workers + 2))
    s['max_stack_depth'] = '8MB'  # 80% of `ulimit -s` (typically 10240KB)
    s['vacuum_cost_delay'] = '50ms'
    s['effective_io_concurrency'] = 4

    conf['WRITE AHEAD LOG'] = s = collections.OrderedDict()
    if bulk_load: s['wal_level'] = 'minimal'  # Default.
    if bulk_load: s['fsync'] = 'off'  # Unsafe.
    s['synchronous_commit'] = 'off'
    if bulk_load: s['full_page_writes'] = 'off'  # Unsafe.
    s['wal_buffers'] = '16MB'
    s['wal_writer_delay'] = '10s'
    s['checkpoint_segments'] = 128 if bulk_load else 64
    s['checkpoint_timeout'] = '30min' if bulk_load else '10min'
    s['checkpoint_completion_target'] = 0.8  # 0.9 may risk overlap with next.
    if bulk_load: s['archive_mode'] = 'off'  # Consistent with minimal wal.

    conf['REPLICATION'] = s = collections.OrderedDict()
    if bulk_load: s['max_wal_senders'] = 0  # Default.

    conf['QUERY TUNING'] = s = collections.OrderedDict()
    s['random_page_cost'] = 2.0
    s['effective_cache_size'] = format_bytes(effective_cache_size)

    conf['AUTOVACUUM PARAMETERS'] = s = collections.OrderedDict()
    if bulk_load: s['autovacuum'] = 'off'

    # Note: For bytea_output, per section 8.4 for v9.2, the default value of
    # 'hex' is faster than 'escape'.

    return conf


def conf_text():

    _parse_settings()
    conf_lines = []

    header = '# pgtune configuration{} with connections={} and memory={}.'
    conf_lines.append(header.format(' for bulk loading'
                                    if settings['bulk_load'] else '',
                                    settings['max_connections'],
                                    format_bytes(settings['mem_fractional'])))

    for section_name, section in _conf_dict().items():
        if section:
            conf_lines.append('\n# {}'.format(section_name))
            for i in section.items():
                conf_lines.append('{} = {}'.format(*i))

    return '\n'.join(conf_lines)


def _main():

    _parse_args()
    print(conf_text())


if __name__ == "__main__":
    _main()
