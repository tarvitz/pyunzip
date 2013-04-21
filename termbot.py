#!/usr/bin/env python
import telnetlib
t = telnetlib.Telnet('localhost',40001)
t.write('terminate_bot\r\n')
t.read_all()

