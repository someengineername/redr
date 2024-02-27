import exifreader
import os
import datetime
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


# def prompt_abort_renaming():
#     print()
#     print()
#     print('-' * 50)
#     print('||| ABORT RENAMING PROCESS |||')


# def is_suffix_applied(filename: str):
#     if filename[-5] == ')':
#         return True
#     else:
#         return False


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


# def prompt_warning_before_rename():
#     print()
#     print()
#     print('-' * 50)
#     print('Files inspected and dates from EXIF extracted succsesfull')
#     print('You wish to continue and rename all files?')


# def prompt_enf_of_program():
#     print()
#     print()
#     print('-' * 50)
#     print('||| PROGRAM END |||')


# def prompt_no_arw_files():
#     print()
#     print()
#     print('-' * 50)
#     print('||| NO ARW FILES IN DIRECTORY |||')


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


# def prompt_integrity_failed():
#     print()
#     print()
#     print('-' * 50)
#     print('||| ALL FILES ARE MODIFIED |||')

def prompt_message(message: str, additional_message=None, type='basic'):
    db_symbols = {'basic': '⚪', 'alert': '🔴', 'warning': '🟡', 'success': '🟢'}

    print('-' * 50)
    print(db_symbols[type] * 3, message, db_symbols[type] * 3)
    if additional_message:
        print(db_symbols['basic'], additional_message, db_symbols['basic'])
    print('-' * 50)
    return None


def change_wroking_doirectoty_routine():
    while True:
        prompt_message('Please, input working directory:')
        working_directoty = str(input())
        try:
            os.chdir(working_directoty)
            break
        except:
            prompt_message('Something went wrong', type='alert')
            prompt_message('Please, try again:', type='warning')

    prompt_message('Work directory updated. New directory:', type='success')
    prompt_message(str(os.getcwd()))


def main():
    # update / change working directory

    change_wroking_doirectoty_routine()

    # get all files with .arw extention
    file_list = filter(lambda x: x[-4:].lower() == '.arw', os.listdir())

    db_filename_exif_date = folder_inspection(file_list)

    if db_filename_exif_date:

        if check_integrity(db_filename_exif_date):
            prompt_message('ALL FILES ARE MODIFIED SUCCSESFULLY', type='success')
        else:
            print_out_detected_files(db_filename_exif_date)
            prompt_message('Files inspected and dates from EXIF extracted succsesfull',
                           'You wish to continue and rename all files?', type='warning')
            rename_process(db_filename_exif_date, True if str(input()) == 'y' else False)

    else:
        prompt_message('NO ARW FILES IN DIRECTORY', type='alert')

    prompt_message('PROGRAM END', type='success')


if __name__ == "__main__":
    promt_welcome_message()
    main()

# todo
# add .jpg filtering and renaming

# todo
# rework integrity check - make as filtering function, which gives None or filtered dict

# todo
# add correct integrity check - with filtering only files approved for renaming

# todo
# add progress bar while reading all files and making integrity check

# todo
# add progress bar while renaming process
