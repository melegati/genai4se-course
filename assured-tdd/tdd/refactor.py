import os
import argparse
from tdd.DeveloperAIHandler import DeveloperAIHandler, TEST_PASSED, TEST_FAILED
from tdd.utils import str2bool, how_many_to_skip

class RefactorRunner():

    def __init__(self, test_file, code_file, full_context, print_context, print_message, max_number_repetitions, logs_folder):

        self.handler = DeveloperAIHandler(
            test_file,  
            code_file,
            full_context,  # send always the full context
            print_context,  # print the context
            print_message,  # print the message from OpenAI
            logs_folder
        )
        self.max_number_repetitions = max_number_repetitions
        self.skip = how_many_to_skip(code_file, logs_folder) + 1

    def create_refactor_prompt(self):
        
        prompt = ('```python \n' +
                  self.handler.get_code() +
                  '```\n' + 
                  'Refactor the provided Python method to enhance its readability and maintainability.' + 
                  'You can assume that the given method is functionally correct. Ensure that you do not ' + 
                  'alter the external behavior of the method, maintaining both syntatic and semantic correctness.' +
                  'Provide the Python method within a code block. Avoid using natural language explanations.')

        return prompt 

    def run(self):
        result = self.handler.execute_tests()

        if result != TEST_PASSED:
            print("The test cases are failing, please fix the code before asking to refactor it.")
            return
        
        counter = 0
        starting_complexity = self.handler.calculate_cyclomatic_complexity()
        self.handler.backup_code_file(self.skip)
        while counter < self.max_number_repetitions:
            counter += 1
            self.handler.send_message(self.create_refactor_prompt(), "{}_{}".format(self.skip, counter))
            self.handler.save_response_to_code_file()
            result = self.handler.execute_tests()

            if result == TEST_PASSED:
                print("Test case passed!Checking complexity now!")
                current_complexity = self.handler.calculate_cyclomatic_complexity()
                if current_complexity < starting_complexity:
                    print("Complexity decreased from {} to {}. Done.".format(starting_complexity, current_complexity))
                    return
                else:
                    print("Complexity increased from {} to {}. Retrying.".format(starting_complexity, current_complexity))
                    self.handler.restore_code_file(self.skip)
            if result == TEST_FAILED:
                print("Test failed! Resending it to ChatGPT...")

        self.handler.restore_code_file(self.skip)


def params():
    parser = argparse.ArgumentParser(description='Description of your program.')

    # Add arguments
    parser.add_argument('-t', '--test_file', type=str, help='Path to the file with the tests.', default='test.py')
    parser.add_argument('-c', '--code_file', type=str, help='Path to the file with the code.', default='code.py')
    parser.add_argument('--full_context', type=str2bool, help='Sending the full context to OpenAI.', default=False)
    parser.add_argument('--print_context', type=str2bool, help='Printing the context before the it is send.',
                        default=False)
    parser.add_argument('--print_message', type=str2bool, help='Printing the message received from OpenAI.',
                        default=False)
    parser.add_argument('--max_number_repetitions', type=int,
                        help='Maximum number of chances given to OpenAI for solving a test case.', default=5)
    parser.add_argument('--logs_folder', type=str, help='Folder to save the logs.', default='logs_refactor')

    # Parse the command-line arguments
    return parser.parse_args()


if __name__ == '__main__':
    parser = params()

    runner = RefactorRunner(
        parser.test_file,
        parser.code_file,
        parser.full_context,
        parser.print_context,
        parser.print_message,
        parser.max_number_repetitions,
        parser.logs_folder
    )

    runner.run()