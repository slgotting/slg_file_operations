import os
import json
import re
import pickle
# from decorators.files import get_filename
# from decorators.logging import log_error


class FileOperations:

    '''
    Working directory defaults to the current working directory
    If sub_directory == True, then the write folder is found as a subdirectory of the current working directory
    If start_home == True, then start from the home directory in order to find the working_directory
        (this clearly negates sub_directory, however sub_directory has prio if True is passed for both)
    Working directory can be set again with self.set_working_directory(*args)
    Methods will default to writing to the default_filename if their filename is not declared. Same for directory
    '''

    def __init__(self, working_directory='', sub_directory=False,
                 start_home=False, default_filename=None):

        self.set_working_directory(
            working_directory, sub_directory, start_home)

        self.default_filename = default_filename

        if self.default_filename != None:
            self.default_filename_with_path = self.working_directory + '/' + self.default_filename

            # try to create file so we dont get any errors
            try:
                open(self.default_filename_with_path, 'x')
            except:
                pass

        # self.create directory if dir doesnt exist - this is a todo item, naming not immediately evident

    def set_working_directory(
            self, working_directory='', sub_directory=False, start_home=False):

        if not working_directory.startswith('/') and working_directory:
            working_directory = '/' + working_directory

        if sub_directory:
            self.working_directory = os.getcwd() + working_directory
        elif start_home:
            self.working_directory = os.environ.get('HOME') + working_directory
        else:
            self.working_directory = working_directory or os.getcwd()

    # @get_filename('.json')
    def write_json(self, data, filename=None):
        '''
        writes json to directory <self.working_directory> with name <filename>
        '''
        with open(f"{self.working_directory}/{filename}", 'w') as outfile:
            json.dump(data, outfile)

    def read_json(self, filename):
        with open(f"{self.working_directory}/{filename}", 'r') as json_:
            return json.load(json_)

    # @get_filename('.pickle')
    def write_pickle(self, data, filename=None):
        if not filename:
            filename = self.default_filename
        with open(f"{self.working_directory}/{filename}", "wb") as file_:
            pickle.dump(data, file_)

    def read_pickle(self, filename=None):
        if not filename:
            filename = self.default_filename
        with open(f"{self.working_directory}/{filename}", "rb") as file_:
            output = pickle.load(file_)
        return output

    # @get_filename('.txt')
    def write_text(self, data, filename, method='a+'):
        with open(f"{self.working_directory}/{ filename }", method) as file_:
            file_.write(data)

    # @get_filename('.txt')
    # @log_error('file_operations.log', True)
    def read_text(self, filename):
        with open(f"{self.working_directory}/{ filename }", 'r') as file_:
            file.seek(0)
        for line in file_:
            print(line.strip())

    def get_file_parts(self, file_):
        '''
        file needs appropriate path headed
        returns filename, file_extension
        '''
        return os.path.splitext(file_)

    def delete_file(self, file_):
        try:
            os.remove(f"{self.working_directory}/{file_}")
        except:
            print('No file to delete')

    def append_text(self, text, file_with_path=None):

        pass

    def verify_defaults(self):

        pass

    def get_files_in_directory(
            self, walk=True, directory=None, full_path=False, recurse=False,
            recursing=False, rec_opts={},
            filetype=''):
        '''
        :param recursing: should never be changed from False, used internally
        :param rec_opt: Recursion options, meant to be passed as dict,
            Params are as follows:
                :param recursion_depth: How far to recurse (default=9999999)
                :param curr_recursion_depth: no purpose to stray from default of: (default=0)
                :param incl_path_to_file: records the path starting from initial directory
                :param curr_path: the current path, needed for :param:incl_path_to_file
                :param sub_dir_filenames: used internally not to be changed
        :param filetype <str>: Return only certain filetype

        BROKEN BUT NOT FIXING RIGHT NOW
            when recurse is True, if recursing more than one level, it also appends an inappropriate
            file for each path in the curr path.
            Example:
                file is /testing/sockets/another_level/another_level.html
                if the starting dir is /testing/ then it will append
                both sockets/another_level/another_level.html and sockets/another_level.html

            Seems fairly complex but I don't need now, because the bad ones are appended at the end, and i currently grab the first seen
        '''

        directory = directory or self.working_directory

        sub_dir_filenames = rec_opts.get('sub_dir_filenames', [])
        files = []

        if walk:
            for root, directories, filenames in os.walk(directory):

                # used by the end block to strip away the sub_dir_filenames
                if rec_opts.get('curr_recursion_depth', 0) > 0:
                    sub_dir_filenames += filenames

                for filename in filenames:
                    if full_path == False:
                        file_ = filename
                    else:
                        file_ = os.path.join(root, filename)

                    if not full_path:
                        files.append(rec_opts.get('curr_path', '') + file_)

                if recurse:
                    if rec_opts.get(
                            'curr_recursion_depth', 0) < rec_opts.get(
                            'recursion_depth', 9999999):
                        for dir_ in directories:
                            files += self.get_files_in_directory(
                                f'{directory}/{dir_}',
                                recurse=True,
                                recursing=True,
                                full_path=full_path,
                                rec_opts={
                                    'recursion_depth': rec_opts.get('recursion_depth', 9999999),
                                    'curr_recursion_depth': rec_opts.get('curr_recursion_depth', 0) + 1,
                                    'incl_path_to_file': rec_opts.get('incl_path_to_file', True),
                                    'curr_path': rec_opts.get('curr_path', '') + dir_ + '/',
                                    'sub_dir_filenames': sub_dir_filenames
                                }
                            )
        else:
            files = [
                f for f in os.listdir(self.working_directory)
                if os.path.isfile(f)]

        # get on the last pass of the recursion, :param:recursing should not be edited
        if not recursing:
            # strip subdirectory filenames
            files = [file_ for file_ in files
                     if file_ not in sub_dir_filenames]

        if filetype:
            if not filetype.startswith('.'):
                filetype = '.' + filetype
            files = [file for file in files if self.get_file_parts(file)[
                1] == filetype]

        return files

    def regex_sub_files(self, regex, files, sub='', count=1):
        '''
        calls a regex sub for each file in files
        TODO: make it so that if sub == 'index' or 'idx' (not sure which), then we can substitute in the index of the file in files
        includes check to make sure returned filename is acceptable and requires input
        '''
        pattern = re.compile(regex)
        new_filenames = []

        for idx, file_ in enumerate(files):

            new_filename = pattern.sub(
                sub, self.get_file_parts(file_)[0],
                count=count)

            if idx == 0:
                while True:
                    ans = input(
                        f"{new_filename} is your new filename, is this acceptable? (y/n)")
                    if ans.lower() == 'y':
                        break
                    elif ans.lower() == 'n':
                        print('Sorry to hear your regex failed, stupid dum dum.')
                        return
                    else:
                        pass
            new_filenames.append(new_filename + self.get_file_parts(file_)[1])
            os.rename(
                f"{self.working_directory}/{file_}",
                f"{self.working_directory}/{new_filename + self.get_file_parts(file_)[1]}")

        print('Your new filenames: \n')
        for file_ in new_filenames:
            print(file_)
