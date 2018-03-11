import os
import io
import re
import codecs


def clean_telephone(text):
    return text.replace("\n", ".")


def clean_blogs(text):
    return re.sub("Posted by (.*?)\n", "", text)


def clean_twitter(text):
    text = text.replace("</p>", "\n")
    return text.replace("<p>", "")


def save_to_file(folder_name, file_name, text):

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    with io.open(file_name, 'w', encoding='utf8') as f:
        f.write(text)


def read_spam_and_email(file, output_folder, output_file):

    message_headers = ["Message-ID:", "Date:", "From:", "To:", "Subject:", "Mime-Version:", "Content-Type:",
                       "Content-Transfer-Encoding:", "Bcc:", "Ccc:", "docno=", "name=", "email=", "sent=",
                       "id=", "subject=", "received=", "inreplyto=", "X-From:", "X-To:", "X-cc:", "X-bcc:", "X-Folder:",
                       "X-Origin:", "X-FileName:", "Reply-To:"]

    txt_file = []
    with codecs.open(file, 'r', encoding='utf-8') as f:
        for line in f:
            if any(line.startswith(m) for m in message_headers):
                continue
            txt_file.append(line)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with codecs.open(output_file, 'w', encoding='utf-8') as f:
        for line in txt_file:
            f.write(line)


def main():

    """Telephone"""
    directory = "masc_tobecleaned_27feb2018/"
    output_folder = "masc_clean_07March2018/"

    for root, directories, filenames, in os.walk(directory):
        for file_name in filenames:
            if file_name.endswith('.txt'):
                path = os.path.join(root, file_name)
                folder_name = output_folder
                out_fname = folder_name

                if "/spam/" in path:
                    out_fname = out_fname + "/spam/"
                    read_spam_and_email(path, out_fname, out_fname + file_name)
                    continue

                if "/email/" in path:
                    out_fname = out_fname + "/email/"
                    read_spam_and_email(path, out_fname, out_fname + file_name)
                    continue

                file = io.open(os.path.join(root, file_name), mode="r", encoding="utf-8")
                text = file.read()

                if "/telephone" in path:
                    out_fname = out_fname + "/telephone/"
                    cleaned_text = clean_telephone(text)
                    save_to_file(out_fname, out_fname + file_name, cleaned_text)

                elif "/twitter/" in path:
                    out_fname = out_fname + "/twitter/"
                    cleaned_text = clean_twitter(text)
                    save_to_file(out_fname, out_fname + file_name, cleaned_text)

                elif "/blog/" in path:
                    out_fname = out_fname + "/blog/"
                    cleaned_text = clean_blogs(text)
                    save_to_file(out_fname, out_fname + file_name, cleaned_text)


if __name__ == "__main__":
    main()


