import binascii
import re
import argparse
import os

class Patcher:
    '''
    ONLY TESTED FOR WINDOWS AND LINUX 64-BIT
    CAN BE PATCHED ON ALL WINDOWS BUILDS >1055 & LINUX BUILD 1055 (INCLUDES BOTH STABLE AND DEV)
    MADE BY: DE YI <https://github.com/deyixtan>
    '''
    INITIAL_LICENSE_CHECK_AOB = {"windows": b"80380074..488b..........48....74..........488d..........66........488d..........66........66......488d....66......4889",
                                 "linux":   b"80380074..488b..........48........48....74..........488b..............488d..........488d....................4885",
                                 "patch":   b"800801"}
    PERSISTENT_LICENSE_CHECK_AOB = {"windows": b"00c3cc55564883ec48",
                                    "linux":   b"00c390488b3f8b7720",
                                    "patch":   b"01"}
    THEME_CHECK_AOB = {"windows": b"0000c705......0000000000b80f0000006648",
                       "linux":   b"0000c7460400000000488d461848",
                       "patch":   b"01"}

    def __init__(self, file_path):
        self.file_path = file_path

        # get hex dump of input file
        with open(file_path, "rb") as file:
            self.hex_dump = bytearray(binascii.hexlify(file.read()))

    def patch_file(self):
        os_target = self.__get_file_os_target()
        if os_target != None and self.__is_initial_license_check_index_valid(os_target) and self.__is_persistent_license_check_index_valid(os_target) and self.__is_theme_check_index_valid(os_target):
            # bypass & patch file with changes
            self.__patch_initial_license_check(os_target)
            self.__patch_persistent_license_check(os_target)
            self.__patch_theme_check(os_target)

            try:
                with open(self.file_path, "wb") as file:
                    file.write(binascii.unhexlify(self.hex_dump))
            except PermissionError:
                return False
            return True
        return False

    def __get_file_os_target(self):
        if self.hex_dump.startswith(b"4d5a"):
            print(" >> Windows version")
            return "windows"
        elif self.hex_dump.startswith(b"7f454c4602"):
            print(" >> Linux version")
            return "linux"
        else:
            print(" >> Unknown version")
            return None

    def __index_is_valid(self, check_aob):
        patterns = re.findall(check_aob, self.hex_dump)
        pat_len = len(patterns)
        print(" >> found " + str(pat_len) + " occurences (1 expected)")

        for p in patterns:
            check_index = self.hex_dump.index(p)
            print(" >> found @" + hex(int(check_index/2)))

        return pat_len == 1

    def __is_initial_license_check_index_valid(self, os):
        print(" >> looking for INITIAL_LICENSE_CHECK_AOB")
        return self.__index_is_valid(Patcher.INITIAL_LICENSE_CHECK_AOB[os])

    def __is_persistent_license_check_index_valid(self, os):
        print(" >> looking for PERSISTENT_LICENSE_CHECK_AOB")
        return self.__index_is_valid(Patcher.PERSISTENT_LICENSE_CHECK_AOB[os])

    def __is_theme_check_index_valid(self, os):
        print(" >> looking for THEME_CHECK_AOB")
        return self.__index_is_valid(Patcher.THEME_CHECK_AOB[os])

    def __patch_check(self, check_aob, patch_aob):
        # bypass checks
        check_index = self.hex_dump.index(re.findall(check_aob, self.hex_dump)[0])
        self.hex_dump[check_index:check_index+len(patch_aob)] = patch_aob
        
    def __patch_initial_license_check(self, os):
        # bypass license
        self.__patch_check(Patcher.INITIAL_LICENSE_CHECK_AOB[os], Patcher.INITIAL_LICENSE_CHECK_AOB["patch"])

    def __patch_persistent_license_check(self, os):
        # bypass license
        self.__patch_check(Patcher.PERSISTENT_LICENSE_CHECK_AOB[os], Patcher.PERSISTENT_LICENSE_CHECK_AOB["patch"])

    def __patch_theme_check(self, os):
        # bypass theme
        self.__patch_check(Patcher.THEME_CHECK_AOB[os], Patcher.THEME_CHECK_AOB["patch"])

# script logic
def main():
    parser = argparse.ArgumentParser(description="Patch Sublime Merge")
    parser.add_argument("file_path", help="file path to sublime merge executable.")
    args = parser.parse_args()

    print("Patcher >> Starting job...")

    # check for valid file path
    if (os.path.isfile(args.file_path)):
        # performs patch
        patcher = Patcher(args.file_path)
        result = patcher.patch_file()

        if result:
            print("Patcher >> Successfully patched '{args.file_path}'.")
        else:
            print("Patcher >> Could not work on input file.")
    else:
        print("Patcher >> Please input a valid file path.")

# direct execution of the script
if __name__ == "__main__":
    main()
