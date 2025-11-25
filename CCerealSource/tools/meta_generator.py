import re
import sys
import os
import glob

OUTPUT_SOURCE_FILE = "../meta_data/metaData.c"
OUTPUT_HEADER_FILE = "../meta_data/metaData.h"

TypeDictionary = {
    "int": "INT",
    "float": "FLOAT",
    "char": "STRING",
    "bool": "BOOL",
    "long": "LONG",
    "double": "DOUBLE"
}


def parse_enums(file_content):
    found_enums = set()
    enum_pattern = r"(?:typedef\s+)?enum\s*(?P<tag>\w+)?\s*\{(?P<body>.*?)\}\s*(?P<name>\w+)?;"

    matches = re.finditer(enum_pattern, file_content, re.DOTALL)

    for match in matches:
        name = match.group("name")
        if not name:
            name = match.group("tag")

        if name:
            found_enums.add(name)

    return found_enums


def parse_structs(file_content):
    parsed_structs = []

    struct_pattern = r"(?:typedef\s+)?struct\s+SERIALIZABLE(?:\s+(?P<tag>\w+))?\s*{(?P<body>.*?)\s*}\s*(?P<name>\w+)?;"
    field_pattern = re.compile(r"\s*(?P<type>[\w\s]+?)\s+(?P<ptr>\*)?(?P<field_name>\w+)(?P<array>\[.*?\])?\s*;",
                               re.VERBOSE)

    matches = re.finditer(struct_pattern, file_content, re.DOTALL)

    for match in matches:
        struct_name = match.group("name")
        if not struct_name:
            struct_name = match.group("tag")
        if not struct_name:
            continue

        body = match.group("body")
        fields = []

        for field_match in field_pattern.finditer(body):
            f_type = field_match.group("type").strip()
            f_name = field_match.group("field_name")

            clean_type = f_type.replace("struct", "").replace("enum", "").replace("const", "").strip()

            fields.append({
                "type": f_type,
                "clean_type": clean_type,
                "name": f_name
            })

        parsed_structs.append({"name": struct_name, "fields": fields})

    return parsed_structs


def generate_output_files(all_structs, known_enums, include_files, source_path, header_path):
    os.makedirs(os.path.dirname(header_path), exist_ok=True)
    with open(header_path, "w") as header_file:
        header_file.write("#pragma once\n")
        header_file.write('#include "serializer.h"\n\n')

        for struct in all_structs:
            header_file.write(f"extern StructScheme {struct['name']}Scheme;\n")

    os.makedirs(os.path.dirname(source_path), exist_ok=True)
    with open(source_path, "w") as source_file:
        header_filename = os.path.basename(header_path)

        source_file.write(f'#include "{header_filename}"\n')
        source_file.write("#include <stddef.h>\n")

        for inc in include_files:
            clean_inc = inc.replace("\\", "/")
            source_file.write(f'#include "{clean_inc}"\n')
        source_file.write("\n")

        for struct in all_structs:
            writeFieldInfoArray(source_file, struct["name"], struct["fields"], known_enums)
            source_file.write("\n")

        for struct in all_structs:
            writeStructScheme(source_file, struct["name"], len(struct["fields"]))
            source_file.write("\n")


def writeFieldInfoArray(file, struct_name, fields, known_enums):
    file.write(f"FieldInfo {struct_name}Fields[] = {{\n")

    for i, field in enumerate(fields):
        clean_type = field["clean_type"]
        c_name = field["name"]

        if clean_type in TypeDictionary:
            meta_type = TypeDictionary[clean_type]
            child_scheme = "NULL"
        elif clean_type in known_enums:
            meta_type = "ENUM"
            child_scheme = "NULL"
        else:
            meta_type = "STRUCT"
            child_scheme = f"&{clean_type}Scheme"

        comma = "," if i < len(fields) - 1 else ""

        file.write(
            f"    {{ "
            f".name = \"{c_name}\", "
            f".offset = offsetof({struct_name}, {c_name}), "
            f".type = {meta_type}, "
            f".childScheme = {child_scheme} "
            f"}}{comma}\n"
        )
    file.write("};\n")


def writeStructScheme(file, struct_name, field_count):
    file.write(
        f"StructScheme {struct_name}Scheme = {{ "
        f".name = \"{struct_name}\", "
        f".fieldCount = {field_count}, "
        f".fields = {struct_name}Fields, "
        f".size = sizeof({struct_name}) "
        f"}};\n"
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python meta_generator.py <file1> [file2] ... [fileN]")
        return

    input_files = []

    path_prefix = "../../"

    for arg in sys.argv[1:]:
        prefixed_arg = path_prefix + arg

        expanded = glob.glob(prefixed_arg)

        if expanded:
            input_files.extend(expanded)
        else:
            input_files.append(prefixed_arg)

    input_files = list(dict.fromkeys(input_files))

    all_parsed_structs = []
    processed_files = []
    known_enums = set()

    print(f"Scanning {len(input_files)} file(s)...")

    for input_path in input_files:
        try:
            with open(input_path, "r") as file:
                content = file.read()
                enums = parse_enums(content)
                known_enums.update(enums)
        except Exception:
            pass

    for input_path in input_files:
        try:
            with open(input_path, "r") as file:
                content = file.read()

            structs = parse_structs(content)
            if structs:
                print(f"  -> Found {len(structs)} struct(s) in {input_path}")
                all_parsed_structs.extend(structs)
                processed_files.append(input_path)

        except FileNotFoundError:
            print(f"Error: Could not find input file: {input_path}")
        except Exception as e:
            print(f"Error reading {input_path}: {e}")

    if not all_parsed_structs:
        print("No structs found. Exiting.")
        return

    generate_output_files(all_parsed_structs, known_enums, processed_files, OUTPUT_SOURCE_FILE, OUTPUT_HEADER_FILE)


if __name__ == "__main__":
    main()
