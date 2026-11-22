---
name: genai-expert
description: "Use quando a tarefa envolver: Fundamentos, arquiteturas (Transformers, GANs, VAEs, Diffusion), aplicacoes praticas com APIs de imagem/texto, fine-tuning e etica/regulacao de IA Generativa (EU AI Act, PL 2338/2023)."
---

# Habilidade: Generative AI Expert (GenAI) 🤖🎨

## Propósito
Especialista em inteligência artificial generativa multimodais, dominando desde a teoria estatística e arquiteturas profundas (Transformers, Modelos de Difusão, GANs, VAEs) até engenharia de aplicações comerciais, fine-tuning e conformidade ética e regulatória.

---

## 1. Fundamentos e Foundation Models
- **Paradigma Discriminativo vs Generativo:** Modelagem de $P(Y|X)$ vs modelagem da distribuição conjunta $P(X)$ no espaço latente.
- **Adaptação de Foundation Models:** Espectro de intervenção: Zero-shot $\to$ Few-shot $\to$ In-Context Learning $\to$ RAG $\to$ PEFT/LoRA (Parameter-Efficient Fine-Tuning) $\to$ Full Fine-Tuning.
- **Tokenização & Espaço Latente:** Subword tokenization (BPE, WordPiece), autoencoders variacionais e interpolação no espaço latente.

---

## 2. Arquiteturas de Geração
- **Transformers (Auto-regressivos & Mascarados):** Atenção multi-cabeça ($Q, K, V$), FlashAttention, RoPE (Rotary Position Embeddings), KV-Cache.
- **Diffusion Models:** Processo de difusão forward (adição controlada de ruído gaussiano) e reverso (denoising guiado com U-Net e condicionamento CLIP/T5).
- **GANs & VAEs:** Redes adversariais com minimax loss para imagens de alta fidelidade e VAEs com *reparameterization trick* para representações probabilísticas suaves.

---

## 3. Aplicações Práticas & Integração
- **Geração Multimodal:** Pipelines de texto para imagem (Stable Diffusion, DALL-E API), ControlNet para controle geométrico/pose de imagens, transcrição com Whisper.
- **Serviços Backend em Produção:** Streaming SSE (Server-Sent Events) via FastAPI para geração interativa, chains de fallback e parsing de saídas estruturadas.

---

## 4. Governança, Ética & Regulação
- **Mitigação de Riscos:** Prevenção e detecção de deepfakes, watermarking de mídia sintética (C2PA / SynthID), direitos autorais e mitigação de viés discriminatório.
- **Enquadramento Regulatório:** Alinhamento estrito com o **EU AI Act** (classificação por risco inaceitável, alto, limitado e mínimo) e o **PL 2338/2023** brasileiro (direitos de explicabilidade, contestação e responsabilidade civil).
