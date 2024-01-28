def remove_duplicates(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        unique_lines = set(file.readlines())

    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(unique_lines)

remove_duplicates('./sample.txt', './output.txt')