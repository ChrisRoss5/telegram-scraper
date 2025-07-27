def insert_after_key(d, target_key, new_key, new_value):
    new_dict = {}
    for key, value in d.items():
        new_dict[key] = value
        if key == target_key:
            new_dict[new_key] = new_value
    return new_dict


# Example usage
original = {"a": 1, "b": 2, "c": 3}
modified = insert_after_key(original, "b", "x", 42)

print(modified)
# Output: {'a': 1, 'b': 2, 'x': 42, 'c': 3}
