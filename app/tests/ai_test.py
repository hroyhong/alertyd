import sys
import os
import json
import re


# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.ai_process.text_generator import generate_text
from app.tests.fetch_combined_test import get_first_fetched_content

def read_prompt_template():
    template_path = os.path.join(project_root, 'prompt_template.txt')
    with open(template_path, 'r') as file:
        return file.read()

def test_generate_text():
    base_prompt = read_prompt_template()
    
    fetched_data = get_first_fetched_content()
    
    if fetched_data:
        title = fetched_data['title']
        content = fetched_data['content'][:500]  # Limit content to 500 characters
        url = fetched_data['link']
        prompt = base_prompt.format(title=title, content=content, link=url)
    else:
        print("Warning: No content fetched. Using placeholder values.")
        prompt = base_prompt.format(title="[No title available]", content="[No content available]", url="[No URL available]")

    print("Prompt:")
    print(prompt)
    print("Prompt type:", type(prompt))
    
    response = generate_text(prompt)
    print("\nGenerated text:")
    print(response)
    
    return response, url

def add_href_to_website(content, url):
    # Find the Website line and add the href
    website_pattern = r'(Website: )(.+)'
    return re.sub(website_pattern, f'\\1<a href="{url}">\\2</a>', content)

if __name__ == "__main__":
    response, url = test_generate_text()
    
    # Parse the JSON response
    response_json = json.loads(response)
    
    # Extract the content
    content = response_json['choices'][0]['message']['content']
    
    # Add href to the Website line
    content_with_href = add_href_to_website(content, url)
    
    # Create the directory if it doesn't exist
    output_dir = os.path.join(project_root, 'app', 'tests', 'generated_text')
    os.makedirs(output_dir, exist_ok=True)
    
    # Write the content with href to a file
    output_file = os.path.join(output_dir, 'test.txt')
    with open(output_file, 'w') as f:
        f.write(content_with_href)
    
    print(f"\nContent with href has been written to {output_file}")