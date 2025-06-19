# GENAI-RAG-Due-Dilligence
A generative AI notebook project which includes web scraping of financial institutes annual report and  perform RAG over it, which in result gives the answers to all questions based on the report injected in vectorDB.
Along with it provinding system prompts with additional informations like credit worthiness rules, financial analysis guides, financial red and green flags . These help LLM to understand and return the answers under these info scopes.




Add .env file to run this project

LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=notebook-due-dilligence
OPENAI_API_KEY=

