REM This file gives an example of how to use the autotune.py script located
REM in <svn-autotune-root>/library/autotune. 
REM You will need to make sure that the "library" directory exists on your
REM PYTHONPATH variable (in Windows, at least). 
REM You will also need to modify the location to match your own <svn-autotune-root>.

REM To see all of the available options, you just need to run with the -h option:
REM python autotune.py -h

python autotune.py --schedule myschedule.csv --popsize 8 --maxevals 16 myidf.idf myparams.csv myuserdata.csv myweather.epw 