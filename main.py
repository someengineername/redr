import sys

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
    print()
    print('')
    print('/')
    print('| Current directory:')
    print('| ', os.getcwd())
    print('\\')
    print()


def tags_error_handler(dates_list: list, file_name: str) -> datetime:
    # info message
    print('/')
    print('| ERROR DATE / MISSING DATE HANDLER:')
    print('|')
    print('| File name:')
    print('|    ', file_name)
    print('| Dates:')

    # print variant for choosing
    for pos, date in enumerate(dates_list):
        try:
            print('|    ', pos + 1, ')', datetime.datetime.isoformat(date))
        except:
            print('|    ', pos + 1, ')', 'date error')

    # pick choice from user, error handler for non-int picks and any str-inputs
    while True:
        try:
            user_pick = int(input('| What date to pick?\n'))
            if 0 < user_pick <= len(dates_list):
                answer = dates_list[user_pick - 1]
                break
            else:
                print('No such variant! Enter correct number from 1 to', len(dates_list))
        except TypeError:
            print('Wrong input! Please, enter correct number.')
        else:
            print('Something went wrong. Repeat input.')

    return answer


def print_out_detected_files(db_filenames_dates: dict):
    print(str('-' * 30 + ' ' + '-' * 30))
    print(str('File name:'.ljust(30) + ' ' + 'EXIF date:'))
    print(str('-' * 30 + ' ' + '-' * 30))
    for k, v in db_filenames_dates.items():
        print(k.ljust(30), ' ', v)
    return None


def folder_inspection(file_list_iterator) -> dict:
    """
    analyzes folder with script file for .ARW files and returns dict (file name -> str, date -> date)
    """

    result = dict()

    for file_name in file_list_iterator:
        with open(file_name, 'rb') as raw:
            # extract EXIF tags from file
            exif_tags_extracted = {k: v for k, v in exifreader.process_file(raw).items() if k != 'JPEGThumbnail'}

            # check all date values in EXIF tags
            # db_date_tags - list of all values |datetime| from date-type tags
            db_date_tags = []
            for tag in ['Image DateTime', 'Thumbnail DateTime', 'EXIF DateTimeOriginal', 'EXIF DateTimeDigitized']:
                try:
                    db_date_tags.append(datetime.datetime.strptime(str(exif_tags_extracted[tag]),
                                                                   '%Y:%m:%d %H:%M:%S'))
                except:
                    pass

            # check if all values are the same in db_date_tags
            # if yes - pick one
            # if no - choose by user

            if all(map(lambda x: True if x == db_date_tags[0] else False, db_date_tags)):
                date_of_photo_from_exif = db_date_tags[0]
                result[str(file_name)] = result.setdefault(file_name, date_of_photo_from_exif)
            else:
                result[str(file_name)] = tags_error_handler(db_date_tags, file_name)

    return result


def rename_process(db_filename_exif_date: dict, answer=True):
    # abort renaming process based on input
    if answer:
        # go by dict of filename and EXIF dates, prepare new filename based on datetime in value of dict by key
        # for file_name, new_date in db_filename_exif_date.items():
        #     new_file_name = datetime.datetime.strftime(new_date, '%Y_%m_%d_%H_%M_%S') + '.ARW'

        while True:

            try:
                old_name = next(iter(db_filename_exif_date))
                new_name = db_filename_exif_date[old_name]
                new_file_name = datetime.datetime.strftime(new_name, '%Y_%m_%d_%H_%M_%S') + '.ARW'
                os.rename(old_name, new_file_name)
                db_filename_exif_date.pop(old_name)
            except FileExistsError:

                print('file exist', new_file_name)

                # to prevent infinite loop - delete duplicate name from list
                db_filename_exif_date.pop(old_name)

            except StopIteration:
                break

    else:
        prompt_message('ABORT RENAMING PROCESS')


def check_integrity(db_dict: dict):
    answer = True

    for k, v in db_dict.items():
        try:
            file_name_struct = list(map(int, [k[:4], k[5:7], k[8:10], k[11:13], k[14:16], k[17:19]]))
        except:
            file_name_struct = [0, 0, 0, 0, 0, 0]
        time_stamp_struct = [v.year, v.month, v.day, v.hour, v.minute, v.second]
        if file_name_struct == time_stamp_struct:
            pass
        else:
            answer = False
            break

    return answer


