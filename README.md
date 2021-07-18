# WGen

WGen (2018) is based in 7zRecover (2014-2016). This project was uploaded as a backup. Saddly I do not remember its status, but it is probably unstable and with the need of alot of coding. 

## So what is WgGen?

It is a Text Graphical software that allows the dynamic generation of words and their use with external commands.

[Screenshoot to be added]

## How this software is different than others?

* It allows to highly customize the words generation.
* For boosting the performance,there are many intesting concepts in the structure of the software:
    * The generation is splitted in chunks and executed in multi-processing tasks.
    * The code for generating the words dynamically generated. WGen generates the minimal for your need and it executes it.
* It allows to display in realtime the progress of the execution thanks to a web socket based communication with the multiprocessing tasks.


## Manual

```
WGen(8)                                             System Manager's Manual                                            WGen(8)

NAME
        pgen - A tool for generating word lists.

DESCRIPTION
        pgen  -  A  tool  for generating word lists. It loads a list of words or strings, and then the incremental mode starts
       generating the combinations. The objective of this program is to allow the user configure "smart" combinations.

       While the program is generating the words, it will display some statistics such as the number of possible combinations,
       the average of combinations/second, and the estimated amount of time.

       Usage: To launch the program, it is only needed to enter "pgen" over a terminal.

       Using the TUI:
              On  vertical  menus use the Up/Down arrows and over horizontal menus Left/Right arrows to move. The enter key is
              used to validate, and the backspace key to return.

       Lists: The lists of words or strings that the program requests must be a file where each string or word is in a differ‐
              ent  line.  (Any  space  in  the beginning or the end of each line will be removed). When the program asks for a
              list, if the list is in the working directory it is possible to only input the name. An example of a list is  in
              the folder make-a-test, placed at /usr/share/doc/pgen

IMPORTANT REMARKS
       +  When using the program if any error happens it will be logged under a file called "7zR-DEBUG", created over the cur‐
       rent directory.

       + When entering paths, hashes or something requested by the TUI, it must be in a single line.

       + The new socket communication system does not allow (for the moment) to send the password back once it has been found.
       The  password  will be written in a file called "7zR-PASSWORD" over your current directory (it is safe to do not delete
       this file when performing multiple attempts).

       + The program will always read and write in utf-8 encoding. Do not use any other encoding. When launching the  program,
       if your system is not in utf-8 the program will display a warning message.

       + When writing lists/passwords tests the files will appear as "empty" until the loop finish or be killed.

       + It is possible that when cracking files if the password contains a double quote " string it may fail, and I ignore if
       it is possible to escape.

OPTIONS
       Max number of process:
              This will configure the maximum number of process used by the program. There is no limit set by the program.  To
              check  the  limit of your computer  i  recommend  to increase the number of process until reaching 90-95% of the
              CPU's capacity. Once you've reached 100% normally there is no interest to increase the number of process because
              it won't make you win any more time.

       Start length:
              This option sets the start length of the combinations produced by the program. The minimum is 2, and if you wish
              to test single words you should use the "Test 1string" option.

       Final length:
              This options sets the final length of the combinations produced by the program. There is no limit set, just take
              in  mind  that if the number of combinations is too big you may make the program crash or make your computer run
              out of memory.

       Add spaces:
              This option will add spaces betwen combinations. A combination will look like "firstword secondword thirdword.."

       Duplicated strings:
              If Duplicated strings is set to "False", it won't test any combination with more than 1 duplicated  string  from
              the list of words. This option overwrites the Next to Next Strings option.

       Remove tests:
              This  option  you  will ask you for a remove-tests list. This list must contain the exact strings that you don't
              want to test. When a string that you don't want to test matches with a combination, the string is  removed  from
              the virtual list in order to gain speed.
              Since  the  program  do  not  has  a "save my advancement" option, the best that you can do is to use the option
              "write tests" and merge its files to a single file and use this option. This is not the most efficient,  but  it
              works fast enough.

       Remove combinations:
              When this option is active, you will be asked for a remove_combinations file. This file must contain all the il‐
              logical strings that you consider unnecessary to test.

              This option makes  to  win an INCREDIBLE amount of time. When you are dealing with a big number of possible com‐
              binations,  this   option  is  crucial  to succeed. For  some  languages  this  option is easy to implement.  In
              Spanish  for example, there are no words containing “zw” , “xy” , “ñb”, “kq”

              For example, If the password list contains "c,a,r,o,z,w"  (separated by lines not by comas) and the  remove com‐
              binations  list contains "zw, wz" (separated by lines not by comas), The incremental mode will automatically re‐
              ject all the combinations containing “zw”, “wz”.

       Next to next strings:
              You can configure if you want duplicated strings next to next or not. This makes  faster  the  password  search.
              Most  of  passwords containing words do not have repeated letters. If your language has some words with repeated
              letters you can add the string to the password list.
              For example, if the password list contains "c,a,r,o"  (separated by lines not by  comas)  And  NtNS  is  set  to
              "False", words like "carro" won't be tested.

              It  is possible to set NtNS to "False", and add 'rr' to the password list. For example if the password list con‐
              tains "c,a,r,rr,o"  (separated by lines not by comas) and NtNS  is  set  to'No",  words  like  "carro"  will  be
              tested.( But will also make combinations with 'rrr' )

              You must be careful with this mode, because some combinations of words could be refused. For example, 'todayyes'
              would be refused if 'yy' is not in the password list.

              If NtNS is set to "yes", all the strings will be tested, but you will loose time checking  strings  like  'aaab‐
              bcc'.

       Write tests:
              This  option  will  write  the combinations that are being tested in a folder over the current directory. If the
              folder already exists in the current directory it will be removed without asking!

       Write Lists:
              This option will write the lists used by the program. It can be useful if you cleaned a list  and  you  want  to
              compare  or  save  the  changes.  The  lists  will not be overwritten but instead generated with the name "<old‐
              name>-new".

       Clean lists:
              Normal: It removes duplicated words or strings.

              Advanced: Normal mode + it removes strings containing other strings.

              None: It adds all the words  or  strings  without checking for duplicates. It is only recommended  to  use  this
              mode if a Normal or an Advanced mode have already been used.

       Sort lists:
              This  option is useful when there are Test or Combinations to remove because it synchronizes the lists. The time
              that takes to python to search for a string is reduced. This option also removes all the un-useful tests. It  is
              recommended to make a backup of the lists before using this option.

       TUI Messages

       + Combining X strings, Stage X of X
              "Combining X strings" displays the current word length that is being generated.

              "Stage X of X." displays the current stage of the word length.

              Both messages are always sent by the process that it is at the top of the scanning.

              For  example:  The word list contains a,b,c,d; Start length=2; Final length=4; number of process=2; and the mes‐
              sage displayed is "+ Combining 3 strings, Stage 2 of 4". We can deduce then that:
                      + There is one process scanning combinations of three strings starting with the letter b.
                      + Since there are two process, the other process is checking a three words  combinations  starting  with
                     the letter a.
                      + All the combinations of two words have been tested.

       + Average of X/s
              The  average  of  words per second that are being iterated by the program. When options like removing duplicated
              strings are activated, the words are generated but not tested. The python generation it is really fast, and  you
              can test it by running in mode "Empty Run".

       + Estimating XXXXX to finish.
              This  statistic should be recalculated almost every second. If the seconds number of the statistic decrease like
              a normal seconds counter the estimated time should be a pretty good approach.

       The end of this line will contain dots (. , .., ...) in order to display that the TUI stats are not frozen.

Written by Rafael Senties Martinelli 04-06-2015, 02-01-2018                                                            WGen(8)

```



