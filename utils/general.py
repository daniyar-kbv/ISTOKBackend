def is_digits(str):
    for char in str:
        if not ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'].__contains__(char):
            return False
    return True
