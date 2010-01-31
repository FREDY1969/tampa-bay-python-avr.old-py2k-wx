#!/usr/bin/python

# load.py memory_type

import os
import sys
import optparse

from doctest_tools import setpath
setpath.setpath(__file__, remove_first = True)

import wx
from ucc.parser import load
import ucc.config

config = ucc.config.load()

class options_dict(dict):
    def __setattr__(self, key, value):
        if value is not None:   
            self[key] = value

def run():
    optparser = optparse.OptionParser(
                  usage="usage: %s [options] [load_dir [memory_type]]" % 
                          os.path.basename(sys.argv[0]))

    optparser.add_option('--install_dir',
      help='the location of the arduino-xxxx directory downloaded from arduino.cc')
    optparser.add_option('--avrdude_port',
      help='the pseudo serial device on your PC that talks to the Arduino')
    optparser.add_option('--mcu',
      help='the microcontroller chip')
    optparser.add_option('--avr_dude_path',
      help='the subdirectory under --install_dir containing the avrdude program')
    optparser.add_option('--avr_config_path',
      help='the subdirectory under --install_dir containing avrdude.conf')
    optparser.add_option('--upload_rate',
      help='the upload baud rate')
    optparser.add_option('--avrdude_programmer',
      help='the download protocol to use')
    optparser.set_defaults()

    options, args = optparser.parse_args(values=options_dict())

    kw_args = dict((param, config.get('arduino', param))
        for param in (
            'install_dir',
            'avrdude_port',
            'mcu',
            'avr_dude_path',
            'avr_config_path',
            'avrdude_programmer',
            'upload_rate'
        ) if Registry.config.has_option('arduino', param)
    )
    for k in kw_args.keys():
        if options.has_key(k): continue
        else: options[k] = kw_args[k]
        
    load_path = args[0]
    for memory_type in 'flash', 'eeprom':
        if os.path.exists(os.path.join(load_path, memory_type + '.hex')):
            print "loading", memory_type + '.hex'
            load.run(load_path=load_path, memory_type=memory_type,
                     **kw_args)
    
    load.run(*args, **options)

if __name__ == '__main__':
    run()