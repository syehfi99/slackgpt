import re
def reformat_text(text):
    # Remove extra whitespaces and newlines
    text = re.sub(r'\s+', ' ', text.strip())

    # Replace special characters to make the text look cleaner
    text = text.replace('.\n', '. ')
    text = text.replace(':\n', ': ')
    text = text.replace('.,', '.')
    text = text.replace('.,', '.')
    text = text.replace(',.', '.')
    return text