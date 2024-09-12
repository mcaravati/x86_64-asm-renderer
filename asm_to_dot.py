import sys
from typing import List

GRAPH_HEADER="""digraph G {
rankdir="TB"

node [shape=box, style=filled, fillcolor=lightgray];
graph [splines=ortho, nodesep=1]
"""

GRAPH_FOOTER="""}
"""

input_file = sys.argv[1]

data=[]
with open(input_file, "r") as f:
    lines = f.readlines()
    for line in lines:      
        data.append(line.split())

def find_address(address: str) -> int:
    """
    This function is used to find the index of a given address in a list of instructions.

    Args:
    address (str): The address to be searched.

    Returns:
    int: The index of the address in the instructions if found, -1 otherwise.

    Raises:
    ValueError: If the address is not found in the instructions.

    """
    for index, row in enumerate(data):  # Start the search from the first index
        if address in row[0]:  # Check if the address is in the first column of the row
            return index  # Return the index if the address is found

    return -1  # Return -1 if the address is not found

# Find chunk beginning
chunk_cursors=[]
jumps = []
for index, line in enumerate(data):

    # Jump, end of chunk
    if line[1][0] == "j":
        jump_to = find_address(line[2].replace("0x", ""))
        chunk_cursors.append(jump_to)
        chunk_cursors.append(index + 1)

        color = "black"
        # Conditional jump
        if line[1] != "jmp":
            color = "green"
            jumps.append((index, index + 1, "red"))

        jumps.append((index, jump_to, color))

# Avoid putting conditional + unconditional jumps at the same time
for cursor in chunk_cursors:
    if data[cursor - 1][1] not in ["ret", "jmp"]:
        # Avoid duplicates
        present = False
        for jump in jumps:
            if jump[0] == cursor - 1 and jump[1] == cursor:
                present = True

        if not present:
            jumps.append((cursor - 1, cursor, "black"))

# Remove duplicates
jumps = list(set(jumps))
chunk_cursors = list(dict.fromkeys(chunk_cursors))
chunk_cursors.sort()
chunks_str = []

def find_chunk(line_index: int) -> int:
    """
    Finds the chunk index for a given line index.

    Parameters:
    line_index (int): The index of the line to find the chunk for.

    Returns:
    int: The index of the chunk that contains the given line.
    """
    # Iterate over the chunk cursors with their indices
    for index, cursor in enumerate(chunk_cursors):
        # Check if the cursor is greater than the line index
        if cursor > line_index:
            # Return the index of the chunk
            return index

    # If no chunk is found, return the length of the chunk cursors
    return len(chunk_cursors)

def render_chunk(lines: List[str]) -> str:
    chunk_str = f"n{len(chunks_str)} [label=<<TABLE BORDER=\"0\">"

    for line in lines:
        chunk_str += "<TR>"

        for index, bit in enumerate(line[1:]):
            if index == 0:
                chunk_str += f"<TD ALIGN=\"LEFT\">{bit.upper()}</TD>"
            else:
                chunk_str += f"<TD ALIGN=\"LEFT\">{bit}</TD>"

        chunk_str += "</TR>"
    
    chunk_str += "</TABLE>>];\n"

    return chunk_str

# Render found chunks
chunk_start = 0
for index, cursor in enumerate(chunk_cursors):
    lines = data[chunk_start:cursor]
    chunks_str.append(render_chunk(lines))
    
    chunk_start = cursor

# Look for ret at the end of the listing
ret_position = 0
for index, line in enumerate(data[chunk_start:]):
    if line[1] == "ret":
        ret_position = chunk_start + index

        lines = data[chunk_start:ret_position + 1]
        chunks_str.append(render_chunk(lines))

# Render jumps
jumps_str = []
for jump in jumps:
    jumps_str.append(
        f"n{find_chunk(jump[0])} -> n{find_chunk(jump[1])} [color={jump[2]}];"
    )

print(GRAPH_HEADER + '\n'.join(chunks_str) + '\n'.join(jumps_str) + GRAPH_FOOTER)