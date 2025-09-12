from openai import OpenAI
from .testtest import output_21, output_22
from .db import get_characters_from_ids

async def openai_test(config):
    chars = await get_characters_from_ids(config, [1, 2, 3, 4])
    client = OpenAI(
        base_url = config.env.base_url,
        api_key = config.env.api_key,
    )

    response = client.chat.completions.create(
    model=config.env.model,
    reasoning_effort="high",
    messages=[
        # Test 1
        # Du bist ein Geschichtenerzähler für eine Zombie Apokalypse. Die Antworten nur in deutsch.
        # {"role": "system", "content": "Du bist ein Geschichtenerzähler für eine Zombie Apokalypse. Die Antworten nur in deutsch."},
        # {"role": "user", "content": "Erzähl mir den start einer geschichte (maximal 200 Wörter) bei der sich 4 Charaktere in einer Stadt namens Louisville treffen und beschließen eine gemeinschaft zu bilden."},
        # {"role": "assistant", "content": output_1},
        # {"role": "user", "content": "Erzähl mir wie es weitergeht (maximal 200 Wörter) ein teil soll sein: Noah trauert seiner Familie nach."},
        # {"role": "assistant", "content": output_2},
        # {"role": "user", "content": f"Schreibe diesen Teil \n>{output_2}\n der Geschichte in die \"Ich\" Perspektive von Noah um (maximal 200 Wörter). Gehe mehr auf Noah ein und vernachlässige die anderen."},
        # Test 2
                # Du bist ein Geschichtenerzähler für eine Zombie Apokalypse. Die Antworten nur in deutsch. Mit dem 
        # Erzählstil: Epistolare Roman und einer dunklen Stimmung.
        # {"role": "system", "content": "Du bist ein Geschichtenerzähler für eine Zombie Apokalypse. Schreibe ausschießlich auf english. Der Erzählstil sollte: Epistolare Roman sein und die allgemeine Stimmung: dark"},
        # {"role": "user", "content": "Erzähl mir den start einer geschichte (maximal 200 Wörter) bei der sich 4 Charaktere in einer Stadt namens Louisville treffen und beschließen eine gemeinschaft zu bilden."},
        # {"role": "assistant", "content": output_21},
        # {"role": "user", "content": "Erzähl mir wie es weitergeht (maximal 200 Wörter) ein teil soll sein: Elias wurde am Bein verletzt."}, # Mod hat im Textinput angegeben, dass Elias sich am Bein verletzt hat
        # {"role": "assistant", "content": output_22},
        # {"role": "user", "content": "Erzähl mir wie es weitergeht (maximal 200 Wörter) ein teil soll sein: Aufbruch"}, # Mod hat im Textinput nichts angegeben, Inspirierendes Wort wird zufällig ausgewählt: Aufbruch
        # Test 3
        {"role": "system", "content": "Du bist ein Geschichtenerzähler für eine Zombie Apokalypse. Schreibe ausschießlich auf deutsch. Der Erzählstil sollte: Epistolare Roman sein und die allgemeine Stimmung: dark"},
        {"role": "user", "content": "Beschreibe mir die welt in der die Menschen jetzt leben müssen mit (maximal 200 Wörter)"},
        {"role": "user", "content": "Erzähl mir den start einer geschichte (maximal 600 Wörter) bei der sich 4 Charaktere in einer Stadt namens Louisville treffen und beschließen eine gemeinschaft zu bilden."}, # --> Muss beim erstellen des Spiels eingegeben werden.
        # {"role": "user", "content": f"Der erste Charaktere: {chars[0].description}"},
        # {"role": "user", "content": f"Der zweiter Charaktere: {chars[1].description}"},
        # {"role": "user", "content": f"Der dritter Charaktere: {chars[2].description}"},
        # {"role": "user", "content": f"Der vierter Charaktere: {chars[3].description}"},
    ]
    )
    print(f"Used model: {response.model}")
    print(response.choices[0].message.content)
