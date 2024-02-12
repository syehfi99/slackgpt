import re
import openai
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

def reformat_text_by_chatgpt(teks):
    result = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    temperature=1,
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "rapihkan teks ini, pertahankan bahasa indonesia \n " + teks},
        ]
    )
    # print(result["choices"][0]["message"]["content"], flush=True)
    return result["choices"][0]["message"]["content"]