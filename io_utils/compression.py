"""
:module: compression.py
:description: Module for uncompressing various compressed files

:author: Arthur Moore <arthur.moore85@gmail.com>
:date: 09/12/16
"""
import os
import zipfile
import libarchive.public
import subprocess
from pyunpack import Archive

__author__ = 'arthur'

RUNS_COMPRESSED = [
    'mame-libretro',
    'neogeo',
    'atari2600',
    'pcengine',
    'snes',
    'gba',
    'gbc',
    'gb',
    'nes',
    'nds'
]


class Compression(object):
    def __init__(self, target):
        self.target_dir = target
        self.file_type = None

    def determine_type(self, file_o):
        """
        Determines filetype, and requirements
        """
        file_type = os.path.splitext(file_o)[1][1:].lower()
        return file_o, file_type

    def unzip(self, file_obj):
        """
        Unzips a ZIP archive
        :param file_obj: file to be unzipped
        """
        try:
            zip_ref = zipfile.ZipFile(file_obj, 'r')
            zip_ref.extractall(self.target_dir)
            zip_ref.close()
        except zipfile.BadZipfile:
            self.clean_up(os.path.join(self.target_dir, file_obj))

    def unzip_seven(self, file_obj):
        """
        Extracts contents of 7z file
        :param file_obj: file to be used.
        """
        with libarchive.public.file_reader(file_obj) as e:
            for entry in e:
                output_file = os.path.join(self.target_dir, entry.pathname)
                with open(output_file, 'wb') as f:
                    for block in entry.get_blocks():
                        f.write(block)

    def unrar(self, file_obj):
        """
        Extracts a RAR archive
        :param file_obj: file to be extracted.
        """
        Archive(file_obj).extractall(self.target_dir)

    def clean_up(self, file_o):
        """
        Cleans redundant archive file.
        """
        os.remove(file_o)

    def extract(self, file_o):
        """
        Extracts all files
        """
        f, t = self.determine_type(file_o)
        parent_dir = f.split(os.sep)[-2]
        if parent_dir not in RUNS_COMPRESSED:
            if t == 'zip':
                self.unzip(f)
            elif t == '7z':
                self.unzip_seven(f)
            elif t == 'rar':
                self.unrar(f)
            elif t == 'ecm':
                subprocess.call('ecm-uncompress "{}"'.format(file_o))

            for ecm_file in os.listdir(parent_dir):
                if ecm_file.endswith(".ecm"):
                    self.extract(ecm_file)
                    self.clean_up(ecm_file)

            self.clean_up(file_o)
