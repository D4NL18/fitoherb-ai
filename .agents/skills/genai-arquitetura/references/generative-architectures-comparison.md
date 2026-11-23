# Comparativo Técnico: Arquiteturas de IA Generativa

Guia de referência para seleção arquitetural entre **GANs**, **VAEs**, **Diffusion Models** e **Transformers** em projetos de IA Generativa.

---

## 1. Matriz Comparativa Geral

| Dimensão | GANs (Generative Adversarial Networks) | VAEs (Variational Autoencoders) | Diffusion Models (DDPM / LDM) | Transformers (Autoregressive / Seq2Seq) |
| :--- | :--- | :--- | :--- | :--- |
| **Mecanismo Central** | Jogo minimax entre Gerador ($G$) e Discriminador ($D$) | Encoder-Decoder probabilístico maximizando ELBO | Adição gradual de ruído (forward) + denoising iterativo (reverse) | Self-Attention + predição autorregressiva do próximo token |
| **Espaço Latente** | Implícito, não estruturado (salvo variantes como StyleGAN) | Explícito, contínuo e regularizado ($\mathcal{N}(0, I)$ via KL) | Latente comprimido (LDM usa VAE) ou espaço de pixels direto | Representações contextuais por token (hidden states / KV cache) |
| **Estabilidade de Treino** | Baixa (mode collapse, gradientes instáveis, sensível a hiperparâmetros) | Alta (loss ELBO estável; risco de posterior collapse) | Muito alta (objetivo simples de MSE/L2 no ruído predito) | Alta em escala (com LayerNorm, AdamW, warmup e clipping) |
| **Qualidade / Fidelidade** | Muito alta em domínios específicos (rostos, super-resolução) | Moderada (tende a gerar saídas mais borradas em imagens) | Estado da arte em fidelidade visual, diversidade e controle | Estado da arte em texto, código, raciocínio e multimodalidade |
| **Latência de Inferência** | Muito baixa (1 único forward pass) | Muito baixa (1 único forward pass no decoder) | Alta (15–50 passos iterativos; mitigado por DDIM/LCM/Distillation) | Média a alta (sequencial token a token; otimizado com KV Cache) |
| **Diversidade (Mode Coverage)** | Baixa a média (propenso a mode collapse) | Alta (cobre bem a distribuição dos dados) | Muito alta (excelente cobertura de modos) | Muito alta (controlável via temperature, top-p, top-k) |
| **Custo Computacional** | Moderado no treino, muito baixo na inferência | Baixo no treino e na inferência | Alto no treino e moderado/alto na inferência | Muito alto no pré-treino; moderado em fine-tuning (LoRA/QLoRA) |

---

## 2. Análise Detalhada por Arquitetura

### 2.1 GANs (Generative Adversarial Networks)
- **Funcionamento:** O Gerador mapeia ruído $z \sim p(z)$ para amostras sintéticas enquanto o Discriminador distingue real vs. falso. Não modela a densidade de probabilidade $p(x)$ explicitamente.
- **Espaço Latente:** Permite interpolação visual, mas sem garantia de continuidade semântica global, a menos que se usem arquiteturas especializadas (ex.: espaço $\mathcal{W}$ do StyleGAN2/3).
- **Estabilidade de Treino:** Requer técnicas de estabilização como **WGAN-GP** (Wasserstein + Gradient Penalty), **Spectral Normalization**, **Label Smoothing** e balanceamento de learning rates (TTUR).
- **Casos de Uso Ideais:** Super-resolução em tempo real (ESRGAN), tradução imagem-para-imagem (CycleGAN, Pix2Pix), síntese de dados tabulares/médicos em baixa latência.

### 2.2 VAEs (Variational Autoencoders)
- **Funcionamento:** O Encoder estima $\mu$ e $\log(\sigma^2)$, o *reparameterization trick* ($z = \mu + \sigma \odot \epsilon$) permite backpropagation, e o Decoder reconstrói $x$. Otimiza $\mathcal{L}_{ELBO} = \mathcal{L}_{rec} + \beta \cdot D_{KL}(q(z|x) \parallel p(z))$.
- **Espaço Latente:** Principal ponto forte — suave, contínuo e interpretável. Ideal para interpolação, compressão semântica e detecção de anomalias (erro de reconstrução alto).
- **Estabilidade de Treino:** Muito estável. Atenção ao *KL vanishing / posterior collapse* (mitigado com *KL annealing* ou $\beta$-VAE).
- **Casos de Uso Ideais:** Compressão latente para Latent Diffusion Models (Stable Diffusion), detecção de anomalias industriais, geração molecular/química e representação de dados estruturados.

### 2.3 Diffusion Models (DDPM, DDIM, Latent Diffusion)
- **Funcionamento:** Corrompe dados em $T$ passos com ruído gaussiano e treina uma rede (U-Net ou DiT — Diffusion Transformer) para prever o ruído $\epsilon$ ou a velocidade $v$ em cada passo $t$.
- **Espaço Latente:** Em *Latent Diffusion Models* (SDXL, Flux), a difusão ocorre no espaço latente de um VAE pré-treinado, reduzindo drasticamente VRAM e FLOPs sem perda perceptível de detalhes.
- **Estabilidade de Treino:** Excelente; não sofre de mode collapse adversarial. Suporta condicionamento rico via Cross-Attention (CLIP/T5) e controle espacial fino (**ControlNet**, **IP-Adapter**).
- **Casos de Uso Ideais:** Text-to-Image (marketing, design, prototipagem), inpainting/outpainting, geração de vídeo (Sora, SVD) e síntese de áudio/música.

### 2.4 Transformers (Decoder-only, Encoder-Decoder)
- **Funcionamento:** Mecanismo de *Scaled Dot-Product Self-Attention* captura dependências de longo alcance em paralelo durante o treino. Na geração (Decoder-only como GPT, Llama, Gemini, Claude), prediz o próximo token condicionado ao contexto anterior.
- **Espaço Latente:** Representações contextuais em camadas sucessivas; custo de atenção cresce quadraticamente $O(N^2)$ com o comprimento da sequência (mitigado por FlashAttention, GQA e sliding window).
- **Estabilidade de Treino:** Previsível segundo *Scaling Laws* (Chinchilla), mas exige infraestrutura distribuída (FSDP/DeepSpeed) para modelos grandes.
- **Casos de Uso Ideais:** Geração de texto e código, agentes autônomos com function calling, RAG, sumarização, raciocínio estruturado e modelos multimodais nativos.

---

## 3. Guia Rápido de Decisão (Trade-offs)

| Cenário / Requisito | Arquitetura Recomendada | Justificativa |
| :--- | :--- | :--- |
| Geração de texto, código, JSON estruturado ou agentes | **Transformer (Decoder-only)** | Única arquitetura com raciocínio contextual e domínio simbólico estado da arte. |
| Geração de imagens fotorrealistas condicionadas por texto/layout | **Latent Diffusion (U-Net / DiT)** | Melhor equilíbrio entre fidelidade, diversidade e controle (ControlNet/LoRA). |
| Inferência visual em tempo real (< 20ms) em edge/mobile | **GAN (ou Diffusion destilado em 1–4 passos)** | Forward pass único garante latência mínima e previsível. |
| Detecção de anomalias ou compressão com espaço latente interpretável | **VAE ($\beta$-VAE / VQ-VAE)** | Espaço latente regularizado e métrica probabilística direta de reconstrução. |
| Dataset pequeno (< 5.000 amostras) com necessidade de estabilidade | **VAE ou Fine-tuning (LoRA) em modelo pré-treinado** | Evita instabilidade de treino do zero e mode collapse típico de GANs. |
