#!/usr/bin/env python3
import sys
import os
import glob


def format_file(name):

    def next_lines_in_block(lst):
        """ Returns True if the initial list members are :FOR block members. """
        for _line in lst:
            _line = _line.strip()
            if _line.startswith('\\'):
                return True
            elif _line == '' or _line.startswith('#') or _line.startswith('...'):
                continue
            else:
                return False
        return False

    in_block = False     # True if the currently processed line is a part of an open :FOR block
    for_position = None  # the position of the ":FOR" string in the current line, as it needs to be replaced (with "FOR")
    added_lines = 0      # counter how many lines were added, if == 0 - the file was not modified
    
    with open(name, mode='r', newline='', encoding='utf8') as fp:
        content = fp.readlines()

        # skip empty files
        if not content:
            return False

        line_ending = '\r\n' if '\r\n' in content[0] else '\n'    # no special treatment for Mac ;)

        # Append newline if file doesn't end with \n
        if '\n' not in content[-1]:
            content[-1] += line_ending
            content.append(line_ending)

        for i, line in enumerate(content):
            stripped = line.lstrip().lower()
            if stripped.startswith(':for'):     # start of a new loop block
                if in_block:
                    # special handling for two :FOR cycles with no delimiter (lines) b/n them - add the closing keyword
                    # the previous loop
                    content[i] = ' ' * for_position + 'END' + line_ending + content[i]
                    line = content[i]
                    added_lines += 1

                for_position = line.find(':')
                line = line[0:for_position] + line[for_position + 1:]

                if '\n' in line[:for_position]:
                    # when the previous "if in_block" appended the closing END, it changed the position of
                    # this line's :FOR in the newly generated line - accommodate for that
                    for_position -= line.index('\n') + 1

                content[i] = line
                in_block = True
                continue

            has_slash = stripped.startswith('\\')

            if in_block:
                if has_slash:
                    pos = line.find('\\')
                    # replace the \ with an whitespace - this will preserve the indentation
                    content[i] = line[:pos] + ' ' + line[pos + 1:]
                elif stripped.startswith('...') or stripped.startswith('#') \
                        or next_lines_in_block(content[i:]):
                    pass
                else:       # presumably a line not in the current FOR block? close the block
                    in_block = False
                    # add the new closing keyword, as a new line
                    content[i] = ' ' * for_position + 'END' + line_ending + content[i]
                    added_lines += 1

            elif has_slash:
                print(f'WARN: \t{name}:{i + added_lines + 1} has an orphaned "\\"')

    # the file has been changed only if there's a closing added (the END) - write it to the FS only in this case
    if added_lines > 0:
        with open(name, mode='w', newline='', encoding='utf8') as file:
            file.writelines(content)
    return added_lines > 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        __, script_name = os.path.split(sys.argv[0])
        print('Pass the target file name as argument; supports glob patterns:')
        print(f'\t{script_name} directory/suite.robot       - modify a single file')
        print(f'\t{script_name} \'directory/*.robot\'         - modify all files ending with robot')
        print(f'\t{script_name} \'directory/**/*.robot\'      - modify all files ending with robot, in all sub-directories')
        print('The file(s) is modified in-place.')
        exit(0)

    for a_file in glob.glob(sys.argv[1], recursive=True):
        changed = format_file(a_file)
        print(f'INFO: {a_file} was {"not " if not changed else ""}modified.')
