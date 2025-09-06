from openai import OpenAI
from .testtest import output_1, output_2

def openai_test(config):
    client = OpenAI(
        base_url = config.base_url,
        api_key = config.api_key,
    )

    response = client.chat.completions.create(
    model=config.model,
    reasoning_effort="high",
    messages=[
        {"role": "system", "content": "Du bist ein Geschichtenerzähler für eine Zombie Apokalypse. Die Antworten nur in deutsch."},
        {"role": "user", "content": "Erzähl mir den start einer geschichte (maximal 200 Wörter) bei der sich 4 Charaktere in einer Stadt namens Louisville treffen und beschließen eine gemeinschaft zu bilden."},
        {"role": "assistant", "content": output_1},
        {"role": "user", "content": "Erzähl mir wie es weitergeht (maximal 200 Wörter) ein teil soll sein: Noah trauert seiner Familie nach."},
        {"role": "assistant", "content": output_2},
        {"role": "user", "content": f"Schreibe diesen Teil \n>{output_2}\n der Geschichte in die \"Ich\" Perspektive von Noah um (maximal 200 Wörter). Gehe mehr auf Noah ein und vernachlässige die anderen."},
    ]
    )
    print(f"Used model: {response.model}")
    print(response.choices[0].message.content)
