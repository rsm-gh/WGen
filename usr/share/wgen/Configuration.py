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



from CCParser import CCParser
from Paths import *; paths=Paths()

class Configuration(object):
    """
        This is the real class used to manage the configuration of the program
    """
    
    def __init__(self):
        self._ccp=CCParser(paths.configuration,'7zrecover_configuration')
        self._password_length_end=3             

        self.set_password_length_start(self._ccp.get_int_defval('StartPassLenght', 2))
        self.set_password_length_end(self._ccp.get_int_defval('PasswordLenght', 3))
        self.set_number_of_process(self._ccp.get_int_defval('MaximumNumberOfProcess', 1))
        
        self._ccp.set_default_bool(True)
        #
        self._next_to_next_strings=self._ccp.get_bool('NextToNextStrings')
        self._test_1string=self._ccp.get_bool('TestOneString')
        
        
        self._ccp.set_default_bool(False)
        #
        self._clear_tests=self._ccp.get_bool('ClearTests')
        self._write_lists=self._ccp.get_bool('WriteLists')
        self._remove_tests=self._ccp.get_bool('RemoveTests')
        self._write_tests=self._ccp.get_bool('WriteTests')
        self._remove_combinations=self._ccp.get_bool('RemoveCombinations')
        self._remove_duplicated_strings=self._ccp.get_bool('RemoveDuplicatedStrings')
        self._sort_lists=self._ccp.get_bool('SortLists')
        self._empty_run=self._ccp.get_bool('EmptyRun')
        self._add_spaces=self._ccp.get_bool('AddSpaces')
        self.set_clean_lists(self._ccp.get_str('CleanLists'))
        self._filetype=self._ccp.get_str('FileType')

    def set_number_of_process(self, integer):
        if integer > 0:
            self._number_of_process=integer
            self._ccp.write('MaximumNumberOfProcess',str(integer))
        else:
            self._number_of_process=1
            
    def set_password_length_start(self, integer):
        if integer > 1:
            
            self._password_length_start=integer
            self._ccp.write('StartPassLenght',str(integer))
            
            if integer > self._password_length_end:
                self._password_length_end=integer
                self._ccp.write('PasswordLenght',str(integer))
        else:
            self._password_length_start=2
            
    def set_password_length_end(self, integer):
        if integer > 1:
            self._password_length_end=integer
            self._ccp.write('PasswordLenght',str(integer))
                    
            if integer < self._password_length_start:
                self._password_length_start=integer
                self._ccp.write('StartPassLenght',str(integer))
        else:
            self._password_length_end=3
                
    def change_clear_tests(self):
        if self._clear_tests:
            self._clear_tests=False
        else:
            self._clear_tests=True
        self._ccp.write('ClearTests', self._clear_tests)
        
    def change_next_to_next_strings(self):
        if self._next_to_next_strings:
            self._next_to_next_strings=False
        else:
            self._next_to_next_strings=True
        self._ccp.write('NextToNextStrings',self._next_to_next_strings)
        
    def change_remove_tests(self):
        if self._remove_tests:
            self._remove_tests=False
        else:
            self._remove_tests=True
        self._ccp.write('RemoveTests', self._remove_tests)

    def change_write_lists(self):
        if self._write_lists:
            self._write_lists=False
        else:
            self._write_lists=True
        self._ccp.write('WriteLists', self._write_lists)   
        
    def change_sort_lists(self):
        if self._sort_lists:
            self._sort_lists=False
        else:
            self._sort_lists=True
        self._ccp.write('SortLists', self._sort_lists)     
        
    def change_remove_combinations(self):
        if self._remove_combinations:
            self._remove_combinations=False
        else:
            self._remove_combinations=True
        self._ccp.write('RemoveCombinations', str(self._remove_combinations))   
        
    def change_remove_duplicated_strings(self):
        if self._remove_duplicated_strings:
            self._remove_duplicated_strings=False
        else:
            self._remove_duplicated_strings=True
        self._ccp.write('RemoveDuplicatedStrings', str(self._remove_duplicated_strings))    
    
    def change_write_combinations(self):
        if self._write_combinations:
            self._write_combinations=False
        else:
            self._write_combinations=True
        self._ccp.write('WriteCombinations', str(self._write_combinations))  
       
    def change_test_1string(self):
        if self._test_1string:
            self._test_1string=False
        else:
            self._test_1string=True
        self._ccp.write('TestOneString', self._test_1string)
 
    def change_add_spaces(self):
        if self._add_spaces:
            self._add_spaces=False
        else:
            self._add_spaces=True
        self._ccp.write('AddSpaces', self._add_spaces)
        
    def set_clean_lists(self, state):
        if state=='advanced':
            self._clean_lists='advanced'
        elif state=='none':
            self._clean_lists='none'
        else:
            self._clean_lists='normal'
        self._ccp.write('CleanLists', self._clean_lists)   

    def increment_clean_lists(self):
        if self._clean_lists=='none':
            self._clean_lists='normal'
        elif self._clean_lists=='normal':
            self._clean_lists='advanced'
        elif self._clean_lists=='advanced':
            self._clean_lists='none'
        self._ccp.write('CleanLists', self._clean_lists)
            
    def decrement_clean_lists(self):
        if self._clean_lists=='advanced':
            self._clean_lists='normal'
        elif self._clean_lists=='normal':
            self._clean_lists='none'
        elif self._clean_lists=='none':
            self._clean_lists='advanced'    
        self._ccp.write('CleanLists', self._clean_lists)   

    def increment_password_length_start(self):
        self.set_password_length_start(self._password_length_start+1)
        
    def decrement_password_length_start(self):
        self.set_password_length_start(self._password_length_start-1)
        
    def increment_password_length_end(self):
        self.set_password_length_end(self._password_length_end+1)
        
    def decrement_password_length_end(self):
        self.set_password_length_end(self._password_length_end-1)
    
    def increment_number_of_process(self):
        self.set_number_of_process(self._number_of_process+1)
    
    def decrement_number_of_process(self):
        self.set_number_of_process(self._number_of_process-1)

    def get_clear_tests(self):
        return self._clear_tests
        
    def get_next_to_next_strings(self):
        return self._next_to_next_strings
        
    def get_remove_tests(self):
        return self._remove_tests
        
    def get_write_lists(self):
        return self._write_lists
        
    def get_sort_lists(self):
        return self._sort_lists
        
    def get_remove_combinations(self):
        return self._remove_combinations
        
    def get_duplicated_strings(self):
        return self._remove_duplicated_strings
        
    def get_password_length_start(self):
        return self._password_length_start
        
    def get_password_length_end(self):
        return self._password_length_end
        
    def get_number_of_process(self):
        return self._number_of_process
        
    def get_clean_lists(self):
        return self._clean_lists

    def get_test_1string(self):
        return self._test_1string

    def get_add_spaces(self):
        return self._add_spaces



class SimpleConfiguration(object):
    """
        This class is only used to test the Loops class without using the TUI or
        saving any data.
    """
    
    
    def __init__(self, duplicated_string, next_to_next_strings, remove_combinations, remove_tests, add_spaces):
    
        self._duplicated_string=duplicated_string
        self._next_to_next_strings=next_to_next_strings
        self._remove_tests=remove_tests
        self._add_spaces=add_spaces
        self._remove_combinations=remove_combinations
        
    
    def print_info(self):
        print('--- Configuration ---')
        print('Write Tests\t', self._write_tests)
        print('Duplicated\t', self._duplicated_string)
        print('Nex to Next\t', self._next_to_next_strings)
        print('Remove Tests\t', self._remove_tests)
        print('Empty Run\t', self._empty_run)
        print('Remove Combs\t', self._remove_combinations)
        print()
    
    def get_duplicated_strings(self):
        return self._duplicated_string
        
    def get_next_to_next_strings(self):
        return self._next_to_next_strings
        
    def get_remove_tests(self):
        return self._remove_tests
        
    def get_add_spaces(self):
        return self._add_spaces
        
    def get_remove_combinations(self):
        return self._remove_combinations


if __name__ == '__main__':
    Configuration=Configuration()
