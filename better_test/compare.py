import core

def diff_json(test_1, test_2, path=""):
    diffs = []

    keys_a = set(test_1.keys())
    keys_b = set(test_2.keys())

    for key in keys_a - keys_b:
        diffs.append({"type": "removed", "path": f"{path}.{key}".lstrip("."), "value": test_1[key]})

    for key in keys_b - keys_a:
        diffs.append({"type": "added", "path": f"{path}.{key}".lstrip("."), "value": test_2[key]})

    for key in keys_a & keys_b:
        val_a = test_1[key]
        val_b = test_2[key]
        current_path = f"{path}.{key}".lstrip(".")

        if isinstance(val_a, dict) and isinstance(val_b, dict):
            diffs.extend(diff_json(val_a, val_b, path=current_path))
        elif val_a != val_b:
            diffs.append({"type": "changed", "path": current_path, "old_value": val_a, "new_value": val_b})
            json 
    return diffs



if __name__ == "__main__":

    def sum2int(int1, int2):
        int3 = int1 + int2
        return int3 

    json1 = core.bettertest(sum2int, inputs=(20, 20), output=40, display=False)
    json2 = core.bettertest(sum2int, inputs=(30, 10), output=40, display=False)

    diffs = diff_json(json1, json2)

    from pprint import pprint
    pprint(diffs)
