---
name: hugging-face-model-trainer
description: "Use quando a tarefa envolver: Train or fine-tune language and vision models using TRL (Transformer Reinforcement Learning) or Unsloth with Hugging Face Jobs infrastructure. Covers SFT, DPO, GRPO and reward modeling training methods, plus GGUF conversion for local deployment."
risk: critical
source: https://github.com/huggingface/skills/tree/main/skills/huggingface-llm-trainer
source_repo: huggingface/skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/huggingface/skills/blob/main/LICENSE
---

# TRL Training on Hugging Face Jobs

## Detailed Guide

Read [the detailed guide](references/detailed-guide.md) before executing this skill. It retains the complete procedure and reference material. Treat its safety, prerequisites, and validation requirements as mandatory. For focused work, load the relevant sections; for end-to-end work, read the guide completely.

## When to Use This Skill

Use this skill when users want to:
- Fine-tune language models on cloud GPUs without local infrastructure
- Train with TRL methods (SFT, DPO, GRPO, etc.)
- Run training jobs on Hugging Face Jobs infrastructure
- Convert trained models to GGUF for local deployment (Ollama, LM Studio, llama.cpp)
- Ensure trained models are permanently saved to the Hub
- Use modern workflows with optimized defaults

### When to Use Unsloth

Use **Unsloth** (`references/unsloth.md`) instead of standard TRL when:
- **Limited GPU memory** - Unsloth uses ~60% less VRAM
- **Speed matters** - Unsloth is ~2x faster
- Training **large models (>13B)** - memory efficiency is critical
- Training **Vision-Language Models (VLMs)** - Unsloth has `FastVisionModel` support

See `references/unsloth.md` for complete Unsloth documentation and `scripts/unsloth_sft_example.py` for a production-ready training script.

## Prerequisites Checklist

Before starting any training job, verify:

### ✅ **Account & Authentication**
- Hugging Face Account with [Pro](https://hf.co/pro), [Team](https://hf.co/enterprise), or [Enterprise](https://hf.co/enterprise) plan (Jobs require paid plan)
- Authenticated login: Check with `hf_whoami()`
- **HF_TOKEN for Hub Push** ⚠️ CRITICAL - Training environment is ephemeral, must push to Hub or ALL training results are lost
- Token must have write permissions
- **MUST pass `secrets={"HF_TOKEN": "$HF_TOKEN"}` in job config** to make token available (the `$HF_TOKEN` syntax
  references your actual token value)

### ✅ **Dataset Requirements**
- Dataset must exist on Hub or be loadable via `datasets.load_dataset()`
- Format must match training method (SFT: "messages"/text/prompt-completion; DPO: chosen/rejected; GRPO: prompt-only)
- **ALWAYS validate unknown datasets** before GPU training to prevent format failures (see Dataset Validation section below)
- Size appropriate for hardware (Demo: 50-100 examples on t4-small; Production: 1K-10K+ on a10g-large/a100-large)

### ⚠️ **Critical Settings**
- **Timeout must exceed expected training time** - Default 30min is TOO SHORT for most training. Minimum recommended: 1-2 hours. Job fails and loses all progress if timeout is exceeded.
- **Hub push must be enabled** - Config: `push_to_hub=True`, `hub_model_id="username/model-name"`; Job: `secrets={"HF_TOKEN": "$HF_TOKEN"}`

## Example Training Scripts

**Production-ready templates with all best practices:**

Load these scripts for correctly:

- **`scripts/train_sft_example.py`** - Complete SFT training with Trackio, LoRA, checkpoints
- **`scripts/train_dpo_example.py`** - DPO training for preference learning
- **`scripts/train_grpo_example.py`** - GRPO training for online RL

These scripts demonstrate proper Hub saving, Trackio integration, checkpoint management, and optimized parameters. Pass their content inline to `hf_jobs()` or use as templates for custom scripts.

## Limitations

- Use this skill only when the task clearly matches its upstream product or API scope.
- Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes.
- Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.

---

## Data Preparation Pipeline & Unsloth QLoRA Recipe (Módulo 3 — Pós IA para Devs)

### 1. Pipeline de Preparação de Datasets para Fine-Tuning
1. **Coleta Estruturada (Web Scraping Ético):** Use `requests` + `BeautifulSoup` (ou `Scrapy`/`Selenium` para páginas dinâmicas) respeitando termos de uso, `robots.txt` e direitos autorais; deduplicar URLs com `set()` e tratar erros HTTP.
2. **Geração Sintética de Outputs (LLM-as-a-Labeler):** Para reduzir o custo de rotulagem manual, gere pares `entrada -> saída esperada` com um LLM instrutor usando `response_format={"type": "json_object"}` e validação de schema.
3. **Unificação e Formatação:** Combine dados proprietários com datasets públicos do Hugging Face (`.jsonl`) em um formato de prompt consistente (ex.: formato **Alpaca** `### Instruction / ### Input / ### Response` + `tokenizer.eos_token` ou delimitadores explícitos `[|News|] ... [|eNews|]`).

### 2. Receita Prática: Fine-Tuning 4-bit QLoRA com Unsloth + `SFTTrainer`
Fundamento: **PEFT / LoRA** congela os pesos do modelo base (16-bit/4-bit) e treina apenas matrizes adaptadoras de baixo posto inseridas nas camadas de atenção e MLP (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`), reduzindo drasticamente o consumo de VRAM.

```python
from unsloth import FastLanguageModel, is_bfloat16_supported
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments, TextStreamer

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3-8b-bnb-4bit",
    max_seq_length=2048,
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

# Dataset formatado com campo "text" (Alpaca + EOS_TOKEN)
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,
        learning_rate=2e-4,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        output_dir="outputs",
    ),
)
trainer.train()

# Inferência otimizada com streaming e salvamento dos adaptadores LoRA
FastLanguageModel.for_inference(model)
model.save_pretrained("lora_model")
tokenizer.save_pretrained("lora_model")
```

### Referência Complementar (Carregar sob Demanda)
- `references/dataset-prep-and-unsloth-qlora.md` — Pipeline completo em 4 etapas (coleta/scraping ético, rotulagem sintética JSON mode, unificação HF + formato Alpaca) e script end-to-end Unsloth + Llama-3-8B 4-bit + `SFTTrainer` + `TextStreamer`.
