



# LLM FastAPI Scaffold

Starter scaffold for a FastAPI-based LLM gateway/orchestration backend.



llm-fastapi-scaffold/
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
├── scripts/
│   └── run.sh
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── router.py
│   │       ├── routes_chat.py
│   │       └── routes_models.py
│   ├── core/
│   │   └── config.py
│   ├── schemas/
│   │   ├── chat.py
│   │   └── model.py
│   ├── providers/
│   │   ├── base.py
│   │   └── ollama_provider.py
│   ├── routing/
│   │   └── rules.py
│   └── services/
│       └── orchestrator.py
└── tests/
    └── api/
        ├── test_health.py
        └── test_models.py



this is the final version

app/
  api/
    routes_chat.py
    routes_models.py
    routes_admin.py
  schemas/
    chat.py
    model.py
  services/
    orchestrator.py
    prompt_builder.py
    guardrails.py
  providers/
    base.py
    ollama_provider.py
    vllm_provider.py
    openai_provider.py
    anthropic_provider.py
  routing/
    rules.py
    cost_router.py
    fallback.py
  core/
    config.py
    auth.py
    logging.py
    metrics.py
  storage/
    db.py
    usage_repo.py



python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
chmod +x scripts/run.sh
./scripts/run.sh

--------------

# FOR Front end user 


async function streamChat() {
  const response = await fetch("http://localhost:8000/api/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      provider: "ollama",
      model: "llama3.2:latest",
      messages: [
        { role: "user", content: "Write a short paragraph about Punjab." }
      ],
      stream: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let fullText = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split("\n");

    for (const line of lines) {
      if (line.startsWith(" ")) {
        const text = line.replace(" ", "");
        if (text === "[DONE]") {
          console.log("Stream finished");
          continue;
        }
        fullText += text;
        console.log(fullText);
      }
    }
  }
}










---------------

# for RAG

app/
  api/
    routes_chat.py
    routes_ingest.py
  schemas/
    chat.py
    rag.py
  services/
    orchestrator.py
    rag_service.py
    ingest_service.py
    prompt_builder.py
  providers/
    ollama_provider.py
    openai_provider.py
    anthropic_provider.py
    embedding_provider.py
  vectorstores/
    base.py
    pgvector_store.py
  repositories/
    document_repo.py
  core/
    config.py
