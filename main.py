from bottle import route, run, request
import os, random, string, argparse
import whisper
import re

parser = argparse.ArgumentParser(description="Whisper integration for Rhasspy")
parser.add_argument('--host', type=str, help="Bind address of the http server", default="0.0.0.0")
parser.add_argument('--port', type=int, help="Port of the http server", default=4444)
parser.add_argument('--filter-chars', type=str, help="Remove specific characters from the recognized text", default=None)
parser.add_argument('--whisper-model', type=str, help="Whisper model to use", default="base")

args = parser.parse_args()

print(args)

model = whisper.load_model(args.whisper_model)

def transform_hint_phrases_line(line):
    # If line contains brackets, remove the line
    if '[' in line or ']' in line:
        return None

    # Check if line contains a range of integers (a..b){Value!int}
    match = re.search(r'\((\d+)\.\.(\d+)\)\{Value!int\}', line)
    if match:
        start, end = map(int, match.groups())
        # Replace the range with each integer in the range
        options = [re.sub(r'\(\d+\.\.\d+\)\{Value!int\}', str(i), line) for i in range(start, end+1)]
    else:
        # Split options marked with pipes
        options = line.split('|')

    # Return transformed options
    return options

# Function to read hint_phrases from a file
def read_hint_phrases(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
        # Split the data by parentheses and pipe symbol
        hint_phrases = [item.strip() for item in data.split('\n') if item.strip() != '']

    return hint_phrases

# Read your hint phrases from a file
hint_phrases = read_hint_phrases("/app/hint_phrases.txt")

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def clean_text(text: str) -> str:
    text = text.strip()
    if args.filter_chars is not None:
        text = text.translate(dict.fromkeys(map(ord, args.filter_chars), None))
    return text

@route('/api/speech-to-text', method='POST')
def api_text_to_speech():
    data = request.body.read()
    filename = get_random_string(20) + ".wav"

    f = open(filename, "wb")
    f.write(data)
    f.close()

    max_attempts = 5
    for attempt in range(max_attempts):
        result = model.transcribe(filename, initial_prompt=' '.join(hint_phrases))
        processed_text = clean_text(result['text'])
        if processed_text:
            break

    os.remove(filename)

    print(result)
    cleaned_text = clean_text(result['text'])
    
    # Post-processing: Check if the transcribed text is in hint_phrases
    if cleaned_text not in hint_phrases:
        cleaned_text = ''

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
