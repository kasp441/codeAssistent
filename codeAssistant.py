import autogen
from autogen.coding import DockerCommandLineCodeExecutor
import tempfile
import argparse

#config file for the assistant
config_list_llama = [
    {
        "model": "llama3.2:latest",
        "api_type": "ollama",
        "client_host": "http://localhost:11434/",
        }
        ]

#actual llm config file for the assistants
llm_config_llama= {
    "seed": 42,
    "config_list": config_list_llama,
    "temperature": 0,
}

config_list_qwen = [
    {
        "model": "qwen2.5-coder",
        "api_type": "ollama",
        "client_host": "http://localhost:11434/",
        }
        ]

#actual llm config file for the assistants
llm_config_qwen= {
    "seed": 42,
    "config_list": config_list_qwen,
    "temperature": 1,
}

def init_agent(type):
    if type == "gwen":
        return autogen.AssistantAgent(
            system_message="you are a helpful agent of which can generate python code. you have been tasked with providing python code for what is asked. when you have a working piece of code, that have been executed atleast once by the code executor. type 'TERMINATE' to end the conversation.",
            llm_config=llm_config_qwen,
            name="PythonDev"
        )
    elif type == "llama":
        return autogen.AssistantAgent(
            system_message="""
            You are a helpful agent specialized in generating Python code. Your primary task is to provide Python code based on the user's requests. Follow these steps:
            1. Understand the user's request.
            2. Generate the Python code accordingly.
            3. Ensure the code is executed at least once by the code executor.
            4. Once the code has been successfully executed, type 'TERMINATE' to end the conversation.
            
            It is crucial to terminate the conversation immediately after the code has been successfully executed to ensure efficiency and avoid redundancy.
            """,
            llm_config=llm_config_llama,
            name="PythonDev"
)


# creats a temporary directory to store the code files
temp_dir = tempfile.TemporaryDirectory()

# setup for the docker container that will serve as the llms playground
cmdexecutor = DockerCommandLineCodeExecutor(
    image="python:3.11",  # Execute code using the given docker image name.
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)

#code executor proxy agent
executer = autogen.UserProxyAgent(
    name= "code executor",
    human_input_mode="NEVER",
    llm_config=False,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"executor": cmdexecutor},
)

# main function with two arguments
def main():
    parser = argparse.ArgumentParser(description=" a simple code assistant")
    parser.add_argument('-o', '--objective', type=str, required=True, help="Objective of the code")
    parser.add_argument('-A', '--agent', type=str, required=False, help="which agent to use, gwen or llama")
    args = parser.parse_args()
    
    if args.agent == "gwen":
        coder = init_agent("gwen")
    elif args.agent == "llama":
        coder = init_agent("llama")
    else:
        coder = init_agent("llama")

    executer.initiate_chat(coder,message=f"Objective: {args.objective}")

if __name__ == "__main__":
    main()