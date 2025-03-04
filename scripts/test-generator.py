import os
import glob
import re
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage
import json
import time

# Initialize Azure OpenAI
llm = AzureChatOpenAI(
    azure_deployment="gpt4o",
    api_version="2024-08-01-preview",
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    temperature=0
)

def get_all_code_files(folder_path='.', extensions=('.py',), exclude_patterns=('test_*.py', '*_test.py', 'venv/*', '.*/*', 'scripts/*')):
    all_files = []
    
    for ext in extensions:
        pattern = f"{folder_path}/**/*{ext}"
        files = glob.glob(pattern, recursive=True)
        
        # Filter out excluded patterns
        for file_path in files:
            should_exclude = False
            for exclude in exclude_patterns:
                if re.match(f".*{exclude.replace('*', '.*')}$", file_path):
                    should_exclude = True
                    break
            
            if not should_exclude:
                all_files.append(file_path)
                
    return all_files

def generate_test_for_file(file_path):
    with open(file_path, 'r') as f:
        file_content = f.read()
    
    # Extract filename without extension for the test name
    file_name = os.path.basename(file_path)
    base_name, ext = os.path.splitext(file_name)
    test_file_name = f"test_{base_name}{ext}"
    
    # Path for the test file, putting it in the same directory as the original file
    test_file_path = os.path.join(os.path.dirname(file_path), test_file_name)
    
    prompt = f"""
    You are an expert test writer. I need you to generate comprehensive pytest test cases for this code:
    
    ```
    {file_content}
    ```
    
    Please generate thorough test cases that:
    1. Cover all functions and methods
    2. Test edge cases and error conditions
    3. Achieve high code coverage
    4. Use pytest fixtures when appropriate
    5. Include docstrings explaining test purposes
    
    Return only valid Python code for the test file without any explanations or formatting.
    """
    
    # Generate the test content using Azure OpenAI
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    test_content = response.content
    
    # Clean up the response to extract just the code
    if "```python" in test_content:
        test_content = test_content.split("```python")[1].split("```")[0].strip()
    elif "```" in test_content:
        test_content = test_content.split("```")[1].split("```")[0].strip()
    
    # Write the test file
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    return test_file_path

def main():
    # Identify all Python files in the project
    code_files = get_all_code_files(extensions=('.py',))
    
    print(f"Found {len(code_files)} Python files to generate tests for")
    
    # Generate tests for each file
    generated_tests = []
    for file_path in code_files:
        print(f"Generating tests for {file_path}")
        try:
            test_path = generate_test_for_file(file_path)
            generated_tests.append(test_path)
            print(f"✅ Generated test file: {test_path}")
        except Exception as e:
            print(f"❌ Failed to generate test for {file_path}: {str(e)}")
    
    print(f"Successfully generated {len(generated_tests)} test files")
    
    # Write a summary of generated tests
    summary = {
        "total_files_analyzed": len(code_files),
        "tests_generated": len(generated_tests),
        "test_files": generated_tests
    }
    
    with open('test_generation_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("Test generation complete!")

if __name__ == "__main__":
    main()
