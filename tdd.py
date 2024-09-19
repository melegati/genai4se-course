from openai import OpenAI
import subprocess
import sys
import argparse
import os
import re
import fnmatch
import shutil

sys.path.append("..")

TEST_PASSED = "TEST_PASSED"
TEST_FAILED = "TEST_FAILED"
TEST_PASSED_WITHOUT_AI = "TEST_PASSED_WITHOUT_AI"


def get_path(filename, idx, filetype="py"):
    return "{}.{}".format(filename.replace(".py", "")+"_"+str(idx), filetype)


def get_next_filename(filename, idx):
    return filename + "_" + str(idx)

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def how_many_to_skip(original_file, multiplier=1):
    file_split = original_file.split("/")
    path = "/".join(file_split[0:len(file_split) - 1])
    path = "." if path == "" else path
    original_file = file_split[-1]
    files = os.listdir(path)
    search_file = original_file.replace(".py", "") + "_*.py"
    matching_files = [file for file in files if fnmatch.fnmatch(file, search_file)and len(file.replace(original_file.replace(".py", ""), "").split("_")) == multiplier +1]
    pattern = re.compile(r'\d+')

    # Extract numbers from each filename and create an array
    numbers_array = [int(pattern.search(file).group()) for file in matching_files if pattern.search(file)]
    files_to_skip = max(numbers_array) if len(numbers_array) > 0 else 0
    return files_to_skip

class TestsBasedCoder:

    def __init__(self, key, test_file, code_file, full_context, print_context, print_message, ):
        self.client = OpenAI(api_key=key)
        self.role = "You are part of a Test Driven Development team. Your role is the development of code such that the provided code is fulfilled."
        self.messages_sent = []
        self.messages_received = []
        self.messages_received_parsed_code = []
        self.errors = []
        self.test_file = test_file
        self.code_file = code_file
        self.full_context = full_context
        self.print_context = print_context
        self.print_message = print_message

    def create_prompt(self):
        trace = self.get_traces_of_last_run()
        if trace == TEST_PASSED:
            return TEST_PASSED
        
        prompt = ('Given the code and tests given below and the trace created by the tests execute, modify the existent code so that the tests will pass.' +
                  'The answer should only contain the code and no explanation.\n' + 
                  'Code:\n ``' + self.get_code() + '``\n\n' +  
                  'Tests:\n ``' + self.get_tests() + '``\n\n' +
                  'Error trace:\n ``' + trace + '``') 

        return prompt


    def save_context(self, context, idx_file):
        filename = self.code_file

        text2save = ""
        for idx in range(len(context)):
            element = context[idx]
            text2save = text2save + "role - " + element["role"] + "\n"
            text2save = text2save + "content:\n"
            #print(element["content"])
            content = element["content"].split("\n")
            for index in range(len(content)):
                line = content[index]
                text2save = text2save + line + "\n"

            text2save = text2save + "\n\n=================================================\n\n"

        path = get_path(filename, idx_file, "txt").replace(".txt", "_context_developer.txt")

        with open(path, 'w') as file:
            file.write(text2save)



    def create_context(self):
        context = [{"role": "system", "content": self.role}]
        for idx in range(len(self.messages_sent)):
            context.append({"role": "user", "content": self.messages_sent[idx]})
            context.append({"role": "assistant", "content": self.messages_received[idx]})

        return context

    def send_message(self, idx):
        context = self.create_context()
        next_message = self.create_prompt()
       
        context.append({"role": "user", "content": next_message})

        if not self.full_context:
            context = [
                   {"role": "system", "content": self.role},
                   {"role": "user", "content": next_message}
               ]

        self.save_context(context, idx)

        if self.print_context:
            print("------ CONTEXT START -------")
            print(context)
            print("------ CONTEXT END -------")

        response = self.client.chat.completions.create(
           model="gpt-4o-mini",
           messages=context
        )

        self.messages_sent.append(next_message)
        message = response.choices[0].message.content

        path = get_path(self.code_file, idx, "txt").replace(".txt", "_response_developer.txt")
        file_opener = open(path, 'w')
        file_opener.writelines(message)
        file_opener.close()

        self.messages_received.append(message)
        self.messages_received_parsed_code.append(self._parse_message(message))

    def save_response_to_code_file(self):
        file_opener = open(self.code_file, 'w')
        complete_code = self.messages_received_parsed_code[-1]
        file_opener.writelines(complete_code)
        file_opener.close()

    def _parse_message(self, message):
        if self.print_message:
            print("------ start message")
            print(message)
            print("------   end message")

        split_message = message.split("\n")

        code = False
        result = []
        tmp = []
        for line in split_message:
            if line.startswith("```") and len(tmp) != 0:
                result.append("\n".join(tmp))
                tmp = []
                break

            if code:
                tmp.append(line)

            if line.startswith("```"):
                code = True
                tmp = []
        # print(code)

        if len(result) == 0:
            return message
        return "\n".join(result)

    def execute_tests(self, idx):
        path = get_path(self.test_file, idx)
        print(path)
        result_sub_process = subprocess.run(["python", path if idx is not None else self.test_file], stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, universal_newlines=True)
        print(result_sub_process.stderr)
        if "OK" not in result_sub_process.stderr.split("\n")[-2]:
            self.errors.append([result_sub_process.stderr])
            return TEST_FAILED
        else:
            self.errors.append(TEST_PASSED)
            return TEST_PASSED

    def get_traces_of_last_run(self):
        if self.errors[-1] == TEST_PASSED:
            return TEST_PASSED
        return "\n".join(self.errors[-1])

    def get_tests(self):
        file = open(self.test_file, 'r')
        return file.read()
    
    def get_code(self):
        file = open(self.code_file, 'r')
        return file.read()
    
    def backup_code_file(self, idx):
        shutil.copyfile(self.code_file, get_path(self.code_file, idx))

    def restore_code_file(self, idx):
        shutil.copyfile(get_path(self.code_file, idx), self.code_file)

