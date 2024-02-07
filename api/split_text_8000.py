import tiktoken
def split_text_8000(text, max_tokens):
    tokens = tiktoken.tokenize(text)
    if len(tokens) <= max_tokens:
        return [text]
    else:
        split_texts = []
        current_text = ""
        current_tokens = 0
        for token in tokens:
            if current_tokens + token.count(" ") <= max_tokens:
                current_text += token
                current_tokens += token.count(" ")
            else:
                split_texts.append(current_text)
                current_text = token
                current_tokens = token.count(" ")
        split_texts.append(current_text)
        return split_texts