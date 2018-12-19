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
      
          :FOR  ${counter}  IN RANGE    1    5      # custom block indent
            #   a comment in the loop
                \    Log   It's ${counter}
      :FOR  ${value}    IN    @{itterable}      # two loops with no lines b/n them
      \    Run Keywords        Log     The value is ${value}
             ...         AND   Log     2nd keyword
      Log   this is a line just after the loop, no lines b/n it and the FOR block
      
      :FOR  ${animal}  IN  cat  dog
      \    Log ${animal}
           # there is an empty line before the next in-block line
           # e.g. a "broken-up" block
      
      \    Log  2nd keyword
      \    Log  3rd keyword
      
      ${answer}=        Evaluate  42
, will be transformed to:

      No Operation
      FOR  ${animal}  IN  cat  dog
           Log ${animal}
           Log  2nd keyword
      END
      
      Log    Outside the loop
      
          FOR  ${counter}  IN RANGE    1    5      # custom block indent
            #   a comment in the loop
                     Log   It's ${counter}
          END
      FOR  ${value}    IN    @{itterable}      # two loops with no lines b/n them
           Run Keywords        Log     The value is ${value}
             ...         AND   Log     2nd keyword
      END
      Log   this is a line just after the loop, no lines b/n it and the FOR block
      
      FOR  ${animal}  IN  cat  dog
           Log ${animal}
           # there is an empty line before the next in-block line
           # e.g. a "broken-up" block
      
           Log  2nd keyword
           Log  3rd keyword
      END
      
      ${answer}=        Evaluate  42

The script will rewrite *only* the files where it detects a for loop, printing on the console the outcome for each analyzed file:

    INFO: suites/file_x.robot was modified.
    INFO: suites/file_y.robot was not modified.

### Other
A line that is after a `:FOR` and doesn't start with `\`, `...` or `#` (or is not an empty line) is considered outside of the loop block, and this is the place where the `END` is added to close the loop.

The script prints to the console a warning for all lines that start with `\`, but are not in a for block.   
A possible reason for that to happen is because of a bug in the script ?\\\_(?)_/? - so watch its output, and correct such issues manually:

    WARN: 	suites/file_x.robot:7 has an orphaned "\" 
    INFO: suites/file_x.robot was modified.
