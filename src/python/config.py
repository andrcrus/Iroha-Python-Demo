import re

# !!!! ONLY LOWER CASE !!!! bug in iroha.
sawmill_names = ["lenlessrubpro", "lesorubka", "pokales", "isengard"]

woods = ["birch", "oak", "pine", "maple"]


def to_lower_case_only_letters(string):
    string = string.lower()
    string = re.sub(r'[^a-z]', '', string)
    return string
