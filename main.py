from pathlib import Path
import xml.etree.ElementTree as ET
import json
import re

def clean_text(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    return s

def find_entries(root):
    entries = root.find("CheatEntries")
    if entries is None:
        return root.findall(".//CheatEntry")
    return entries.findall(".//CheatEntry")

def parse_ct(ct_path: Path):
    tree = ET.parse(ct_path)
    root = tree.getroot()
    entries = find_entries(root)
    result = []
    for e in entries:
        desc = clean_text(e.findtext("Description", "")) or clean_text(e.findtext("Name", "")) or clean_text(e.findtext("text", ""))
        vtype = clean_text(e.findtext("VariableType", ""))
        addr = clean_text(e.findtext("Address", ""))
        result.append({"title": desc, "VariableType": vtype, "Address": addr})
    return result

def write_json(data, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    structured = [{"title": d["title"], "details": {"VariableType": d["VariableType"], "Address": d["Address"]}} for d in data]
    out_path.write_text(json.dumps(structured, indent=2, ensure_ascii=False), encoding="utf-8")

def write_txt(data, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for d in data:
        lines.append(d["title"])
        lines.append(f"  VariableType: {d['VariableType']}")
        lines.append(f"  Address: {d['Address']}")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")

# Generator

TYPE_MAP = {
    "Float": ("read_float", 4),
    "Double": ("read_double", 8),
    "4 Bytes": ("read_int", 4),
    "4Bytes": ("read_int", 4),
    "Dword": ("read_int", 4),
    "Byte": ("read_uchar", 1),
    "1 Byte": ("read_uchar", 1),
    "2 Bytes": ("read_short", 2),
    "Short": ("read_short", 2),
    "Signed 4 Bytes": ("read_int", 4),
    "String": ("read_string", None),
}

def parse_module_plus_offset(addr: str):
    import re
    m = re.match(r'^\s*([^\s\+]+)\s*\+\s*([0-9a-fA-Fx]+)\s*$', addr)
    if not m:
        return None
    module = m.group(1)
    off_str = m.group(2)
    try:
        offset = int(off_str, 0)
    except ValueError:
        offset = int(off_str, 16)
    return module, offset

def address_is_number(addr: str):
    try:
        int(addr, 0)
        return True
    except Exception:
        return False

def pymem_read_block(title: str, var_type: str, address: str):
    parsed = parse_module_plus_offset(address)
    method, size = TYPE_MAP.get(var_type, (None, 4))
    lines = []
    lines.append(f"    # {title} ({var_type})")
    if parsed:
        module, offset = parsed
        lines.append(f"    mod = module_from_name(pm.process_handle, r'{module}')")
        lines.append(f"    addr = mod.lpBaseOfDll + {hex(offset)}")
    elif address_is_number(address):
        addr_int = int(address, 0)
        lines.append(f"    addr = {hex(addr_int)}")
    else:
        lines.append(f"    addr = {repr(address)}  # unknown format, adjust manually")
    if method == "read_string":
        lines.append("    value = pm.read_string(addr, 256)")
    elif method:
        lines.append(f"    value = pm.{method}(addr)")
    else:
        lines.append(f"    value = pm.read_bytes(addr, {size})")
    lines.append(f"    values[{repr(title)}] = value")
    lines.append("")
    return "\n".join(lines)

def write_pymem(data, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# Generated file")
    lines.append("import time")
    lines.append("from pymem import Pymem")
    lines.append("from pymem.process import module_from_name")
    lines.append("")
    lines.append("def connect():")
    lines.append("    process_name = input('Enter process name (game.exe): ').strip()")
    lines.append("    if not process_name:")
    lines.append("        raise RuntimeError('Process name required')")
    lines.append("    return Pymem(process_name)")
    lines.append("")
    lines.append("def read_all(pm):")
    lines.append("    values = {}")
    for d in data:
        block = pymem_read_block(d['title'], d['VariableType'], d['Address'])
        lines.append(block)
    lines.append("    return values")
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    pm = connect()")
    lines.append("    while True:")
    lines.append("        vals = read_all(pm)")
    lines.append("        for k, v in vals.items():")
    lines.append("            print(f\"{k}: {v}\")")
    lines.append("        time.sleep(0.25)")
    out_path.write_text("\n".join(lines), encoding="utf-8")

#main

def main():
    in_path = Path(input("Enter input .ct file path: ").strip('" '))
    if not in_path.exists():
        print("Input file not found.")
        return
    out_path = Path(input("Enter output file path: ").strip('" '))
    fmt = input("Output format (json/txt/pymem): ").strip().lower()
    data = parse_ct(in_path)
    if fmt == "json":
        write_json(data, out_path)
        print(f"Wrote {len(data)} entries to {out_path} (JSON)")
    elif fmt == "txt":
        write_txt(data, out_path)
        print(f"Wrote {len(data)} entries to {out_path} (TXT)")
    elif fmt == "pymem":
        if out_path.suffix.lower() != ".py":
            out_path = out_path.with_suffix(".py")
        write_pymem(data, out_path)
        print(f"Wrote continuous Pymem reader to {out_path} ({len(data)} entries)")
    else:
        print("Invalid format. Choose json, txt, or pymem.")

if __name__ == "__main__":
    main()