class Runner():

    def __init__(self, test_file, code_file, full_context, print_context, print_message, max_number_repetitions):

        # Use variables
        openAI_key = os.getenv('OPEN_AI_KEY')
        self.handler = TestsBasedCoder(
            openAI_key,
            test_file,  
            code_file,
            full_context,  # send always the full context
            print_context,  # print the context
            print_message  # print the message from OpenAI
        )
        self.max_number_repetitions = max_number_repetitions
        self.skip = how_many_to_skip(code_file) + 1

    def run(self):
        result = self.handler.execute_tests(None)

        if result == TEST_PASSED:
            print("The test case is already fulfilled, the code was not modified by ChatGPT.")
            return

        counter = 0
        self.handler.backup_code_file(self.skip)
        while counter < self.max_number_repetitions:
            counter += 1
            self.handler.send_message("{}_{}".format(self.skip, counter))
            self.handler.save_response_to_code_file()
            result = self.handler.execute_tests(None)

            if result == TEST_PASSED:
                print("Test case passed! You can inspect the updated code now!")
                break
            if result == TEST_FAILED:
                print("Test failed! Resending it to ChatGPT...")

        if result == TEST_FAILED:
            self.handler.restore_code_file(self.skip)


def params():
    parser = argparse.ArgumentParser(description='Description of your program.')

    # Add arguments
    parser.add_argument('--test_file', type=str, help='Path to the file with the tests.', default='test.py')
    parser.add_argument('--code_file', type=str, help='Path to the file with the code.', default='prod.py')
    parser.add_argument('--full_context', type=str2bool, help='sending the full context to OpenAI.', default=False)
    parser.add_argument('--print_context', type=str2bool, help='Printing the context before the it is send.',
                        default=False)
    parser.add_argument('--print_message', type=str2bool, help='Printing the message received from OpenAI.',
                        default=False)
    parser.add_argument('--max_number_repetitions', type=int,
                        help='Maximum number of chances given to OpenAI for solving a test case.', default=5)

    # Parse the command-line arguments
    return parser.parse_args()


if __name__ == '__main__':
    parser = params()

    runner = Runner(
        parser.test_file,
        parser.code_file,
        parser.full_context,
        parser.print_context,
        parser.print_message,
        parser.max_number_repetitions
    )

    runner.run()