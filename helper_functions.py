# helper_functions

def convert_string_to_int(string: str, minimum, maximum=None) -> int or str:
    for symbol in string:
        if symbol.isalpha() == True:
            string = string.replace(symbol, "")

    try:
        result = eval(string)
        assert result == int(result)
    except Exception as e:
        print(e)
        return "input is not an integer"

    if minimum != None:
        if result < minimum:
            return f"input must be greater or equal to {minimum}"

    if maximum != None:
        if maximum < result:
            return f"input must be less or equal to {maximum}"

    return int(result)