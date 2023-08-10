from db import (
    readPromptCollection,
)


# generate all exist prompt button
def generateAllPromptButton():
    startingData = readPromptCollection()

    buttons = []
    for data in startingData["prompt_name"]:
        buttons.append(
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": data.upper(),
                },
                "value": data,
                "action_id": data,
            },
        )

    blocks = [{"type": "actions", "elements": buttons}]
    return blocks


# generate prompt button by props dataPrompt
# key: prompt 1
# prompt: buatkan blak dwodkwaodka wdowa od aowdo


def generateRadioPrompt(dataPrompt):
    options = []
    for data in dataPrompt["prompts"]:
        option = {
            "text": {
                "type": "plain_text",
                "text": data["key"].upper(),
                "emoji": True,
            },
            "value": data["key"],
        }
        options.append(option)

    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Pilih Prompt"},
            "accessory": {
                "type": "radio_buttons",
                "options": options,
                "action_id": "radio_pilih_prompt",
            },
        },
        {"type": "divider"},
        {
            "dispatch_action": True,
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": "keyword_input",
            },
            "label": {
                "type": "plain_text",
                "text": "Masukkan keyword anda",
                "emoji": True,
            },
        },
    ]
    return blocks


def generateSelectPromptPrivate(dataPrompt, key):
    options = []
    for data in dataPrompt["prompts"]:
        option = {
            "text": {
                "type": "plain_text",
                "text": data["key"].upper(),
                "emoji": True,
            },
            "value": f"{key} {data['key']}",
        }
        options.append(option)

    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"Pilih Prompt {key.upper()}"},
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Pilih prompt tersedia",
                    "emoji": True,
                },
                "options": options,
                "action_id": "select_pilih_prompt",
            },
        },
        {"type": "divider"},
        {
            "dispatch_action": True,
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": "keyword_input_private",
            },
            "label": {
                "type": "plain_text",
                "text": "Masukkan keyword anda",
                "emoji": True,
            },
        },
    ]
    return blocks


def generateSelectPrompt(dataPrompt):
    options = []
    for data in dataPrompt["prompts"]:
        option = {
            "text": {
                "type": "plain_text",
                "text": data["key"].upper(),
                "emoji": True,
            },
            "value": data["key"],
        }
        options.append(option)

    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Pilih Prompt"},
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Pilih prompt tersedia",
                    "emoji": True,
                },
                "options": options,
                "action_id": "select_pilih_prompt",
            },
        },
        {"type": "divider"},
        {
            "dispatch_action": True,
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": "keyword_input",
            },
            "label": {
                "type": "plain_text",
                "text": "Masukkan keyword anda",
                "emoji": True,
            },
        },
    ]
    return blocks


def generateAddPromptByChannelName(channel_name):
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Tambah Prompt Channel {channel_name.upper()}",
                "emoji": True,
            },
        },
        {
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "action_id": "prompt_key",
            },
            "label": {"type": "plain_text", "text": "Key", "emoji": True},
        },
        {
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": "prompt_value",
            },
            "label": {"type": "plain_text", "text": "Prompt", "emoji": True},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Contoh penggunaan:\nkey: `10 step membuat donat`\n prompt: `buatkan 10 step membuat donat enak dengan bahan sederhana di rumah [keyword]`",
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Submit", "emoji": True},
                "value": "click_me_123",
                "action_id": "action_add_prompt",
            },
        },
    ]
    return blocks


# generate prompt button by props dataPrompt
def generateUpdatePromptByKey(dataPrompt, channel_name):
    options = []
    for data in dataPrompt["prompts"]:
        option = {
            "text": {
                "type": "plain_text",
                "text": data["key"].upper(),
                "emoji": True,
            },
            "value": data["prompt"],
        }
        options.append(option)

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Update Prompt Channel {channel_name.upper()}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Pilih Prompt Key"},
            "accessory": {
                "type": "static_select",
                "options": options,
                "action_id": "select_key",
            },
        },
        {"type": "divider"},
        {
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "action_id": "prompt_key",
            },
            "label": {
                "type": "plain_text",
                "text": "Key (isi untuk ubah key name)",
                "emoji": True,
            },
        },
        {
            "dispatch_action": True,
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": "keyword_update_prompt",
            },
            "label": {
                "type": "plain_text",
                "text": "Masukkan update prompt",
                "emoji": True,
            },
        },
    ]
    return blocks


def generateDeletePrompt(dataPrompt, channel_name):
    options = []
    for data in dataPrompt["prompts"]:
        option = {
            "text": {
                "type": "plain_text",
                "text": data["key"].upper(),
                "emoji": True,
            },
            "value": data["prompt"],
        }
        options.append(option)

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Delete Prompt Channel {channel_name.upper()}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Pilih Prompt Key"},
            "accessory": {
                "type": "static_select",
                "options": options,
                "action_id": "select_key",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Pilih key untuk menghapus prompt",
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Hapus", "emoji": True},
                "value": "click_me_123",
                "action_id": "action_delete_prompt",
            },
        },
    ]
    return blocks


def generateImageBlocks(image_url, text):
    blocks =  [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": f"_{text}_"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Unduh",
					"emoji": True
				},
				"value": f"{image_url}",
                "url": f"{image_url}",
				"action_id": "download_image"
			}
		},
		{
			"type": "image",
			"image_url": f"{image_url}",
			"alt_text": f"{text}"
		}
	]

    return blocks
