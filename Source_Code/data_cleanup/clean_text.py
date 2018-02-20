import io
import sys
from normalize_csv_comments import *

''' Path for normalize_csv_comments.py:
https://github.com/sfu-discourse-lab/SFU_Comment_Extractor/blob/master/Source_Code/CSV_creation/normalize_csv_comments.py'''


def main():
    directory = input_folder

    for root, directories, filenames, in os.walk(directory):
        for file_name in filenames:
            if file_name.endswith('.txt'):
                text_file = io.open(os.path.join(root, file_name), mode="r", encoding="utf-8")
                cleaned_text = normalize(text_file.read())
                path = os.path.join(root, file_name)
                year = re.search('Nov2017/(.+?)/', path).group(1)

                folder_name = output_folder + str(year)
                file_name = folder_name + "/" + file_name

                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)

                with io.open(file_name, 'w', encoding='utf8') as f:
                    f.write(cleaned_text)


if __name__ == "__main__":
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    main()

