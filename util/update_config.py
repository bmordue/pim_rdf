

import os

def update_config_pim():
    """
    Updates the config-pim.ttl file with the correct list of TTL files.
    """
    # Get the absolute path of the current directory
    current_dir = '/home/ben/Projects/pim_rdf'

    # Find all .ttl files, excluding config-pim.ttl
    ttl_files = []
    for root, _, files in os.walk(current_dir):
        for file in files:
            if file.endswith(".ttl") and file != "config-pim.ttl":
                ttl_files.append(os.path.join(root, file))

    # Sort the files for consistency
    ttl_files.sort()

    # Construct the new content string
    new_content_lines = ["          <file:{}>".format(f) for f in ttl_files]
    new_content = " ,\n".join(new_content_lines)

    # Read the original config-pim.ttl file
    config_file_path = os.path.join(current_dir, "config-pim.ttl")
    with open(config_file_path, "r") as f:
        original_content = f.read()

    # Find the start and end of the file list
    start_marker = "ja:externalContent"
    end_marker = "]"

    start_index = original_content.find(start_marker)
    if start_index == -1:
        print("Error: Could not find the start marker in config-pim.ttl")
        return

    start_of_list = start_index + len(start_marker)
    end_of_list = original_content.find(end_marker, start_of_list)
    if end_of_list == -1:
        print("Error: Could not find the end marker in config-pim.ttl")
        return

    # Construct the new config file content
    new_config_content = (
        original_content[:start_of_list]
        + "\n"
        + new_content
        + "\n        "
        + original_content[end_of_list:]
    )

    # Write the updated content back to the file
    with open(config_file_path, "w") as f:
        f.write(new_config_content)

    print("config-pim.ttl has been updated successfully.")

if __name__ == "__main__":
    update_config_pim()