def prompt_message(message: str, additional_message=None, type='basic'):
    db_symbols = {'basic': '⚪', 'red': '🔴', 'yellow': '🟡', 'green': '🟢'}

    print('-' * 50)
    print(db_symbols[type] * 3, message, db_symbols[type] * 3)
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
        except:
            prompt_message('Something went wrong', type='red')
            prompt_message('Please, try again:', type='yello')

    prompt_message('Work directory updated. New directory:',str(os.getcwd()), type='green')
    # prompt_message(str(os.getcwd()))


def main():
    # update / change working directory

    change_working_directory_routine()

    db_files_for_renaming = directory_inspection_routine()

    if db_files_for_renaming:
        prompt_message('List successfully created', type='green')
        # ask for print-out

        # ask for confirmation

        #do the renaming

    else:
        prompt_message('No files detected', type='green')



    prompt_message('End of program', type='green')

    raise Exception

    # get all files with .arw extention
    file_list = filter(lambda x: x[-4:].lower() == '.arw', os.listdir())

    db_filename_exif_date = folder_inspection(file_list)

    if db_filename_exif_date:

        if check_integrity(db_filename_exif_date):
            prompt_message('ALL FILES ARE MODIFIED SUCCSESFULLY', type='green')
        else:
            print_out_detected_files(db_filename_exif_date)
            prompt_message('Files inspected and dates from EXIF extracted succsesfull',
                           'You wish to continue and rename all files?', type='yellow')
            rename_process(db_filename_exif_date, True if str(input()) == 'y' else False)

    else:
        prompt_message('NO ARW FILES IN DIRECTORY', type='red')

    prompt_message('PROGRAM END', type='green')


def directory_inspection_routine() -> dict[str, str]:
    """
    Function (routine) look's-up through current working directory and searches ARW and JPG files, which are not named in accordance with pattern (YYYY_MM_DD_HH_MM_SS.EXT). Based on user's input - JPG files may or may not be included into further processing list. As return gives dict{file_name: exif_date}. If no applicable files are found - returns None.
    :return:
    """

    result = dict()

    prompt_message('Cheking-in files...', type='yellow')

    list_arw_files = []
    list_jpg_files = []

    # get ALL files
    # filter only non 'YYYY_MM_DD_HH_MM_SS' files names (exclude files already renamed)
    with os.scandir(os.getcwd()) as it:
        for pos in tqdm(it):
            if not pos.name.startswith('.') and pos.is_file():
                # get file name
                file_name = pos.name

                # RE application to check pattern
                pattern = re.compile(r'\d{4}_\d{2}_\d{2}_\d{2}_\d{2}')
                checker_func = lambda x: True if pattern.match(x) else False

                # if file extention ARW and without pattern - place in distinct list
                if file_name.lower().endswith('.arw') and not checker_func(file_name):
                    list_arw_files.append(pos)
                # if file extention JPG and without pattern - place in distinct list
                elif file_name.lower().endswith('.jpg') and not checker_func(file_name):
                    list_jpg_files.append(pos)

    # sequnce to merge or ignore JPG-files into final list
    if len(list_jpg_files) > 0:
        prompt_message('JPG files detected',type='red')
        prompt_message('Do you wish to include JPG files into renaming process? Y / N','JPG files may not include correct EXIF data.\n(based on export settings in Lightroom)', type='yellow')
        # prompt_message(,'')
        # prompt_message()
        if input() == 'y':
            list_all_files = list_jpg_files + list_arw_files
        else:
            list_all_files = list_arw_files
    else:
        list_all_files = list_arw_files


    # just make a plug with empty EXIF data - fill it later on
    # for now - to check further algo
    temp_dict = {k.name : 'DATA' for k in list_all_files}


    if len(list_all_files) == 0:
        # prompt_message('No applicable files are detected', type='yellow')
        return None
    else:
        prompt_message('Total count:',str(len(list_all_files)) + ' files')
        return temp_dict


if __name__ == "__main__":
    promt_welcome_message()
    main()

# todo
# add .jpg filtering and renaming

# todo
# add progress bar while renaming process
