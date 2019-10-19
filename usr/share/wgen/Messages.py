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


TEXT_LICENSE_AND_CHOICE=''' This program is free software, it is distributed
 in  the hope that it will be useful, but WITHOUT 
 ANY  WARRANTY. Look at the  GNU  General  Public 
 License 3 for more details.'''

TEXT_HEADER='''WGen - utf8 wordlist generator.
Copyright (C) 2014-2016, 2018 Rafael Senties Martinelli.


-------------------------------------------------
'''

TEXT_ASK_FOR_PASS_LIST=''' If you  put  the  main input list that you want
 to  use  under the terminal working  directory, 
 and   you  rename it "wgen-main",  you  wont be 
 asked for it.

 Please enter the path to the main input list:
 '''

TEXT_ASK_FOR_RMCOMB_LIST=''' If you put the remove-combinations list that you
 want to use in  the terminal working  directory, 
 and  you  rename  it  "wgen-rmcomb", you wont be 
 asked for it.

 Path to the remove-combinations list:
 '''

TEXT_ASK_FOR_RMTEST_LIST=''' If you put the remove-tests list that you want to
 use in  the terminal  working  directory, and you
 rename it "wgen-rmtests", you wont be asked for it.

 Path to the remove-tests list:
 ''' 

TEXT_ASK_FOR_FILE_AGAIN=''' The path that you added don't exist,
 or is not a file. \n\n\n Try again:'''
 
TEXT_THE_FILE_WAS_EMPTY=''' The {0} is empty. \n\n\n\n Please chose another file:''' 

TEXT_FINISH="""All the lists went generated or
 the process was stopped.."""
 
TEXT_TERMINAL_TOO_SMALL='''Your screen terminal is too small,
the minimal screen size is
51x17 (width*height)'''

TEXT_PYCORE_PROBLEM=''' 
 It seems that one of the loops could not connect to the socket 
 server. To avoid displaying incomplete results the incremental
 mode will exit.
\n If after restarting  the  program  the problem persists report 
 the bug if you want support.
'''

ENCODING='''
 It seems that your default system's encoding is "{}" instead 
 of "utf-8".
 
 Normally the program performance and messages should not have any 
 problem     BUT YOU MUST     careful of giving utf-8 files to the 
 program, and reading files in utf-8.
 
 Do you still want to launch the program (y/n)? '''

TEXT_THE_STATISTICS_WILL_APPEAR='''The statistics will appear as soon as possible.'''

TEXT_INCREMENTAL_IS_BEING_INITIALIZED='''The incremental mode is being initialized..'''

TEXT_THE_FILE_IS_NOT_VALID='''The file is not valid.'''

BUTTON_RETURN="[Backspace to Return]"
BUTTON_START="[Start]"
BUTTON_CONFIGURE="[Configure]"
BUTTON_EXIT="[Exit]"
BUTTON_PRESS_BACKSPACE_TO_STOP="[Press Backspace to stop]"
BUTTON__WRITE_RETURN_TO_GO_THE_MENU='[Write "return" to go the Menu]'
BUTTON_PRESS_ANY_KEY_TO_RETURN_TO_THE_MENU="[Press any key to return to the Menu]"
BUTTON_YES_REMOVE_IT="[yes, remove it]"
BUTTON_NO_RETURN_TO_THE_MENU="[no, return to the menu]"

TEXT_GENERATING_WITH='''Generating lists with the file "{}"'''
TEXT_POSSIBLE_COMBINATIONS="{} possible combinations."

TEXT_TESTING_ONE_WORD_STRING='''Checking all the words of the password list..'''
TEXT_THE_LIST_IS_BEING_CHECKED='''The list "{}" is being checked,'''
TEXT_THE_LIST_IS_BEING_IMPORTED='''The list "{}" is being imported.'''
TEXT_THE_LIST_IS_BEING_SORTED='''The list "{}" is being sorted,'''

TEXT_CONFIGURATION_PAGE="Configuration Menu"
TEXT_START_LENGTH="Start length:"
TEXT_FINAL_LENGTH="Final length:"
TEXT_MAX_NUM_OF_PROC="Max number of process:"
TEXT_NEXT_TO_NEXT_STRINGS="Next to next strings:"
TEXT_REMOVE_COMBINATIONS="Remove combinations:"
TEXT_DUPLICATED_STRINGS="Duplicated strings:"
TEXT_SORT_LISTS="Sort lists:"
TEXT_WRITE_LISTS="Write lists:"
TEXT_REMOVE_TESTS="Remove tests:"
TEXT_CLEAN_LISTS="Clean lists:"
TEXT_CLEAN_TESTS="Clear tests:"
TEXT_ADD_SPACES="Add spaces:"

TEXT_COMBINING_AND_STAGE="• Combining {} strings, Stage {} of {}."
TEXT_TOTAL_DONE="• {} generated, {}% done."
TEXT_AVERAGE_OF="• Average of {}/s."
TEXT_ESTIMATING_X_TO_FINISH="• Estimating {} to finish."
