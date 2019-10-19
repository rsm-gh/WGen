#!/usr/bin/python3
#

#  Copyright (C) 2014-2016, 2018  Rafael Senties Martinelli 
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


"""
    - I tried to use regex for the "remove tests" option, but it seemed to fail. Sometimes it was returning true when
      the test didn't existed.  More information at the doc: Regex test
"""

import os
import time
import threading
import traceback
import socket

from datetime import datetime

# Local imports
from Paths import *; PATHS=Paths()
from Debug import W_try_or_log

Queue=[]

WRITE_LOOP=False #used to write_errors, it will write the cracking code


TAB='''    '''

REMOVE_COMBINATIONS='''
{tab}if remove_combinations.search(test_word{level}):
{tab}   self._count+=len_word_list**({lnb}-{inb})
{tab}   continue\n
'''

# Should the word be removed? remove_tests.remove(word) ?
REMOVE_TESTS='''
{tab}if test_word{level} in remove_tests:
{tab}    self._count+=1
{tab}    continue\n
'''

# Matching with re would be so much faster, saddly It couln't make it work
# for exact matches
#
#REMOVE_TESTS='''
#{tab}if remove_tests.match(test_word):
#{tab}    self._count+=1
#{tab}else:
#'''

REMOVE_NEXT_TO_NEXT='''
{tab}if word{inb2}==word{inb1}:
{tab}    self._count+=len_word_list**({lnb}-{inb})
{tab}    continue\n
'''

REMOVE_DUPLICATED='''
{tab}if len(current_word_list{level})!=len(set(current_word_list{level})):
{tab}    self._count+=len_word_list**({lnb}-{inb})
{tab}    continue\n'''


DEBUG_LOOPS_TEMPLATE='''
[{}]: Problem in loop...
    Starting Word: {}
    Stage: {}
    Substage: {}
    Count: {}
    Error:
{}\n
'''

def invert_bool(boolean):
    if boolean == False:
        return True
        
    return False
    
    
