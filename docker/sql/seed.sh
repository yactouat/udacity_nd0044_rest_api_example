#!/bin/bash

export PGPASSWORD='pwd'
psql -U 'usr' -d 'rest' -a -f /sql/rest.psql