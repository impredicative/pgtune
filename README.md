# pgtune

**pgtune** prints generalized performance optimizations for `postgresql.conf` given the optional inputs `max_connections` and `mem_fraction`.

For help: `$ pgtune.py -h`

**CAUTION:** This software is experimental. Use of benchmark tests, perhaps with `pgbench`, is advisable.

https://github.com/impredicative/pgtune/

## Example
### Usage example
```
$ ./pgtune.py --max_connections=32 --mem_fraction=0.5
# pgtune configuration for connections=32 and memory=938MB.

# CONNECTIONS AND AUTHENTICATION
max_connections = 32

# RESOURCE USAGE (except WAL)
shared_buffers = 234MB
temp_buffers = 18MB
work_mem = 8MB
maintenance_work_mem = 46MB
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
effective_cache_size = 586MB
```

### Inclusion example
The printed values can be written to a file which can be used by `postgresql.conf` with the *include directive*, as for example:

`include 'postgresql.conf.custom'`

## License

See [license](LICENSE).