@W_try_or_log
def create_buteforce_attack(self, loops_number, starting_word, configuration, DEBUG):

    source ='''
def __bruteforce_attack_template__(self):
    
    try:
    
        write_wordlist_buffer_size=10**4 + 1
        write_wordlist_buffer=[]
        write_wordlist_count=0
        
        word_list=({})
        len_word_list=len(word_list)
'''.format(','.join(['"{}"'.format(word) for word in self._password_tuple]))
    
    del self._password_tuple

    indent=2
    remove_tests=configuration.get_remove_tests()
    remove_combinations=configuration.get_remove_combinations()
    not_duplicated=invert_bool(configuration.get_duplicated_strings())
    not_next_to_next=invert_bool(configuration.get_next_to_next_strings())
    
    if configuration.get_add_spaces():
        JOIN_char=' '
    else:
        JOIN_char=''

    if remove_tests:
        #source+='''        remove_tests=re.compile("|".join(map(re.escape, self._remove_tests_tuple)))\n'''
        source+='''{}\n'''.format(TAB*indent)
        source+='''{0}remove_tests=({1})\n'''.format(TAB*indent,','.join(['"{}"'.format(word) for word in self._remove_tests_tuple]))
        source+='''{}del self._remove_tests_tuple\n'''.format(TAB*indent)
        source+='''{}\n'''.format(TAB*indent)

    if remove_combinations:
        source+='''{}\n'''.format(TAB*indent)
        source+='''{}remove_combinations=self._remove_combinations_re\n'''.format(TAB*indent, self._remove_combinations_re)
        source+='''{}del self._remove_combinations_re\n'''.format(TAB*indent)
        source+='''{}\n'''.format(TAB*indent)

    source+='''{}write_file=open("{}", encoding='utf-8', mode='at')\n'''.format(TAB*indent, self._write_path)

    if not DEBUG:
        source+='''{}threading.Thread(target=self.MSG_update_stats).start()\n'''.format(TAB*indent)
        source+='''{}\n'''.format(TAB*indent)

    if starting_word == None:
        loops_number+=1
        start_word=''
    else:
        start_word=starting_word
        

    for i in range(loops_number):

        if not_next_to_next and i > 0:
            
            code_string=REMOVE_NEXT_TO_NEXT.format(tab=TAB*indent, lnb=loops_number, inb=i+1, inb1=i-1, inb2=i-2)
            if i==1:
                code_string=code_string.replace('word-1','"{0}"'.format(start_word))
                
            source+=code_string

        if not_duplicated and i > 0:
            source+='''{}\n'''.format(TAB*indent)
            source+='''{0}current_word_list{1}=("{3}",word0{2})'''.format(TAB*indent, i-1,  ''.join([',word{0}'.format(k) for k in range(1, i)]), start_word)
            source+=REMOVE_DUPLICATED.format(tab=TAB*indent, lnb=loops_number, inb=i+1, level=i-1)

        if  i > 0 or i == loops_number-1:

            source+='''{}\n'''.format(TAB*indent)
            
            if i == 1:
                if start_word=='':
                    source+='''{}test_word0=word0\n'''.format(TAB*indent)
                else:
                    source+='''{}test_word0="{}"+word0\n'''.format(TAB*indent, start_word)
            else:
                source+='''{}test_word{}=test_word{}+word{}\n'''.format(TAB*indent, i-1, i-2, i-1)

        if remove_combinations and i > 0:
            source+=REMOVE_COMBINATIONS.format(tab=TAB*indent, lnb=loops_number, inb=i+1, level=i-1)
        
        if i < loops_number-1:
            
            # For the moment the enumb function is not really necessary, but in the future it could be nice to skipp stages
            #
            #if not not_duplicated and not not_next_to_next and not remove_combinations and not remove_tests:
            source+='''{0}for word{1} in word_list:\n'''.format((TAB*indent),i)
            #else:
            #    source+='''{tab}for numb{nb}, word{nb} in enumerate(word_list):\n'''.format(tab=TAB*indent, nb=i)
                
            indent+=1
             
    
    if remove_tests > 0:
        source+=REMOVE_TESTS.format(tab=TAB*indent, level=i-1)

    source+='''{}if write_wordlist_count < write_wordlist_buffer_size:\n'''.format(TAB*indent)
    indent+=1
    source+='''{}write_wordlist_count+=1\n'''.format(TAB*indent)
    source+='''{}write_wordlist_buffer.append(test_word{})\n'''.format(TAB*indent, loops_number-2)
    indent-=1
    source+='''{}else:\n'''.format(TAB*indent)
    indent+=1
    source+='''{0}write_file.write('\\n'.join(_word for _word in write_wordlist_buffer))\n'''.format(TAB*indent,'{0}')
    source+='''{}write_wordlist_count=0\n'''.format(TAB*indent)
    source+='''{}write_wordlist_buffer[:] = []\n'''.format(TAB*indent)
    source+='''{}\n'''.format(TAB*indent)
    indent-=1
    source+='''{}self._count+=1\n'''.format(TAB*indent)
    source+='''{}\n'''.format(TAB*indent)
    
    if DEBUG:
        ############################### D E B U G ############################################
            
        source+='''{}print(self._count, test_word)\n'''.format(TAB*indent)
        source+='''{}print(self._count)\n'''.format(TAB*2)
        source+='''{}write_file.close()\n'''.format(TAB*2)
        source+='''{}self.delete_file_if_empty()\n'''.format(TAB*2)
        ####################################################################################
    else:

        #source+='''{0}if os.path.exists("{1}"):\n'''.format(TAB*indent, PATHS.stop_loop_file)
        #indent+=1
        #source+='''{}write_file.close()\n'''.format(TAB*indent)
        #source+='''{}self.delete_file_if_empty()\n'''.format(TAB*indent)
        #source+='''{}self.MSG_end_loop()\n'''.format(TAB*indent)
        #source+='''{}return\n'''.format(TAB*indent)
        #indent-=1
        
        indent=2
        source+='''{}if len(write_wordlist_buffer) > 0:\n'''.format(TAB*indent)
        indent+=1
        source+='''{0}write_file.write('\\n'.join(_word for _word in write_wordlist_buffer))\n'''.format(TAB*indent)
        source+='''{}del write_wordlist_buffer[:]\n'''.format(TAB*indent)
        source+='''{}del write_wordlist_count\n'''.format(TAB*indent)
        
        indent-=1
        source+='''{}\n'''.format(TAB*indent)
        source+='''{}write_file.close()\n'''.format(TAB*indent)
        source+='''{}self.delete_file_if_empty()\n'''.format(TAB*indent)
        source+='''{}self.MSG_end_loop()\n'''.format(TAB*indent)
        source+='''{}\n'''.format(TAB*indent)

    source+='''    except Exception as e:\n'''
    source+='''        self.write_errors(traceback.format_exc())'''

    with open (self._write_path+".py", encoding='utf-8', mode='wt') as f:
        f.write(source)

    bytecode = compile(source, '<string>', 'exec', )
    locals = {}
    eval(bytecode, globals(), locals)
    return locals['__bruteforce_attack_template__']


