import tiktoken

from api.reformat_text import reformat_text

def split_text_8000(text, max_tokens, embedding_encoding):
    encoding = tiktoken.get_encoding(embedding_encoding)
    tokens = encoding.encode(text)
    # print('tokens awal:', len(tokens), flush=True)
    if len(tokens) <= max_tokens:
        return [text]
    else:
        split_texts = []
        current_text = ""
        current_tokens = 0
        for token in tokens:
            token_str = encoding.decode([token])
            # token_str = reformat_text(token_str)
            if current_tokens + token_str.count(" ") <= max_tokens:
                current_text += token_str
                current_tokens += token_str.count(" ") + 1
            else:
                if current_tokens > max_tokens:
                    split_texts.append(current_text[:max_tokens])
                    split_texts.append(current_text[max_tokens:])
                else:
                    split_texts.append(current_text)
                current_text = token_str
                current_tokens = token_str.count(" ") + 1
        split_texts.append(current_text)
        return split_texts