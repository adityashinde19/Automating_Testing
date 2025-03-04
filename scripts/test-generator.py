import os
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage

def generate_test_cases(code_content, file_path):
    llm = AzureChatOpenAI(
        azure_deployment="gpt4o",
        api_version="2024-08-01-preview",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint="https://aressgenaisvc2.openai.azure.com/openai/deployments/gpt4o/chat/completions?api-version=2024-08-01-preview",
        temperature=0
    )

    prompt = f"""Generate comprehensive test cases for the following code. 
    The output should be valid Python pytest code. 
    Include edge cases and exception handling.
    Code file path: {file_path}
    Code content:
    {code_content}
    
    Return only the Python test code without any explanations or markdown formatting."""

    response = llm([HumanMessage(content=prompt)])
    return response.content

def main():
    test_dir = "tests"
    os.makedirs(test_dir, exist_ok=True)

    # Process all Python files in the project
    for root, dirs, files in os.walk("."):
        if "venv" in dirs:
            dirs.remove("venv")
        if test_dir in dirs:
            dirs.remove(test_dir)
            
        for file in files:
            if file.endswith(".py") and not file.startswith("test_"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    code_content = f.read()
                
                test_code = generate_test_cases(code_content, file_path)
                test_file = os.path.join(test_dir, f"test_{file}")
                
                with open(test_file, "w") as f:
                    f.write(f"# Auto-generated tests for {file_path}\n\n")
                    f.write(test_code)
                print(f"Generated tests for {file_path}")

if __name__ == "__main__":
    main()
