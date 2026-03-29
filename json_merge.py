#!/usr/bin/env python3
"""Deep JSON merge with conflict resolution strategies."""

def deep_merge(base, override, strategy="override"):
    if not isinstance(base, dict) or not isinstance(override, dict):
        if strategy == "override": return override
        if strategy == "keep": return base
        if strategy == "error": raise ValueError(f"Conflict: {base} vs {override}")
        return override
    result = dict(base)
    for key, val in override.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(val, dict):
                result[key] = deep_merge(result[key], val, strategy)
            elif isinstance(result[key], list) and isinstance(val, list):
                if strategy == "append":
                    result[key] = result[key] + val
                elif strategy == "unique":
                    combined = result[key] + [v for v in val if v not in result[key]]
                    result[key] = combined
                else:
                    result[key] = val
            else:
                if strategy == "keep":
                    pass
                elif strategy == "error":
                    raise ValueError(f"Conflict at key '{key}': {result[key]} vs {val}")
                else:
                    result[key] = val
        else:
            result[key] = val
    return result

def flatten(obj, prefix="", sep="."):
    result = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{prefix}{sep}{k}" if prefix else k
            result.update(flatten(v, new_key, sep))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{prefix}{sep}{i}" if prefix else str(i)
            result.update(flatten(v, new_key, sep))
    else:
        result[prefix] = obj
    return result

def unflatten(flat, sep="."):
    result = {}
    for key, val in flat.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = val
    return result

if __name__ == "__main__":
    a = {"name": "base", "config": {"debug": True, "port": 8080}}
    b = {"config": {"debug": False, "host": "0.0.0.0"}}
    import json
    print(json.dumps(deep_merge(a, b), indent=2))

def test():
    a = {"x": 1, "nested": {"a": 1, "b": 2}, "list": [1, 2]}
    b = {"x": 2, "nested": {"b": 3, "c": 4}, "list": [3]}
    # Override (default)
    r = deep_merge(a, b)
    assert r["x"] == 2 and r["nested"] == {"a": 1, "b": 3, "c": 4} and r["list"] == [3]
    # Keep
    r2 = deep_merge(a, b, strategy="keep")
    assert r2["x"] == 1 and r2["nested"]["b"] == 2
    # Append lists
    r3 = deep_merge(a, b, strategy="append")
    assert r3["list"] == [1, 2, 3]
    # Flatten
    f = flatten({"a": {"b": 1}, "c": [10, 20]})
    assert f["a.b"] == 1 and f["c.0"] == 10
    # Unflatten
    u = unflatten({"a.b": 1, "a.c": 2})
    assert u == {"a": {"b": 1, "c": 2}}
    print("  json_merge: ALL TESTS PASSED")
