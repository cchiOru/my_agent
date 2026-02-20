#path: main.py
from dotenv import load_dotenv
load_dotenv()
from myagent.agent import root_agent

def main():
    user_input = {
        "ingredients": ["egg", "rice", "soy sauce"]
    }

    response = root_agent.run(user_input)
    print(response)

if __name__ == "__main__":
    main()
