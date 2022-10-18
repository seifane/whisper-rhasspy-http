from bottle import route, run, request
import os, random, string, argparse
import whisper

parser = argparse.ArgumentParser(description="Whisper integration for Rhasspy")
parser.add_argument('--host', type=str, help="Bind address of the http server", default="0.0.0.0")
parser.add_argument('--port', type=int, help="Port of the http server", default=4444)
parser.add_argument('--filter-chars', type=str, help="Remove specific characters from the recognized text", default=None)
parser.add_argument('--whisper-model', type=str, help="Whisper model to use", default="base")

args = parser.parse_args()

print(args)

model = whisper.load_model(args.whisper_model)


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def clean_text(text: str) -> str:
    text = text.strip()
    if args.filter_chars is not None:
        text = text.translate(dict.fromkeys(map(ord, args.filter_chars), None))
    return text

@route('/api/text-to-speech', method='POST')
def api_text_to_speech():
    data = request.body.read()
    filename = get_random_string(20) + ".wav"

    f = open(filename, "wb")
    f.write(data)
    f.close()

    result = model.transcribe(filename)

    os.remove(filename)

    print(result)
    cleaned_text = clean_text(result['text'])
    print("Clean text:")
    print(cleaned_text)
    res = {
        "text": cleaned_text,
        "likelihood": 1.0,
        "transcribe_seconds": 2,
        "wav_seconds": 2,
    }
    return res


run(host=args.host, port=args.port)
