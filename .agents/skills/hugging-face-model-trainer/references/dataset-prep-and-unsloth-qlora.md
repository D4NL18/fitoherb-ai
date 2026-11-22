# Preparação de Datasets e Fine-Tuning QLoRA 4-bit com Unsloth

## 1. Pipeline de Preparação de Dados (4 Etapas)

### Etapa 1 e 2: Coleta Estruturada (Web Scraping Ético)
Respeite termos de serviço, `robots.txt` e direitos autorais. Deduplique URLs com `set()` e isole seletores HTML:
```python
import json
import requests
from bs4 import BeautifulSoup

def extrair_artigo(url: str) -> str:
    resp = requests.get(url, timeout=15)
    if resp.status_code != 200:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    container = soup.find("div", class_="article__content")
    if not container:
        return ""
    paragraphs = container.find_all("p", class_="paragraph inline-placeholder")
    return " ".join(p.get_text(strip=True) for p in paragraphs)
```

### Etapa 3: Rotulagem Sintética com LLM (JSON Mode)
Automatiza a geração de pares `(entrada, saída esperada)` com validação estrita via `json.loads`:
```python
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_resumo_sintetico(story: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": 'Summarize the news article and return JSON: {"summary": "..."}'},
            {"role": "user", "content": f"{story}\n###"},
        ],
        temperature=0.3,
        max_tokens=128,
    )
    payload = json.loads(resp.choices[0].message.content)
    return payload["summary"].strip()
```

### Etapa 4: Unificação com Dataset Complementar (Hugging Face) e Formatação Alpaca
Combine dados próprios com datasets públicos (ex.: `glnmario/news-qa-summarization`) em formato padronizado com `EOS_TOKEN`:
```python
ALPACA_PROMPT = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

def formatar_para_sft(examples, eos_token: str):
    texts = [
        ALPACA_PROMPT.format(inst, inp, out) + eos_token
        for inst, inp, out in zip(examples["instruction"], examples["input"], examples["output"])
    ]
    return {"text": texts}
```

---

## 2. Fundamentos: Full Fine-Tuning vs PEFT / LoRA + Quantização 4-bit
- **Full Fine-Tuning:** O *Optimizer State (32-bit)* atualiza todos os pesos do *Base Model (16-bit)*, exigindo altíssima VRAM e risco maior de *Catastrophic Forgetting*.
- **QLoRA (4-bit + LoRA):** Quantiza o modelo base congelado em 4 bits e treina apenas matrizes adaptadoras de baixo posto (`r=16`, `lora_alpha=16`) nas projeções de atenção e MLP (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`), reduzindo drasticamente o consumo de memória.

---

## 3. Script Completo: Unsloth + Llama-3-8B 4-bit + `SFTTrainer` + `TextStreamer`

```python
from datasets import load_dataset
from transformers import TextStreamer, TrainingArguments
from trl import SFTTrainer
from unsloth import FastLanguageModel, is_bfloat16_supported

MAX_SEQ_LENGTH = 2048

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

dataset = load_dataset("json", data_files="dataset_sft.json", split="train")
dataset = dataset.map(lambda ex: formatar_para_sft(ex, tokenizer.eos_token), batched=True)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,
        learning_rate=2e-4,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
    ),
)

trainer.train()

# Inferência otimizada em streaming
FastLanguageModel.for_inference(model)
inputs = tokenizer(
    [ALPACA_PROMPT.format("SUMMARIZE THIS NEWS", "Texto da notícia...", "")],
    return_tensors="pt",
).to("cuda")
_ = model.generate(**inputs, streamer=TextStreamer(tokenizer), max_new_tokens=128)

# Persistência dos adaptadores LoRA
model.save_pretrained("lora_model")
tokenizer.save_pretrained("lora_model")
```
