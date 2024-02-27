import exifreader
import os
import datetime
import re
from tqdm import tqdm
from art import tprint


def promt_welcome_message():
    tprint('R E D R   Script')
    print('Raw Exif Date Renamer Script')
    # tprint('RENAMER')
    print('')
    print('/')
    print('| Welcome!')
    print('| ')
    print('| This little script will rename all .ARW files according to the date described in EXIF data')
    print('| Name pattern will be applied as:')
    print('|    YYYY-MM-DD-HH-MM   ')
    print(
        '| If multiple photos of the same date (in-EXIF) will be detected:\n'
        '|    YYYY-MM-DD-HH-MM-1,YYYY-MM-DD-HH-MM-2 and so on')
    print('\\')


def print_out_detected_files(db_filenames_dates: dict):
    print(str('-' * 30 + ' ' + '-' * 30))
    print(str('File name:'.ljust(30) + ' ' + 'EXIF date:'))
    print(str('-' * 30 + ' ' + '-' * 30))
    for k, v in db_filenames_dates.items():
        print(k.ljust(30), ' ', v)
    return None


def prompt_message(message: str, additional_message=None, type_color='basic'):
    db_symbols = {'basic': '⚪', 'red': '🔴', 'yellow': '🟡', 'green': '🟢'}

    print('-' * 50)
    print(db_symbols[type_color] * 3, message, db_symbols[type_color] * 3)
    if additional_message:
        print(db_symbols['basic'], additional_message, db_symbols['basic'])
    print('-' * 50)
    return None


def change_working_directory_routine():
    while True:
        prompt_message('Please, input working directory:')
        working_directoty = str(input())
        try:
            os.chdir(working_directoty)
            break
        except OSError:
            prompt_message('Wrong directory input', type_color='red')
            prompt_message('Please, try again:', type_color='yellow')

    prompt_message('Work directory updated. New directory:', str(os.getcwd()), type_color='green')
    # prompt_message(str(os.getcwd()))


def is_pattern_complied(string, pattern):
    if pattern.match(string):
        return True
    else:
        return False


