import json
import re


def extract_json(input_string):
    i_stack = []
    c_stack = []
    for i, c in enumerate(input_string):
        if c == "{" or c == "[":
            if i > 1 and input_string[i - 1] == "\\":
                continue
            else:
                i_stack.append(i)
                c_stack.append(c)
        elif c == "}" or c == "]":
            last_c = c_stack.pop()
            if (last_c == "{" and c =="}") or (last_c == "[" and c == "]"):
                last_i = i_stack.pop()
                if len(i_stack) == 0:
                    return json.loads(input_string[last_i:i+1])
