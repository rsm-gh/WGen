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

    > Big improvement:
    
        The socket connection must be improved....
        What about using pyro again, and generate the loops on live so there be no
        connection problem? it would save the problem of "sending back the password"
                            
                            or
                            
        + Implement a communication system to send the password over the 37 bytes command. ?
        + Add the option: "start at"

"""


import os
import sys
import curses
import getpass
import shutil
import psutil
import getpass
import traceback
import socket
import re

from time import time
from multiprocessing import Process, freeze_support
from threading import Thread
from collections import OrderedDict, deque
from datetime import timedelta
from decimal import Decimal
from random import randint
from unicodedata import normalize

# local imports
import Loops
from Messages import *
from Configuration import *
from Paths import *; PATHS=Paths()
from Debug import W_try_or_log, debug

def modify_tupple(_tuple, index, value):
    _list=list(_tuple)
    _list[index]=value
    return tuple(_list)
    
def get_abs_path(path):
    if not os.path.exists(path):
        possible_path='{}/{}'.format(PATHS.current_dir, os.path.basename(path))
        if os.path.exists(possible_path):
            return possible_path
    return path

def format_socket_number(number):
    number = str(number)
    
    while len(number) < 5:
        number='0'+number
        
    return number
    
    
def format_number_for_tui(number):
    """
        Take a number and format it so it can be properly
        seen at the TUI, ex: 1000 -> 1'000
    """
    
    if number > 30:
        number=int(number)
    
    formated_number="{:,}".format(int(number)).replace(',',"'")
    
    if len(formated_number) > 15:
        formated_number="{:.2E}".format(Decimal(number))
    
    return formated_number

def set_with_order(seq):
    #http://stackoverflow.com/a/480227/3672754
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

class Index:
    """
        This class is used to manage the text displayed
        at the TUI menus.
    """
    
    def __init__(self, max_val, current=0, min_val=0, step=6):
        self._min=min_val
        self._max=max_val
        self._current=current
        self.change_step(step)
        self._range_min=min_val
        self._range_max=self._range_min+self._step

    def change_step(self, value):
        if value > self._max+1:
            self._step=self._max+1
        elif value >= 4:
            self._step=value
        
    def get_current(self):
        return self._current
    
    def increment(self):
        self._current+=1
        if self._current > self._max:
            self._current=self._min
        return self._current
    
    def decrement(self):
        self._current-=1
        if self._current < self._min:
            self._current=self._max
        return self._current
    
    def get_range(self):
        if self._current > self._range_max-1:
            while self._current > self._range_max-1:
                self._range_max += 1
            self._range_min=self._range_max-self._step  
        elif self._current < self._range_min:
            while self._current < self._range_min:  
                self._range_min -= 1
                
            self._range_max=self._range_min+self._step
            
        return self._range_min, self._range_max
        
        
class AverageQueue:
    """
        This class is used to easily calculate the average of tests per second.
    """
    def __init__(self, queue_size=30):
        
        self._queue=deque(maxlen=queue_size)        
        self._queue_size=queue_size
        self._current_val=0
        self._queue.append((0, time()))
        
    def update_from_total(self, total):
        self._queue.append((total-self._current_val, time()))
        self._current_val=total
        
    def get_average(self):
        return round(sum(val[0] for val in self._queue)/(self._queue[-1][1] - self._queue[0][1]), 1)
    
    def debug_data(self):
        return '''
queue_size = {}
current_val = {}
get_average() = {}
queue =
{}
'''.format(self._queue_size, self._current_val, self.get_average(), '\n'.join(str(item) for item in self._queue))
    

class Main:
    
    def __init__(self):

        self.TUI=curses.initscr()
        
        (y,x)=self.TUI.getmaxyx()
        if y < 17 or x < 51:
            print(TEXT_TERMINAL_TOO_SMALL)
            self.exit_main()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
        
        self.configuration=Configuration()

        self.main_menu_dict=OrderedDict([
    (BUTTON_START,      (0, 3,  3,  'INCREMENTAL_mode')),
    (BUTTON_CONFIGURE,  (1, 2,  12, 'SCAN_configure')),
    (BUTTON_EXIT,       (2, 2,  25, 'exit_main'))
                                            ])
            
        self.menu_configure_dict=OrderedDict([
    (TEXT_MAX_NUM_OF_PROC,      ('get_number_of_process',       'decrement_number_of_process',      'increment_number_of_process')),
    (TEXT_START_LENGTH,         ('get_password_length_start',   'decrement_password_length_start',  'increment_password_length_start')),
    (TEXT_FINAL_LENGTH,         ('get_password_length_end',     'decrement_password_length_end',    'increment_password_length_end')),
    (TEXT_ADD_SPACES,           ('get_add_spaces',              'change_add_spaces',                'change_add_spaces')),
    (TEXT_DUPLICATED_STRINGS,   ('get_duplicated_strings',      'change_remove_duplicated_strings', 'change_remove_duplicated_strings')),
    (TEXT_NEXT_TO_NEXT_STRINGS, ('get_next_to_next_strings',    'change_next_to_next_strings',      'change_next_to_next_strings')),
    (TEXT_REMOVE_COMBINATIONS,  ('get_remove_combinations',     'change_remove_combinations',       'change_remove_combinations')),
    (TEXT_REMOVE_TESTS,         ('get_remove_tests',            'change_remove_tests',              'change_remove_tests')),
    (TEXT_WRITE_LISTS,          ('get_write_lists',             'change_write_lists',               'change_write_lists')),
    (TEXT_CLEAN_LISTS,          ('get_clean_lists',             'decrement_clean_lists',            'increment_clean_lists')),
    (TEXT_SORT_LISTS,           ('get_sort_lists',              'change_sort_lists',                'change_sort_lists')),
        ])
        
        self.menu_configure_index=Index(len(self.menu_configure_dict)-1)
        
        
        default_command=0
        self.header_text=TEXT_HEADER
 

    """
        TUI methods & extras
    """
    @W_try_or_log
    def INCREMENTAL_mode(self):
        
        Loops.Queue=[]
        self.incremental_is_working=True
        self.file_name=None
        self.count_dict={}
        self.process_ended=0
        self.max_id=(0,0)
        self.password=None
        self.advancement_queque=[]
        self.graphical_dots=''
        self.average_queue=AverageQueue()

        
        # the program will increment the port in case it be already used
        port=6434
        
        # the password may be good idea for preventing the TUI having inputs
        # from other process
        self.tui_password=randint(100000000,999999999)
        
        number_of_process = self.configuration.get_number_of_process()
        
        if os.path.exists(PATHS.stop_loop_file):
            os.remove(PATHS.stop_loop_file)

        """
            Get the paths that will be used to generate the lists
        """

        passwords_path=self.ASK_for_listpath('wgen-main')
        if not passwords_path:
            return
        self.list_name=os.path.basename(passwords_path)
        if len(self.list_name) > 9:
            self.list_name=self.list_name[:7]+'..'

        self.cracking_text=TEXT_GENERATING_WITH.format(self.list_name)
                
        
        if self.configuration.get_remove_tests(): 
            rmtests_path=self.ASK_for_listpath('wgen-rmtests')
            if rmtests_path==False:
                return 
        else:
            rmtests_path=None
            remove_tests_tuple=None

        if self.configuration.get_remove_combinations():
            rmcombs_path=self.ASK_for_listpath('wgen-rmcomb')        
            if rmcombs_path==False:
                return
        else:
            rmcombs_path=None
            remove_combinations_re=None
            
            
        """
            Add the binding to cancel the incremental mode by using backspace
        """
        quit_thread=Thread(target=self.THREAD_quit_on_scanning)
        quit_thread.start()
        
        
        """
            Create the lists for the brute force attack
        """
            
        self.passwords_tuple,self.number_of_words = self.CREATE_words(passwords_path, 'passwords', 'tuple')    
    
        if rmtests_path != None:
            remove_tests_tuple, number_of_rmtst = self.CREATE_words(rmtests_path,'remove_tests', 'tuple')
            if not remove_tests_tuple:
                return
                
        if rmcombs_path != None:
            remove_combinations_re, number_of_rmcomb = self.CREATE_words(rmcombs_path,'remove_combinations', 're')
            if not remove_combinations_re:
                return

        if not self.incremental_is_working:
            return

        """
            Calculate the total_of_combinations
        """
        self.total_of_combinations=0
        for i in range(self.configuration.get_password_length_start(), self.configuration.get_password_length_end()+1):
            self.total_of_combinations+=self.number_of_words**i

        self.combinations_text=TEXT_POSSIBLE_COMBINATIONS.format(format_number_for_tui(self.total_of_combinations))

        self.UPDATE_cracking_header()
        self.TUI.insstr(9, 2, TEXT_INCREMENTAL_IS_BEING_INITIALIZED, curses.color_pair(2))
        self.TUI.refresh()

        try:
            if os.path.exists(PATHS.output_folder):
                shutil.rmtree(PATHS.output_folder)
            os.makedirs(PATHS.output_folder)
        except Exception as e:
            debug(traceback.format_exc())

        """
            Start the listening socket, and increment the port if necessary
        """
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.serversocket.bind(('localhost', port))
                break
            except:
                port+=1
        self.serversocket.listen(number_of_process+1) # max number of connections, +1 doesn't hurt
        Thread(target=self.SOCKET_listener).start()
        #debug('7zserver at'+str(port))


        """
            Initialize the Loops
        """
        for stage, combination_number in enumerate( range(self.configuration.get_password_length_start(), 
                                                    self.configuration.get_password_length_end()+1)):
            
            if not self.incremental_is_working:
                return
            
            elif combination_number==2:
                Loops.Loop(  combination_number, stage, 0, self.list_name, self.configuration,
                                None, self.passwords_tuple, remove_combinations_re, remove_tests_tuple,
                                self.tui_password, port
                            )
                            
                            
                self.count_dict['00002:00000']=0
            else:
                for substage, word in enumerate(self.passwords_tuple):
                    Loops.Loop(  combination_number, stage, substage, self.list_name, self.configuration,
                                    word, self.passwords_tuple,remove_combinations_re, remove_tests_tuple,
                                    self.tui_password, port
                                )
                
                    self.count_dict[format_socket_number(stage)+format_socket_number(substage)]=0

        del remove_combinations_re
        del remove_tests_tuple


        """
            Check if all the loops successfully pinged the server
        """
        for loop in Loops.Queue:
            if not loop:
                self.UPDATE_programs_header()
                self.TUI.insstr(6, 2,TEXT_PYCORE_PROBLEM, curses.color_pair(2))
                self.TUI.insstr(15, 2, BUTTON_PRESS_ANY_KEY_TO_RETURN_TO_THE_MENU, curses.color_pair(3)) 
                self.TUI.refresh()
                choice=self.TUI.getch()
                return


        #debug('\nLoops initialization ended.\n')

        self.UPDATE_cracking_header()
        self.TUI.insstr(9, 2,TEXT_THE_STATISTICS_WILL_APPEAR, curses.color_pair(2))
        self.TUI.insstr(15, 2, BUTTON_PRESS_BACKSPACE_TO_STOP, curses.color_pair(3))
        self.TUI.refresh()
            
        self.passwords_tuple=None


        if self.incremental_is_working:
            self.start_time=time()
            for i in range(number_of_process):
                Thread(target=self.INCREMENTAL_start_next_process).start()
            
            while self.incremental_is_working:
                """
                    This part of the code used to be placed at the SOCKET_listener method method.
                    in order to improve the speed of the SOCKET_listener, it is now just appending to a queue,
                    and the processing is done here.
                """ 

                _tui_password=str(self.tui_password)

                for item in self.advancement_queque:
                
                    connection, address, buf = item
                    self.advancement_queque.remove(item)
                    
                    if len(buf) > 0 and self.incremental_is_working:
                        
                        data=buf.decode('utf-8').split(':')
                        #debug('7z received data: {}'.format(data))
                        
                        if data[4] == _tui_password:
                            
                            command=data[0]
                            stage=data[1]
                            substage=data[2]
                            count=data[3]

                            # The commands are organized by "the most called"
                            #
                            if command == '150':
                                """
                                    Increment the count for the stats
                                """
                                self.count_dict[stage+substage]=int(count)
                                
                                stage=int(stage)
                                substage=int(substage)
                                
                                # The TUI is only updated by the TOP process
                                if (stage == self.max_id[0] and substage >= self.max_id[1]) or stage > self.max_id[0]:
                                    
                                    self.UPDATE_incremental_avancement( stage+self.configuration.get_password_length_start(), 
                                                                        substage+1
                                                                        )
                                    self.max_id=(stage, substage)

                           
                            elif command == '100':
                                self.INCREMENTAL_start_next_process()
                            
                            elif command == '666':
                                """
                                    The password was found
                                """
                                self.password=False
                                self.incremental_is_working=False
                                Loops.Queue=[]
                                self.tui_password=None
                                
                            elif command == '200':
                                """
                                    Ping
                                """
                                pass
                            
                            else:
                                debug('Wrong command by: {}, command: {}'.format(address, ':'.join(data)))
                        else:
                            debug('Warning: wrong password by: {}\n data: {}'.format(address[0], ':'.join(data)))
                            #debug('PASSWORD: {}, recived: {}'.format(_tui_password, data[-1:]))
                
                

            
            self.UPDATE_incremental_result()
            
        return
        
    @W_try_or_log
    def THREAD_quit_on_scanning(self):
        """
            Thread to manage the exit of an operation. This method
            scans at the background for the backspace key.
        """
        while self.incremental_is_working:              
            choice=self.TUI.getch()     
            if choice in (curses.KEY_BACKSPACE, 127):
                open(PATHS.stop_loop_file, 'wb').close()
                Loops.Queue=[]
                self.tui_password=None
                self.incremental_is_working=False
                break


    @W_try_or_log
    def CREATE_words(self, file_path, file_type, object_type='list'):
        """
            This method will read an utf-8 text file and perform a series of tests
            in order to create a valid/optimized list/tuple/re of words for the incremental mode.
            
            The object can be "list", "tuple", "re"
            
        """
    
        filter_type=self.configuration.get_clean_lists()
        file_name=os.path.basename(file_path)

        self.UPDATE_programs_header()
        self.TUI.insstr(7, 2,TEXT_THE_LIST_IS_BEING_IMPORTED.format(file_name), curses.color_pair(2))
        self.TUI.refresh()
        

        if filter_type=='none':
            with open(file_path, encoding='utf-8', mode='rt') as f:
                local_word_list=f.read()
                
            local_word_list=[line.strip() for line in normalize('NFC',local_word_list).splitlines()]
            length=len(local_word_list)
            added_words=length
        
        elif filter_type in ['normal','advanced']:
            
            # This is the normal filter, it removes the duplicated strings
            
            with open(file_path, encoding='utf-8', mode='rt') as f:
                lines=f.read()
                
            lines=list(filter(None, set_with_order(line.strip() for line in normalize('NFC',lines).splitlines())))
            length=len(lines)
            
            if filter_type == 'normal':
                local_word_list = lines
                lines=None
                added_words = length
            
            elif filter_type=='advanced':
            
                self.UPDATE_programs_header()
                self.TUI.insstr(7, 2,TEXT_THE_LIST_IS_BEING_CHECKED.format(file_name), curses.color_pair(2))
                self.TUI.insstr(8, 2,"[>                   ] 0%", curses.color_pair(2))
                self.TUI.insstr(15, 2, BUTTON_PRESS_BACKSPACE_TO_STOP, curses.color_pair(3))
                self.TUI.refresh()

                local_word_list=[]
                added_words,old_percent=0,0
                
                try:
                    for word_count, word in enumerate(lines):
                        
                        if not self.incremental_is_working:
                            return False, False
                        
                        else:
                            for local_word in local_word_list:
                                
                                if not self.incremental_is_working:
                                    return False, False
                                
                                elif local_word in word:
                                    alredy=True
                                    break
                                    
                            if not already:
                                local_word_list.append(word)
                                added_words+=1

                        percent=int(round(word_count*100/length))
                        
                        if percent > old_percent:
                            old_percent=percent
                            av_percent=int(round(percent*0.2))
                            avancement=("="*av_percent)+">"+(" "*(20-av_percent))
                            self.UPDATE_programs_header()
                            self.TUI.insstr(7, 2,TEXT_THE_LIST_IS_BEING_CHECKED.format(file_name), curses.color_pair(2))
                            self.TUI.insstr(8, 2,"["+avancement+"] "+str(percent)+"%", curses.color_pair(2))
                            self.TUI.insstr(15, 2, BUTTON_PRESS_BACKSPACE_TO_STOP, curses.color_pair(3))
                            self.TUI.refresh()

                except Exception as e:
                    debug(traceback.format_exc())
                    return False, False
            
        if self.configuration.get_sort_lists():
            self.UPDATE_programs_header()
            self.TUI.insstr(7, 2,TEXT_THE_LIST_IS_BEING_SORTED.format(file_name), curses.color_pair(2))
            self.TUI.insstr(8, 2,"[>                   ] 0%", curses.color_pair(2))
            self.TUI.insstr(15, 2, BUTTON_PRESS_BACKSPACE_TO_STOP, curses.color_pair(3))
            self.TUI.refresh()            

            if file_type=='passwords':
                local_word_list.sort()  
            else:                
                sorted_password_list=sorted(self.passwords_tuple, key=len , reverse=True)
                comb_words_dict={}

                old_percent=0
                for local_word_count, local_word in enumerate(sorted(local_word_list)):
                    
                    if not self.incremental_is_working:
                        return False, False
                    
                    substrings_count=0
                    testing_word=local_word
                    for word in sorted_password_list:
                        
                        if not self.incremental_is_working:
                            return False, False                        
                                
                        elif word in testing_word:
                            occurence=testing_word.count(word)
                            testing_word=testing_word.replace(word,'')
                            substrings_count+=occurence
                            if testing_word == '':
                                break
                                
                    if testing_word !='':
                        substrings_count='x'   # warn the user that it is not a combinations of words?
                    
                    if substrings_count in comb_words_dict:
                        comb_words_dict[substrings_count].append(local_word)
                    else:
                        comb_words_dict[substrings_count]=[local_word]

                    percent=int(round(local_word_count*100/added_words))
                    if percent > old_percent:
                        old_percent=percent
                        av_percent=int(round(percent*0.2))
                        avancement=("="*av_percent)+">"+(" "*(20-av_percent))
                        self.UPDATE_programs_header()
                        self.TUI.insstr(7, 2,TEXT_THE_LIST_IS_BEING_SORTED.format(file_name), curses.color_pair(2))
                        self.TUI.insstr(8, 2,"["+avancement+"] "+str(percent)+"%", curses.color_pair(2))
                        self.TUI.insstr(15, 2, BUTTON_PRESS_BACKSPACE_TO_STOP, curses.color_pair(3))
                        self.TUI.refresh()
                        
                local_word_list=[]
                for key in sorted(comb_words_dict.keys()):
                    
                    if not self.incremental_is_working:
                        return False, False
                        
                    local_word_list+=comb_words_dict[key]

        
        if self.configuration.get_write_lists():
            try:
                with open(file_path+'-new', encoding='utf-8', mode='wt') as f:
                    for word in local_word_list:
                        f.write(word+'\n')
            except Exception as e:
                debug(traceback.format_exc())
                return False, False
        
        if object_type=='re':
            return re.compile('|'.join(map(re.escape, local_word_list))), added_words
            
        elif object_type=='tuple':
            return tuple(local_word_list), added_words
            
        elif object_type == 'list':
            return local_word_list, added_words
        else:
            debug("Wrong object={} request on CREATE_WORDS".format(object_type))
            return False, False

    @W_try_or_log
    def ASK_for_listpath(self, choice):
        """
            choice can be "rmcomb","rmtests" or passwords
        """
    
        if choice=='wgen-rmcomb':
            message=TEXT_ASK_FOR_RMCOMB_LIST
        elif choice=='wgen-rmtests':
            message=TEXT_ASK_FOR_RMTEST_LIST
        elif choice=='wgen-main':
            message=TEXT_ASK_FOR_PASS_LIST  
        else:
            debug('WRONG choice (#200): {}'.format(choice))
            return False
        
        listpath=PATHS.current_dir+'/'+choice
        if not os.path.exists(listpath) or not os.path.isfile(listpath) or os.stat(listpath)[6]==0:
            self.UPDATE_programs_header()
            self.TUI.insstr(6, 0,message,curses.color_pair(2))
            self.TUI.insstr(15, 0,BUTTON__WRITE_RETURN_TO_GO_THE_MENU,curses.color_pair(3))
            self.TUI.refresh()
            self.ALLOW_user_input()
            listpath=self.TUI.getstr(12,1,curses.color_pair(2)).decode('utf-8').strip()
            
            if listpath=='return':
                self.ALLOW_keyboard_movement()
                return False
                    
            while not os.path.exists(listpath) or not os.path.isfile(listpath) or os.stat(listpath)[6]==0:
                self.UPDATE_programs_header()
                self.TUI.insstr(6, 0,TEXT_ASK_FOR_FILE_AGAIN,curses.color_pair(2))
                self.TUI.insstr(15, 0,BUTTON__WRITE_RETURN_TO_GO_THE_MENU,curses.color_pair(3))
                self.TUI.refresh()
                listpath=self.TUI.getstr(12,1,curses.color_pair(2)).decode('utf-8').strip()
                
                if listpath=='return':
                    listpath=False
                    break
        
        self.ALLOW_keyboard_movement()
        return listpath
        
    def UPDATE_main_menu(self):
        """
           Update the display of the main menu
        """          
        
        self.UPDATE_programs_header()
        self.TUI.insstr(6, 0,TEXT_LICENSE_AND_CHOICE,curses.color_pair(2))
        
        for key in self.main_menu_dict.keys():
            _, state, x, _ = self.main_menu_dict[key]
            self.TUI.insstr(15, x,key,curses.color_pair(state))
        self.TUI.refresh()

    def UPDATE_configure_menu(self):
        """
           Update the display of the configuration menu
        """  
        
        #y,x=self.TUI.getmaxyx()   # this was to resize menus when the TUI is resized
        #self.menu_configure_index.change_step(y-12)
        self.UPDATE_programs_header()
        self.TUI.insstr(6, 1, TEXT_CONFIGURATION_PAGE,curses.color_pair(2))
        height=8
        min_val, max_val = self.menu_configure_index.get_range()
        current=self.menu_configure_index.get_current()
        for i in range(min_val, max_val):
            key=list(self.menu_configure_dict.keys())[i]
            method, _, _, = self.menu_configure_dict[key]
            value=str(getattr(getattr(self,'configuration'),method)())
            if i != current:
                state=2
            else:
                state=3
                
            self.TUI.insstr(height, 2,  key,    curses.color_pair(state))
            self.TUI.insstr(height, 26, value,  curses.color_pair(state))
            height+=1
        
        self.TUI.insstr(height+2,1,BUTTON_RETURN,curses.color_pair(2))
        self.TUI.refresh()

    def UPDATE_programs_header(self):
        self.TUI.clear()
        self.TUI.insstr(0, 0, self.header_text)

    def UPDATE_cracking_header(self):      
        self.UPDATE_programs_header()
        self.TUI.insstr(6, 1,self.cracking_text,curses.color_pair(2))
        self.TUI.insstr(7, 2,self.combinations_text,curses.color_pair(2))
        
    def UPDATE_incremental_result(self):
        """
            This method is displayed when the incremental method finishes or it is stopped.
            It displays the result of the cracking attempt.
        """
        
        self.UPDATE_programs_header()
        self.TUI.insstr(6, 1, TEXT_FINISH,curses.color_pair(2))
        self.TUI.insstr(15, 1, BUTTON_RETURN, curses.color_pair(3))
        self.TUI.refresh()
            
        while True:
            choice=self.TUI.getch()
            if choice in (curses.KEY_BACKSPACE, 127):
                return        

    def UPDATE_incremental_avancement(self, string_level, string_stage):
        """
            Update the TUI by displaying the current statistics.
        """
        
        try:
            #debug('string_level: {}, string_stage: {}'.format(string_level, string_stage))

            done=sum(self.count_dict.values())
            self.average_queue.update_from_total(done)
            
            total_of_combinations=self.total_of_combinations
            
            self.UPDATE_cracking_header()
            
            if done <= 0 or total_of_combinations <= 0:
                self.TUI.insstr(9, 2,TEXT_THE_STATISTICS_WILL_APPEAR, curses.color_pair(2))
            else:
                # Calculate the statistics
                #
                left=total_of_combinations-done
                ratio=self.average_queue.get_average()
                
                if ratio < 0:
                    debug("Negative average")
                    debug(self.average_queue.debug_data())
                
                
                global_percent=round((done*100)/total_of_combinations, 1)
                
                
                # Format the statistics
                #
                if ratio < 99:
                    formatted_ratio=str(round(ratio, 2))
                else:
                    formatted_ratio=format_number_for_tui(ratio)
                
                
                if string_level > 2:
                    stages=self.number_of_words
                else:
                    stages=1
                
                if global_percent > 100:
                    time_string="?"
                else:
                    time_string=str(timedelta(seconds=left/ratio))
                    
                    # remove miliseconds
                    if '.' in time_string:
                        time_string=time_string.split('.',1)[0]
                    
                    
                # Send the statistics
                #
                self.TUI.insstr(9, 2,TEXT_TOTAL_DONE.format(format_number_for_tui(done), global_percent), curses.color_pair(2))  
                self.TUI.insstr(10, 2,TEXT_COMBINING_AND_STAGE.format(string_level,string_stage, stages), curses.color_pair(2))
                self.TUI.insstr(11, 2,TEXT_AVERAGE_OF.format(formatted_ratio), curses.color_pair(2))
                self.TUI.insstr(12, 2,TEXT_ESTIMATING_X_TO_FINISH.format(time_string)+self.graphical_dots, curses.color_pair(2))
            
                # Update the advancement dots
                #
                self.graphical_dots+='.'
                if self.graphical_dots=='....':
                    self.graphical_dots=''
            
            self.TUI.insstr(15, 2, BUTTON_PRESS_BACKSPACE_TO_STOP, curses.color_pair(3))
            self.TUI.refresh()
        
        except Exception as e:
            debug(traceback.format_exc())


    def ALLOW_keyboard_movement(self):
        curses.echo(0)
        curses.curs_set(0)
        self.TUI.keypad(1)
        
    def ALLOW_user_input(self):
        curses.echo()
        self.TUI.keypad(1)
        curses.curs_set(1)

    def SCAN_main(self):
        """
            Scan (keyboard movement) the main menu of the TUI
        """
        
        self.ALLOW_keyboard_movement()
                
        choice=''
        over=list(self.main_menu_dict.keys())[0]
        self.UPDATE_main_menu()
        while True:
            choice=self.TUI.getch()
                    
            index, state, _, method = self.main_menu_dict[over]
            if choice==curses.KEY_RIGHT or choice==curses.KEY_LEFT:
                if choice==curses.KEY_RIGHT:
                    if index+1 <= len(self.main_menu_dict)-1:
                        index+=1
                    else:
                        index=0
                elif choice==curses.KEY_LEFT:
                    if index-1 >= 0:
                        index-=1
                    else:
                        index=len(self.main_menu_dict)-1
                self.main_menu_dict[over]=modify_tupple(self.main_menu_dict[over], 1, 2)
                over=list(self.main_menu_dict.keys())[index]
                self.main_menu_dict[over]=modify_tupple(self.main_menu_dict[over], 1, 3)
            elif choice==10:
                getattr(self, method)()
            self.UPDATE_main_menu()

    def SCAN_configure(self):
        """
            Scan (keyboard movement) the configuration menu of the TUI
        """
        
        choice=''
        over=list(self.menu_configure_dict.keys())[self.menu_configure_index.get_current()]
        self.UPDATE_configure_menu()
        
        while True:
            choice=self.TUI.getch()
            if choice in (curses.KEY_BACKSPACE, 127):
                return
            else:
                _, left_method, right_method = self.menu_configure_dict[over]
                if choice==curses.KEY_UP:
                    over=list(self.menu_configure_dict.keys())[self.menu_configure_index.decrement()]
                elif choice==curses.KEY_DOWN:
                    over=list(self.menu_configure_dict.keys())[self.menu_configure_index.increment()]
                elif choice==curses.KEY_RIGHT:
                    getattr(getattr(self,'configuration'),right_method)()
                elif choice==curses.KEY_LEFT:
                    getattr(getattr(self,'configuration'),left_method)()

            self.UPDATE_configure_menu() 

    @W_try_or_log
    def SOCKET_listener(self):
        """
            This is the socket listener. It listens the process messages in order to
            update the stats and TUI. The messages are always 37 bytes in the following format:
            
                code:stage:substage:count:password
            
            * When using commands that doesn't require stage, substage and count, they are replaced
            by zeros.
            
        """

        while self.incremental_is_working:
            connection, address = self.serversocket.accept()
            self.advancement_queque.append((connection, address, connection.recv(37)))
                
        self.serversocket.close()
    
    @W_try_or_log
    def INCREMENTAL_start_next_process(self):
        """
            This method starts the process of the incremental queue.
        """
    
        if len(Loops.Queue) > 0 and self.incremental_is_working:
            loop=Loops.Queue[0]
            Loops.Queue.remove(loop)
            Process(target=loop.bruteforce_attack()).start()

        elif self.incremental_is_working:
            self.process_ended+=1
            if self.process_ended==self.configuration.get_number_of_process():
                self.incremental_is_working=False
                Loops.Queue=[]
                self.tui_password=None



    def exit_main(self):
        """
            Completely exit the program.
        """
        self.incremental_is_working=False
        curses.nocbreak()
        self.TUI.keypad(0)
        curses.echo()
        curses.endwin()
        exit()




if __name__ == '__main__':
    try:
        sys_encoding=sys.getdefaultencoding().lower()
        
        launch=True
        if sys_encoding != 'utf-8':
            answer=input(ENCODING.format(sys_encoding))
            
            if not 'y' in answer.lower():
                launch=False
                
        if launch:
            main=Main()
            main.SCAN_main()
            
    except Exception as e:
        debug(traceback.format_exc())
