from epub_converter import EpubConverter
from sys import argv
import json


def save_json_structure(structure: dict, output_file: str) -> None:
    with open(output_file, "w") as file:
        json.dump(structure, file, indent=4)


def main():
    epub_file = argv[1]
    print(f"Converting {epub_file} to JSON structure")
    converter = EpubConverter()
    structure = converter.convert(epub_file)

    output_file = f"{epub_file.replace('.epub', '')}.json"
    save_json_structure(structure, output_file)


if __name__ == "__main__":
    main()
