#!/usr/bin/env python3
"""JSON Merge Patch - Apply RFC 7396 merge patches to JSON documents."""
import sys, json, copy

def merge_patch(target, patch):
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    if not isinstance(target, dict):
        target = {}
    result = copy.deepcopy(target)
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = merge_patch(result.get(key, {}), value)
    return result

def diff(original, modified):
    if not isinstance(original, dict) or not isinstance(modified, dict):
        return copy.deepcopy(modified) if original != modified else {}
    patch = {}
    for key in set(list(original.keys()) + list(modified.keys())):
        if key not in modified:
            patch[key] = None
        elif key not in original:
            patch[key] = copy.deepcopy(modified[key])
        elif original[key] != modified[key]:
            if isinstance(original[key], dict) and isinstance(modified[key], dict):
                sub = diff(original[key], modified[key])
                if sub: patch[key] = sub
            else:
                patch[key] = copy.deepcopy(modified[key])
    return patch

def main():
    if len(sys.argv) >= 3:
        with open(sys.argv[1]) as f: target = json.load(f)
        with open(sys.argv[2]) as f: patch = json.load(f)
        print(json.dumps(merge_patch(target, patch), indent=2))
    else:
        original = {"title": "Hello", "author": {"name": "Alice"}, "tags": ["a", "b"], "draft": True}
        patch = {"title": "Goodbye", "author": {"name": "Bob", "email": "bob@test.com"}, "tags": ["c"], "draft": None}
        print("=== JSON Merge Patch (RFC 7396) ===\n")
        print(f"Original: {json.dumps(original)}")
        print(f"Patch:    {json.dumps(patch)}")
        result = merge_patch(original, patch)
        print(f"Result:   {json.dumps(result)}")
        print(f"\nReverse diff:")
        rev = diff(result, original)
        print(f"  {json.dumps(rev)}")

if __name__ == "__main__":
    main()
