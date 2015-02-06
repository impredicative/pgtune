# pgtune

**pgtune** prints generalized performance optimizations for `postgresql.conf` for PostgreSQL 9.x using the optional inputs `max_connections` and `mem_fraction`. The original `postgresql.conf` file is not an input.

**CAUTION:** This software is experimental. Use of benchmark tests, perhaps with `pgbench`, is advisable.

https://github.com/impredicative/pgtune/

## Contents

- [Help](#help)
- [Examples](#examples)
	- [Shell usage](#shell-usage)
	- [Module usage](#module-usage)
	- [Bulk loading comparison](#bulk-loading-comparison)
	- [Inclusion](#inclusion)
- [References](#references)
- [License](#license)

## Help
```
$ ./pgtune.py -h
usage: pgtune.py [-h] [-b] [-c MAX_CONNECTIONS] [-f MEM_FRACTION]

postgresql.conf tuner

optional arguments:
  -h, --help            show this help message and exit
  -b, --bulk-load       for temporary use while bulk loading (default: false)
  -c MAX_CONNECTIONS, --max-connections MAX_CONNECTIONS
                        minimally necessary maximum connections (default: 100)
                        (min: 1)
  -f MEM_FRACTION, --mem-fraction MEM_FRACTION
                        fraction (>0 to 1.0) of total physical memory (1877MB)
                        to consider (default: 1.0)
```

## Examples
### Shell usage
```
$ ./pgtune.py --max-connections=32
# pgtune configuration with connections=32 and memory=1877MB.

# CONNECTIONS AND AUTHENTICATION
max_connections = 32

# RESOURCE USAGE (except WAL)
shared_buffers = 469MB
temp_buffers = 45MB
work_mem = 21MB
maintenance_work_mem = 93MB
max_stack_depth = 8MB
vacuum_cost_delay = 50ms
effective_io_concurrency = 4

# WRITE AHEAD LOG
synchronous_commit = off
wal_buffers = 16MB
wal_writer_delay = 10s
checkpoint_segments = 64
checkpoint_timeout = 10min
checkpoint_completion_target = 0.8

# QUERY TUNING
random_page_cost = 2.5
effective_cache_size = 1173MB
```

### Module usage
```python
import pgtune
pgtune.settings.update({'max_connections': 64, 'mem_fraction': 0.5, 'bulk_load': False})  # as needed
print(pgtune.conf_text())
```

### Bulk loading comparison
```
$ diff -ty --suppress-common-lines -W 60 <(./pgtune.py -c16) <(./pgtune.py --bulk-load -c16) | sed '1d'
work_mem = 41MB              |  work_mem = 45MB
maintenance_work_mem = 93MB  |  maintenance_work_mem = 234MB
                             >  wal_level = minimal
                             >  fsync = off
                             >  full_page_writes = off
checkpoint_segments = 64     |  checkpoint_segments = 128
checkpoint_timeout = 10min   |  checkpoint_timeout = 30min
                             >  archive_mode = off
                             >
                             >  # REPLICATION
                             >  max_wal_senders = 0
                             >
                             >  # AUTOVACUUM PARAMETERS
                             >  autovacuum = off
```

### Inclusion
The printed values can be written to a file which can be used by `postgresql.conf` with the *include directive*, as for example:

`include 'postgresql.conf.tuned'`

## References
1. [PostgreSQL 9.2 Documentation - Chapter 14. Performance Tips](http://www.postgresql.org/docs/9.2/static/performance-tips.html)
2. [PostgreSQL 9.2 Documentation - Chapter 18. Server Configuration](http://www.postgresql.org/docs/9.2/static/runtime-config.html)
3. [PostgreSQL Wiki - Tuning Your PostgreSQL Server](http://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)
4. [PostgreSQL 9.0 High Performance (2010)](http://www.amazon.com/PostgreSQL-High-Performance-Gregory-Smith/dp/184951030X)
5. [PostgreSQL Administration Essentials (2014)](http://www.amazon.com/PostgreSQL-Administration-Essentials-Hans-Jurgen-Schonig/dp/1783988983/)
6. [PostgreSQL Proficiency for Python People - PyCon 2014](https://www.youtube.com/watch?v=0uCxLCmzaG4)


## License

See [license](LICENSE).
