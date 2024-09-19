class TextFormatter:
    def __init__(self):
        self.line_width = 0

    def set_line_width(self, width):
        self.line_width = width
        
    def center_word(self, word):
        total_space = self.line_width - len(word)
        left_space = total_space // 2
        right_space = total_space - left_space
        return ' ' * left_space + word + ' ' * right_space