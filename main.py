import exifreader
import os
import datetime
import re
import random
from tqdm import tqdm
from art import tprint


def prompt_welcome_message():
    """
    Welcoming message at the start of the program
    :return: None
    """
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
    """
    Printing dictionary with pair {file_name : datetime} in easy-view style.
    :param db_filenames_dates: {file_name : datetime}
    :return: None
    """
    print(str('-' * 30 + ' ' + '-' * 30))
    print(str('File name:'.ljust(30) + ' ' + 'EXIF date:'))
    print(str('-' * 30 + ' ' + '-' * 30))
    for k, v in db_filenames_dates.items():
        print(k.ljust(30), ' ', v)


def prompt_message(message: str, additional_message: str = None, type_color='basic'):
    """
    Unified function to deal with different styles of messages.
    Have 2 line of text with 1 semaphore-style lights on the head of the message.
    Bottom line of a message will always be with white lights,
    :param message: type == str. 1st line of a message. Will be covered by color lights on sides.
    :param additional_message: type == str. 2nd line of a message. Will be covered by white light always.
    :param type_color: type == str. Allowed input: ('red': '🔴', 'yellow': '🟡', 'green': '🟢').
    If not specified - white color.
    :return: None
    """
    db_symbols = {'basic': '⚪', 'red': '🔴', 'yellow': '🟡', 'green': '🟢'}

    picked_colour = db_symbols.get(type_color, 'basic')

    print('-' * 50)
    print(picked_colour * 3, message, picked_colour * 3)
    if additional_message:
        print(db_symbols['basic'], additional_message, db_symbols['basic'])
    print('-' * 50)


def change_working_directory_routine():
    """
    Simple routine to change working directory based on user's input.
    :return:
    """
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


def is_pattern_complied(string: str, pattern) -> bool:
    """
    Routine to check if string is comply with suggested regex pattern
    :param string: String to pass a test
    :param pattern: regex pattern r"...."
    :return: bool
    """

    if pattern.match(string):
        return True
    else:
        return False


def date_input_routine() -> datetime.datetime:
    """
    Routine to give user a possibility to enter the date of a file manually.
    Can be applied in several cases such as: missing EXIF dates, conflit of a dates in EXIF date e.t.c.
    :return: datetime
    """
    prompt_message('Please enter valied date:', type_color='yellow')

    while True:
        answer = input()

        if is_pattern_complied(answer, re.compile(r'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}')):
            prompt_message('Date applied')
            break
        else:
            prompt_message('Invalid input. Try again', type_color='yellow')

    return datetime.datetime.strptime(answer, '%Y:%m:%d %H:%M:%S')


def directory_inspection_routine() -> dict[str, str] | None:
    """
    Function (routine) look's-up through current working
    directory and searches ARW and JPG files, which are
    not named in accordance with pattern (YYYY_MM_DD_HH_MM_SS.EXT).
    Based on user's input - JPG files may or may not be included
    into further processing list. As return gives dict{file_name: exif_date}.
    If no applicable files are found - returns None.
    :return: dict | None
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
                pattern = re.compile(r'\d{4}_\d{1,2}_\d{1,2}_\d{1,2}_\d{1,2}')

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

            with open(filename.name, 'rb') as photo_file:

                try:
                    exif_tags_extracted = {k: v for k, v in exifreader.process_file(photo_file).items() if
                                           k in ['Image DateTime', 'Thumbnail DateTime', 'EXIF DateTimeOriginal',
                                                 'EXIF DateTimeDigitized']}
                except KeyError:
                    exif_tags_extracted = dict()

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


def renaming_recursive_function(filename: str, old_name: str, new_name: str, counter=0):
    """
    Recursive function which is truing to rename a file nevertheless an OSError (such as "file exists" error)

    :param filename: Original name of a file
    :param old_name: Same as filename. In fact, function can be refactored not to use this param.
    :param new_name: New name of file, which is generated based on timedate.strptime method from EXIF tags.
    :param counter: recursive parameter, which translates downwards by recursive calls. +1, +2, e.t.c.
    Used as an indicator of a copy of a file (number in brackets)
    :return: None
    """

    counter += 1
    try:
        os.rename(old_name, new_name)
    except OSError:
        modified_name = ''
        if counter == 1:
            modified_name = new_name[:-4] + '-' + '(' + str(counter) + ')' + filename[-4:]
        elif counter > 1:
            modified_name = new_name[:-8] + '-' + '(' + str(counter) + ')' + filename[-4:]
        renaming_recursive_function(filename, old_name, modified_name, counter)


def renaming_routine(dict_filename_and_exif_date: dict):
    """
    Main routine for renaming process.
    Goes through the dict, prepared before and calling for recursive function of renaming.
    :param dict_filename_and_exif_date: {file_name:str : datetime: datetime}
    :return: None
    """
    for filename, exif_date in tqdm(dict_filename_and_exif_date.items()):
        old_name = filename
        new_name = datetime.datetime.strftime(exif_date, '%Y_%m_%d_%H_%M_%S') + old_name[-4:]
        renaming_recursive_function(filename, old_name, new_name)


def scramble_routine():
    """
    Routine, used in development to scramble all the names of all files in directory.
    Simply goes through a directory and gives XXXXXXXXXXXXXXXX.YYY name, where X - [0...9], .YYY - extension of a file
    Warning! Picks ALL the files, not only .ARW and .JPG
    :return: None
    """
    with os.scandir(os.getcwd()) as it:
        for pos in tqdm(it):
            if not pos.name.startswith('.') and pos.is_file():
                new_name = ''.join([str(random.randint(0, 9)) for _ in range(15)]) + pos.name[-4:]
                os.rename(pos.name, new_name)
        print()


def scramble_routine_entry_point():
    """
    Entry point to call scramble routine.
    User confirmation applied.
    :return: None
    """
    prompt_message('???ARE YOU SURE???', type_color='red')
    prompt_message('!!!FAILURE CAN BE!!!', type_color='red')

    if input() == 'y':
        scramble_routine()
    else:
        prompt_message('scramlbe cancelled', type_color='green')


def main():
    """
    Main routine to organize renaming process program.
    In final product - scramble routine entry point is commented due to high risks of failure.
    Such as renaming of a non .ARW and .JPG files
    :return: None
    """
    # update / change working directory
    change_working_directory_routine()

    # QUITE DANGEROUS!
    # scramble_routine_entry_point()

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
            renaming_routine(dict_filename_and_exif_date)
        # if confirmation not recived - abort process, finish the programm
        else:
            prompt_message('Renaming process cancelled', type_color='yellow')
    # if applicable files are not found - finish the program
    else:
        prompt_message('No files detected', type_color='green')

    prompt_message('End of program', type_color='green')


if __name__ == "__main__":
    prompt_welcome_message()
    main()
