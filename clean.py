import argparse
from purify import clean_html


def main(file_name):
    print(f"The provided URL is: {file_name}")
    clean_html(
        f"../purified/purified_{file_name}", html_file_path=f"../html/{file_name}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a File.")
    parser.add_argument("file_name", type=str, help="The file name to process")

    args = parser.parse_args()
    main(args.file_name)
