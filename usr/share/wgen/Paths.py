#!/usr/bin/python3
#

#  Copyright (C) 2014-2015, 2018  Rafael Senties Martinelli 
#
#  This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License 3 as published by
#   the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA.

import os
import getpass

class Paths:
    
    def __init__(self):
        
        self.current_dir=os.getcwd()        
        
        self.output_folder='{0}/wgen-files'.format(self.current_dir)
        
        self.output_subfolder='{0}/comb_{1}'.format(self.output_folder,'{0}')
        
        self.default_input_list='{0}/wgen-words'.format(self.current_dir)

        self.debug_file='{0}/wgen-ERRORS'.format(self.current_dir)

        current_user=getpass.getuser()
        if current_user=='root':
            self.configuration='/root/.config/wgen.ini'
        else:
            self.configuration='/home/{0}/.config/wgen.ini'.format(current_user)

        self.cracking_loop_temp='/tmp/loop-{0}-{1}'.format(current_user,'{0}')
        self.uri='/tmp/wgen-URI-{0}'.format(current_user)
        self.stop_loop_file='/tmp/wgen-STOP-{0}'.format(current_user)



if __name__ == '__main__':
    p=Paths()
    print(p.current_dir)
    print(p.default_input_list)

