#!/usr/bin/env python3
"""
transform_rules.py

Usage:
  python transform_rules.py <rules_input_dir> <rules_output_dir>

What it does:
 - Maps Sigma abstract fields (CommandLine, Image, etc.) to ECS macOS ESF fields
 - Lowercases string detection tokens for caseless behavior
 - Writes transformed rules to output dir (preserving filenames)
"""
import sys
import os
import yaml
import copy

# Mapping: Sigma abstract -> ECS field
FIELD_MAP = {
    "CommandLine": "process.command_line",
    "Image": "process.executable",
    "Executable": "process.executable",
    "ProcessId": "process.pid",
    "ParentProcessId": "process.parent.pid",
    "ParentImage": "process.parent.executable",
    "ParentCommandLine": "process.parent.command_line",
    "ProcessName": "process.name",
    "ParentProcessName": "process.parent.name",
    "User": "user.name",
    "UserId": "user.id",
    "Hostname": "host.hostname",
    "HostName": "host.name",
    "FileName": "file.name",
    "FilePath": "file.path",
    "FileExt": "file.extension",
    "FileDirectory": "file.directory",
    "DestinationIp": "destination.ip",
    "DestinationPort": "destination.port",
    "SourceIp": "source.ip",
    "SourcePort": "source.port",
    "Protocol": "network.protocol",
    "EventType": "event.type",
    "EventAction": "event.action"
}

# Fields we want to treat as caseless
CASELESS_FIELDS = {
    "process.command_line",
    "process.executable",
    "process.parent.executable",
    "file.path",
    "file.name",
    "user.name"
}

def map_field_name(key):
    """Map abstract Sigma field to ECS, leave unchanged if already ECS"""
    return FIELD_MAP.get(key, key)

def lower_tokens(value):
    """Lowercase strings or lists recursively for caseless search"""
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, list):
        return [lower_tokens(v) for v in value]
    return value

def transform_detection(detection):
    """Transform a detection block: map fields, lowercase caseless"""
    if not isinstance(detection, dict):
        return detection
    out = {}
    for sel_name, sel_body in detection.items():
        if sel_name.lower() == "condition":
            out[sel_name] = sel_body
            continue
        if isinstance(sel_body, dict):
            new_sel = {}
            for field_key, field_val in sel_body.items():
                # handle operators like |contains|all
                if "|" in field_key:
                    base, suffix = field_key.split("|", 1)
                    mapped_key = map_field_name(base) + "|" + suffix
                else:
                    mapped_key = map_field_name(field_key)
                # lowercase tokens if caseless
                if mapped_key.split(".")[0] in CASELESS_FIELDS:
                    new_sel[mapped_key] = lower_tokens(field_val)
                else:
                    new_sel[mapped_key] = field_val
            out[sel_name] = new_sel
        else:
            out[sel_name] = sel_body
    return out

def transform_rule(doc):
    d = copy.deepcopy(doc)
    if "detection" in d and isinstance(d["detection"], dict):
        d["detection"] = transform_detection(d["detection"])
    return d

def process_file(in_path, out_path):
    with open(in_path, "r", encoding="utf-8") as f:
        docs = list(yaml.safe_load_all(f))
    out_docs = []
    for doc in docs:
        if doc is None:
            continue
        out_docs.append(transform_rule(doc))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump_all(out_docs, f, sort_keys=False)

def main():
    if len(sys.argv) != 3:
        print("Usage: transform_rules.py <rules_input_dir> <rules_output_dir>")
        sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2]
    if not os.path.isdir(src):
        print("Input directory does not exist:", src)
        sys.exit(1)
    os.makedirs(dst, exist_ok=True)
    for root, _, files in os.walk(src):
        for fn in files:
            if not fn.lower().endswith((".yml", ".yaml")):
                continue
            rel = os.path.relpath(root, src)
            in_file = os.path.join(root, fn)
            out_dir = os.path.join(dst, rel)
            out_file = os.path.join(out_dir, fn)
            print("Transforming:", in_file, "->", out_file)
            process_file(in_file, out_file)
    print("Done. Transformed rules written to:", dst)

if __name__ == "__main__":
    main()
