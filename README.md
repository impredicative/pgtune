# pgtune

**pgtune** prints generalized performance optimizations for postgresql.conf given the optional inputs `max_connections` and `mem_fraction`.

For help: `$ pgtune.py -h`

https://github.com/impredicative/pgtune/

## Example
### Usage example
```
$ ./pgtune.py -c 32
# pgtune configuration for connections=32 and memory=1877MB.

max_connections = 32
shared_buffers = 469MB
effective_cache_size = 1173MB
temp_buffers = 36MB
work_mem = 17MB
maintenance_work_mem = 93MB
checkpoint_segments = 64
checkpoint_timeout = 10min
checkpoint_completion_target = 0.8
wal_buffers = 16MB
wal_writer_delay = 10s
vacuum_cost_delay = 50ms
random_page_cost = 2.5
effective_io_concurrency = 4
synchronous_commit = off
max_stack_depth = 8MB
```

### Inclusion example
The printed values can be saved to a file which can be used by postgresql.conf with the include directive, as for example:
`include 'postgresql.conf.custom'`

