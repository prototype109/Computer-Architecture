import sys

if len(sys.argv) < 2:
    print('you might have forgotten to include the file name')
    sys.exit()

command_list = []

try:
    with open(sys.argv[1]) as file:
        for line in file:
            split_line = line.split('#')
            first_value = split_line[0]

            if first_value == '':
                continue

            if first_value[0] == '1' or first_value[0] == '0':
                num = first_value[:8]
                command_list.append(int(num, 2))

except FileNotFoundError:
    print(f'{sys.argv[0]}: {sys.argv[1]} file not found')