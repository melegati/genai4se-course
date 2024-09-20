from openai import OpenAI
import subprocess
import shutil
import lizard

TEST_PASSED = "TEST_PASSED"
TEST_FAILED = "TEST_FAILED"
TEST_PASSED_WITHOUT_AI = "TEST_PASSED_WITHOUT_AI"

def get_path(filename, idx, filetype="py"):
    return "{}.{}".format(filename.replace(".py", "")+"_"+str(idx), filetype)

class DeveloperAIHandler:

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

    def create_tdd_prompt(self):
        trace = self.get_traces_of_last_run()
        if trace == TEST_PASSED:
            return TEST_PASSED
        
        prompt = ('Given the code and tests below and the trace created by the tests execution, modify the existent code so that the tests will pass.' +
                  'The answer should only contain the code and no explanation.\n' + 
                  'Code:\n ``' + self.get_code() + '``\n\n' +  
                  'Tests:\n ``' + self.get_tests() + '``\n\n' +
                  'Error trace:\n ``' + trace + '``') 

        return prompt

    def create_refactor_prompt(self):
        
        prompt = ('```python \n' +
                  self.get_code() +
                  '```\n' + 
                  'Refactor the provided Python method to enhance its readability and maintainability.' + 
                  'You can assume that the given method is functionally correct. Ensure that you do not ' + 
                  'alter the external behavior of the method, maintaining both syntatic and semantic correctness.' +
                  'Provide the Python method within a code block. Avoid using natural language explanations.')

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

    def send_message(self, message, idx):
        context = self.create_context()
       
        context.append({"role": "user", "content": message})

        if not self.full_context:
            context = [
                   {"role": "system", "content": self.role},
                   {"role": "user", "content": message}
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

        self.messages_sent.append(message)
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

    def execute_tests(self):
        result_sub_process = subprocess.run(["python", self.test_file], stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE, universal_newlines=True)
        print(result_sub_process.stderr)
        if "OK" not in result_sub_process.stderr.split("\n")[-2]:
            self.errors.append([result_sub_process.stderr])
            return TEST_FAILED
        else:
            self.errors.append(TEST_PASSED)
            return TEST_PASSED
        
    def calculate_cyclomatic_complexity(self):
        result = lizard.analyze_file(self.code_file)
        return sum([f.cyclomatic_complexity for f in result.function_list])

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