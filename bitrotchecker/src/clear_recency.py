from bitrotchecker.src.recency_util import RecencyUtil


def main():
    recency_util = RecencyUtil()

    with open("files_to_remove_from_recency.txt", mode="r") as input_file:
        for line in input_file.readlines():
            file_path = line.strip()
            if file_path:
                recency_util._remove_recency_record(file_path)


if __name__ == "__main__":
    main()
