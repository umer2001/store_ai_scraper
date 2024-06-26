import os
import argparse
from purify import clean_html


def main(file_path):
    path, file_name = os.path.split(file_path)
    print(f"The file path is: {file_path}")
    clean_html(
        f"{path}/purified_{file_name}", html_file_path=f"{file_path}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a File.")
    parser.add_argument("file_name", type=str, help="The file name to process")

    args = parser.parse_args()
    main(args.file_name)