def date_input_routine() -> datetime.datetime:
    prompt_message('Please enter valied date:', type_color='yellow')

    while True:
        answer = input()

        if is_pattern_complied(answer, re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')):
            prompt_message('Date applied')
            break
        else:
            prompt_message('Invalid input. Try again', type_color='yellow')

    return datetime.datetime.strptime(answer, '%Y:%m:%d %H:%M:%S')


def directory_inspection_routine() -> dict[str, str]:
    """
    Function (routine) look's-up through current working
    directory and searches ARW and JPG files, which are
    not named in accordance with pattern (YYYY_MM_DD_HH_MM_SS.EXT).
    Based on user's input - JPG files may or may not be included
    into further processing list. As return gives dict{file_name: exif_date}.
    If no applicable files are found - returns None.
    :return:
    """

    result = dict()

    prompt_message('Cheking-in files...', type_color='yellow')

    list_arw_files = []
    list_jpg_files = []

    # get ALL files
    # filter only non 'YYYY_MM_DD_HH_MM_SS' files names (exclude files already renamed)
    with os.scandir(os.getcwd()) as it:
        for pos in it:
            if not pos.name.startswith('.') and pos.is_file():
                # get file name
                file_name = pos.name

                # REGEX application to check pattern
                pattern = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}')

                # if file extention ARW and without pattern - place in distinct list
                if file_name.lower().endswith('.arw') and not is_pattern_complied(file_name, pattern):
                    list_arw_files.append(pos)
                # if file extention JPG and without pattern - place in distinct list
                elif file_name.lower().endswith('.jpg') and not is_pattern_complied(file_name, pattern):
                    list_jpg_files.append(pos)

    # sequnce to merge or ignore JPG-files into final list based on user input
    if len(list_jpg_files) > 0:
        prompt_message('JPG files detected', type_color='red')
        prompt_message('Do you wish to include JPG files into renaming process? Y / N',
                       'JPG files may not include correct EXIF data.\n(based on export settings in Lightroom)',
                       type_color='yellow')
        if input() == 'y':
            list_all_files = list_jpg_files + list_arw_files
        else:
            list_all_files = list_arw_files
    else:
        list_all_files = list_arw_files

    # if no files detected - return empty dict
    if len(list_all_files) == 0:
        return result
    # if files presented - generate dict with EXIF dates connected via dict
    else:
        for filename in tqdm(list_all_files, colour='MAGENTA'):

            # TODO
            # remove 99999(9) after finishing the algorytm!
            # extracted_date_from_exif = datetime.datetime(year=2000, month=12, day=31, hour=12, minute=00)

            with open(filename.name, 'rb') as photo_file:
                # TODO
                # apply exception handling - missing EXIF tags and so on

                # extracting EXIF tags
                exif_tags_extracted = {k: v for k, v in exifreader.process_file(photo_file).items() if
                                       k in ['Image DateTime', 'Thumbnail DateTime', 'EXIF DateTimeOriginal',
                                             'EXIF DateTimeDigitized']}

                # check if tags even presented:
                if exif_tags_extracted:
                    list_of_all_dates = [v for k, v in exif_tags_extracted.items()]

                    # if all dates are equal - pick first one
                    if all(map(lambda x: x, list_of_all_dates)):
                        # extracted_date_from_exif = str(list_of_all_dates[0])
                        extracted_date_from_exif = datetime.datetime.strptime(str(list_of_all_dates[0]),
                                                                              '%Y:%m:%d %H:%M:%S')
                    # if dates not equal or not even presented
                    else:
                        for enum, position in enumerate(list_of_all_dates):
                            print(str(enum + 1), position)
                        pass

                # no tags presented, need to enter the date!!!
                else:
                    prompt_message('No tags presented for file', str(file_name), type_color='red')
                    extracted_date_from_exif = date_input_routine()

            # fill-up dictionary by EXTRACTED_DATE_FROM_EXIF value (no matter how we get this number)
            result[filename.name] = result.setdefault(filename.name, extracted_date_from_exif)

    return result


def renaming_rouitne(dict_filename_and_exif_date: dict):
    # go by dict and try to rename file
    for filename, exif_date in dict_filename_and_exif_date.items():
        old_name = filename
        new_name = str(str(exif_date.year) + '_' +
                       str(exif_date.month) + '_' +
                       str(exif_date.day) + '_' +
                       str(exif_date.hour) + '_' +
                       str(exif_date.minute) + '_' +
                       str(exif_date.second)) + old_name[-4:]

        try:
            os.rename(old_name,new_name)
        except:
            print(str(filename + ' error'))



def main():
    # update / change working directory
    change_working_directory_routine()

    # extract names of files applicable for renaming process (more on that in directory_inspection_routine docs)
    dict_filename_and_exif_date = directory_inspection_routine()

    # if applicable files list generated (non-zero lenght) - go for listing and confirmation
    if dict_filename_and_exif_date:
        prompt_message('List successfully created', str('Files count:' + str(len(dict_filename_and_exif_date))),
                       type_color='green')
        prompt_message('Would you like to see list of files?')
        if input() == 'y':
            print_out_detected_files(dict_filename_and_exif_date)
        else:
            pass

        # ask for confirmation
        prompt_message("Base actions applied and we're ready to go")
        prompt_message('Do you confirm the start of renaming process?', type_color='red')

        # if confirmation recived - go to renaming procee
        if input() == 'y':
            renaming_rouitne(dict_filename_and_exif_date)
        # if confirmation not recived - abort process, finish the programm
        else:
            prompt_message('Renaming process cancelled', type_color='yellow')
    # if applicable files are not found - finish the program
    else:
        prompt_message('No files detected', type_color='green')

    prompt_message('End of program', type_color='green')


if __name__ == "__main__":
    promt_welcome_message()
    main()
