# Transform Robot Framework pre-v3.1 for-loops to the new syntax

Robot Framework adds a new syntax for the [for loops](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#for-loops): the starting keyword (`FOR`) is no longer prefixed with a colon, the block isn't marked with slashes - `\`, and it must end with the `END` keyword.

This script can be used to transform source files from the "old style" to the new one.



## Usage

 - Prerequisite - needs python version >= 3.6.
 - The target file(s) is modified **in-place** - so they must be in version control (preferable), or use the script on backup copies.

The script accepts a single argument - the target to be modified; the argument supports file names wildcard; samples:

    change_for_rf.py directory/suite.robot     # modify a single file
    change_for_rf.py directory/*.robot         # modify all files ending with robot
    change_for_rf.py directory/**/*.robot      # modify all files ending with robot, in all sub-directories

## Modifications

A source with this content:
      
      No Operation
      :FOR  ${animal}  IN  cat  dog
      \    Log ${animal}
      \    Log  2nd keyword
      Log    Outside the loop
      :FOR  ${counter}  IN RANGE    1    5
      #   a comment in the loop
      \    Log   It's ${counter}
      :FOR  ${value}    IN    @{itterable}
      \    Run Keywords        Log     The value is ${value}
             ...         AND   Log     2nd keyword
, will be transformed to:

      No Operation
      FOR  ${animal}  IN  cat  dog
           Log ${animal}
           Log  2nd keyword
      END
      Log    Outside the loop
      FOR  ${counter}  IN RANGE    1    5
      #   a comment in the loop
           Log   It's ${counter}
      END
      FOR  ${value}    IN    @{itterable}
           Run Keywords        Log     The value is ${value}
             ...         AND   Log     2nd keyword
      END

The script will rewrite *only* the files where it detects a for loop, printing on the console the outcome for each analyzed file:

    INFO: suites/file_x.robot was modified.
    INFO: suites/file_y.robot was not modified.

### Known Limitations
A line that is after a `:FOR` and doesn't start with `\`, `...` or `#` is considered outside of the loop block, and this is the place where the `END` is added to close the loop.
This means that blocks that have empty lines (or start with any other character but these 3) will be "broken-up" in the middle - and any lines that are originally in the block will now be left out. It's easier to explain with a sample; on this old-style loop:

      :FOR  ${animal}  IN  cat  dog
      \    Log ${animal}
           # there is an empty line before the next in-block line
      
      \    Log  2nd keyword

, the result will be a "broken-up" loop, due to the empty line:

      FOR  ${animal}  IN  cat  dog
           Log ${animal}
           # there is an empty line before the next in-block line
      END
      
      \    Log  2nd keyword

which is obviously an incorrect syntax.  
The script prints to the console a warning for all such lines - so watch its output, and correct the issue manually:

    WARN: 	suites/file_x.robot:7 has an orphaned "\" 
    INFO: suites/file_x.robot was modified.
