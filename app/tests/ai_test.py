import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.ai_process.text_generator import generate_text

def test_generate_text():
    prompt = "Hello!"
    response = generate_text(prompt)
    print(response)

if __name__ == "__main__":
    test_generate_text()
