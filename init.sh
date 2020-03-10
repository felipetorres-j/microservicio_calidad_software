#!/bin/bash
rm docker/timescale/init.sql

sed 's/#COUNTRY/cl/' docker/timescale/init.sqlin >> docker/timescale/init.sql
sed 's/#COUNTRY/mx/' docker/timescale/init.sqlin >> docker/timescale/init.sql