class Loop(object):
    
    @W_try_or_log
    def __init__(self,  combinations_number, stage, substage, listname, configuration,
                        starting_word, password_tuple, remove_combinations_re, remove_tests_tuple,
                        tui_password, port, DEBUG=False):
        
 
        # socket variables
        self._port=port
        self._tui_password=tui_password
        
        #self.write_errors('Port:{}, CombNumb:{} stage:{}, substage:{}, tui_password:{}'.format(self._port, combinations_number, stage, substage, tui_password))

        """
            This block was removed to avoid an overload at the initialization when all the loops are generated
        """
        try:
            ping=self.SEND_MSG(200)
        except Exception as e:
            self.write_errors("Problem when doing the ping on loops..\n"+str(traceback.format_exc()))
        
        if  ping or DEBUG:
            Queue.append(self)
        else:
            Queue.append(False)
            return None
        
            
        # statistics variables
        self._stage=stage
        self._substage=substage
        self._count=0
        self._thread=True
        
        # incremental variables
        self._listname=listname
        self._password_tuple=password_tuple
        self._combinations_number=combinations_number        
        self._starting_word=starting_word
        
        self._loop_ended=False # used to avoid sending multiple 100 code messages
        
        """
            Initialization of the buteforce_attac method
        """
        if self._starting_word==None:
            self._write_path=PATHS.output_subfolder.format(combinations_number)
        else:
            parent_dir=PATHS.output_subfolder.format(combinations_number)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            self._write_path='{0}/{1}'.format(parent_dir, self._substage+1)

        if configuration.get_remove_combinations():
            self._remove_combinations_re=remove_combinations_re

        if configuration.get_remove_tests():
            """
             This block of the code removes impossible tests of the _remove_tests_tuple.
             
              It will remove words that:
                - Do not start with the startin_word
                - Exced the maximum number of characters, based in the combinations number and the longuest password string

                To do:
                    (#100) remove words that are too small

            """
            max_word_length=len(max(password_tuple, key=len))
            
            if self._starting_word == None:
                starting_word_length=max_word_length
            else:
                starting_word_length=len(self._starting_word)
                
            max_word_length=max_word_length*self._combinations_number
            
            if configuration.get_add_spaces():
                max_word_length+=self._combinations_number-1
            
            
            self._remove_tests_tuple=[]
            for item in remove_tests_tuple:
                if len(item) <= max_word_length and (self._starting_word==None or item[:starting_word_length] == self._starting_word):
                    self._remove_tests_tuple.append(item)
                    
                    
            self._remove_tests_tuple=tuple(self._remove_tests_tuple)
            
            #self.write_errors(str(self._remove_tests_tuple))
            #self._remove_tests_tuple=re.compile("|".join(map(re.escape, self._remove_tests_tuple)))
            #self.write_errors(str(self._remove_tests_tuple))

        """
            Creation of the buteforce_attac method and add it to the class
        """
        function = create_buteforce_attack(self, combinations_number, self._starting_word, configuration, DEBUG)
        self.bruteforce_attack = function.__get__(self, type(self))


    def SEND_MSG(self, code, stage='00000', substage='00000', count='0000000000'):
        #
        # Format the message to 23 bytes (code, must be a 3 substages)
        #
        stage=str(stage)
        substage=str(substage)
        count=str(count)
        
        while len(stage) < 5:
            stage='0'+stage

        while len(substage) < 5:
            substage='0'+substage
            
        while len(count) < 10:
            count='0'+count
            
        bytes_data=bytes('{}:{}:{}:{}:{}'.format(code, stage, substage, count, self._tui_password), 'utf-8')
        
        #self.write_errors('Loop sending MSG: {}'.format(bytes_data.decode('utf-8')))
        
        #
        # make the connection and send the message
        #
        try:
            clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsocket.settimeout(1)
            clientsocket.connect(('localhost', self._port))
            clientsocket.send(bytes_data)
            clientsocket.close()
        except:
            pass
                
        return True

    @W_try_or_log
    def MSG_update_stats(self):
        _stage=self._stage
        _substage=self._substage
        
        #self.write_errors('LOOP THEAD STARTED')

        while self._thread:
            time.sleep(.9)
            #self.write_errors('Loop status: stage:{}, substage:{}, count:{}'.format(_stage, _substage, self._count))
            self.SEND_MSG(150, _stage, _substage, self._count)
            #self.write_errors('loop message SENT')


        #self.write_errors('LOOP THEAD ENDED')


    def MSG_end_loop(self, next=True):
        self._thread=False
        
        # this is to be sure that all the stats went sent before exing the loop
        try:
            self.SEND_MSG(150, self._stage, self._substage, self._count)
        except:
            self.write_errors("Problem ending loop stats:\n"+str(traceback.format_exc()))
        
        if next and not self._loop_ended:
            try:
                self.SEND_MSG(100)
                self._loop_ended=True
            except Exception as e:
                self.write_errors("Problem ending loop:\n"+str(traceback.format_exc()))

    def delete_file_if_empty(self):
        if os.stat(self._write_path)[6]==0:
            os.remove(self._write_path)
            
            
    def write_errors(self, error):
        with open(PATHS.debug_file, encoding='utf-8', mode='at') as f:
            f.write(DEBUG_LOOPS_TEMPLATE.format(    datetime.now(),
                                                    self._starting_word, 
                                                    self._stage,
                                                    self._substage,
                                                    self._count,
                                                    error,
                                                    ))    
        


if __name__ == '__main__':
    """
        This part is only for testing !!
    """
    from itertools import product as iProduct
    from copy import deepcopy
    import re
    
    from Configuration import SimpleConfiguration


    WRITE_LOOP=True

    config=SimpleConfiguration(     duplicated_string=True,
                                    next_to_next_strings=True,
                                    remove_combinations=False,
                                    remove_tests=False,
                                    add_spaces=False)

    loop=Loop(   combinations_number=4, 
                    stage=0,
                    substage=0,
                    listname='testing',
                    configuration=config,
                    starting_word='AA',
                    password_tuple=('th','is','c','prg','ram','f'), 
                    remove_combinations_re=re.compile('|'.join(map(re.escape, ('cis','cprg')))), 
                    remove_tests_tuple=('abcd','abdc','acbd','acdb','adbc','adcb'),
                    tui_password=None,
                    port=6000,
                    DEBUG=False)

    loop.bruteforce_attack()
    


