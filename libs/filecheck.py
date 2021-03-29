import os

#define class to check size of video
class FileCheck():
    def __init__(self, file_path):
        self.file_dir = file_path

    def get_filesize(self):
        # get the file size
        file_byte = os.path.getsize(self.file_dir)
        return self.sizeConvert(file_byte)

    def sizeConvert(self, size):
        # size convert
        K, M, G = 1024, 1024 ** 2, 1024 ** 3
        FLAT=0
        if size >= G:
            #define if size of video larger that 60GB return 0
            return size, FLAT
        elif size >= M:
            return size, FLAT
        elif size >= K:
            return size, FLAT
        else:
            FLAT=1
            return size, FLAT
