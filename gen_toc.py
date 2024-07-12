import os


def generate_table_of_contents(directory):
    toc = []
    for root, dirs, files in os.walk(directory):
        # ignore dot-folders
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        files.sort()

        for file in files:
            if not file.endswith(".md"):
                continue

            filepath = os.path.relpath(os.path.join(root, file), directory)

            # get titles
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()[2:]

            depth = filepath.count(os.path.sep)
            indent = '  ' * depth
            
            # construct entry
            toc.append(f"{indent}- [{first_line}]({filepath})")

    return "\n".join(toc)


if __name__ == "__main__":
    table_of_contents = generate_table_of_contents('docs')
    print(table_of_contents)
