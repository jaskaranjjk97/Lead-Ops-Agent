from app import config
from app.llm import get_llm


def main():
    print("Config loaded.")
    print(f"  OPENAI_MODEL: {config.OPENAI_MODEL}")
    print(f"  CRM_FILE: {config.CRM_FILE}")
    print(f"  ICP_FILE: {config.ICP_FILE}")

    llm = get_llm(temperature=0.2)
    print(f"  LLM initialized: {llm.model_name}")
    print("Setup OK")


if __name__ == "__main__":
    main()
