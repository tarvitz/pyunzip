# -*- coding: utf-8 -*-
import six
import argparse
from zipfile import ZipFile


def decode_filename(filename, codepage):
    """
    decode filename according by given codepage

    :param str | bytes filename: filename (bytes if python 2 version is used)
    :param str codepage: codepage, (cp866, cp1251, koi8-r, etc)
    :rtype: str
    :return: encoded file name
    """
    if six.PY3:
        return filename.encode('cp437').decode(codepage)
    elif six.PY2:
        return filename.decode(codepage)
    else:
        raise EnvironmentError("Wrong python interpreter version")


def main(opts):
    for filename in opts.files:
        zip_file = ZipFile(filename)
        info_list = zip_file.infolist()
        for entry in info_list:
            entry.filename = decode_filename(entry.filename, opts.codepage)
            zip_file.extract(entry, path=opts.dest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', metavar='filename.zip', nargs='+',
                        type=str)
    parser.add_argument('-c', '--code-page', dest='codepage',
                        required=True, metavar='encoding',
                        help='filename code page, cp866, cp1251, koi8-r, etc')
    parser.add_argument('-d', '--dest', dest='dest',
                        help='extract destination directory', required=False,
                        default='.')
    arguments = parser.parse_args()
    main(arguments)
