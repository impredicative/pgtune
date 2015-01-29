# pgtune

pgtune prints generalized performance optimizations for postgresql.conf given the optional inputs max_connections and memory fraction. The printed values can be saved to a file which can be used by postgresql.conf with the include directive, as for example:

include 'postgresql.conf.custom'

For help: $ pgtune.py -h

https://github.com/impredicative/pgtune