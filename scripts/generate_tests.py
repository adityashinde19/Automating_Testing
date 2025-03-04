import os
import openai
import glob

def generate_tests():
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2023-12-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
    # Get all source code files
    source_files = glob.glob('app/**/*.py', recursive=True)
    
    # Read and concatenate source code
    source_code = ""
    for file in source_files:
        with open(file, 'r') as f:
            source_code += f"\n\n# File: {file}\n{f.read()}"
    
    # Truncate to fit context window
    source_code = source_code[:12000]  # Adjust based on model context window
    
    # Generate tests using Azure OpenAI
    response = client.chat.completions.create(
        model="gpt4o",  # Use your deployed model name
        messages=[
            {"role": "system", "content": "You are a senior QA engineer. Generate comprehensive test cases in Python using pytest format."},
            {"role": "user", "content": f"Generate pytest test cases for this code:\n{source_code}\n\nOutput only the test code with no explanations."}
        ],
        temperature=0.2,
        max_tokens=2000
    )
    
    # Save generated tests
    test_code = response.choices[0].message.content
    with open('tests/test_generated.py', 'w') as f:
        f.write(test_code)
    
    print("Test generation completed")

if __name__ == "__main__":
    generate_tests()
