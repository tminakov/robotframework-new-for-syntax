#!/usr/bin/env python3
import sys
import os
import glob


def format_file(name):
    file_changed = False
    in_block = False

    with open(name, mode='r', newline='') as file:
        modified_lines = []
        line_ending = None
        in_block = False

        for line in file:
            if line_ending is None:
                line_ending = '\r\n' if '\r\n' in line else '\n'    # no special treatment for Mac ;)

            stripped = line.lstrip().lower()
            if stripped.startswith(':for'):
                if in_block:    # special handling for two :FOR cycles with no delimiter (lines) b/n them
                    closing_line = ' ' * for_position + 'END' + line_ending
                    modified_lines.append(closing_line)
                    
                for_position = line.find(':')
                line = line[0:for_position] + line[for_position+1:]
                file_changed = True
                in_block = True
                modified_lines.append(line)
                continue

            has_slash = stripped.startswith('\\')

            if in_block:
                if has_slash:
                    pos = line.find('\\')
                    # replace the \ with an whitespace - this will preserve the indentation
                    line = line[:pos] + ' ' + line[pos+1:]
                elif stripped.startswith('...') or stripped.startswith('#'):
                    pass
                else:       # presumably a line not in the current FOR block? close the block
                    in_block = False
                    # add the new closing keyword, as a new line
                    closing_line = ' '*for_position + 'END' + line_ending
                    modified_lines.append(closing_line)
            elif has_slash:
                print(f'WARN: \t{name}:{len(modified_lines) + 1} has an orphaned "\\"')
                
            modified_lines.append(line)

    if file_changed:
        with open(name, mode='w', newline='') as file:
            file.writelines(modified_lines)
    return file_changed


if __name__ == '__main__':
    if len(sys.argv) != 2:
        __, script_name = os.path.split(sys.argv[0])
        print('Pass the target file name as argument; supports glob patterns:')
        print(f'\t{script_name} directory/suite.robot     - modify a single file')
        print(f'\t{script_name} directory/*.robot         - modify all files ending with robot')
        print(f'\t{script_name} directory/**/*.robot      - modify all files ending with robot, in all sub-directories')
        print('The file(s) is modified in-place.')
        exit(0)

    for a_file in glob.glob(sys.argv[1], recursive=True):
        changed = format_file(a_file)
        print(f'INFO: {a_file} was {"not " if not changed else ""}modified.')
