---
name: genai-arquitetura
description: Arquiteturas de IA Generativa — GANs (Gerador/Discriminador), VAEs (Encoder/Decoder/reparameterização), Diffusion Models e Transformers para geração de conteúdo.
pages: 575-632
---

# IA Generativa — Arquiteturas

## Objetivo

Dominar as principais arquiteturas de redes neurais usadas em IA Generativa: GANs com training loop adversarial, VAEs com reparameterization trick, Diffusion Models com forward/reverse process, e Transformers como base dos LLMs modernos.

---

## Conceitos Fundamentais

### 1. GANs — Generative Adversarial Networks

GANs são compostas por dois modelos neurais que competem entre si em um jogo adversarial.

```
[Ruído Aleatório z]
        ↓
   [Gerador G]          → Imagem falsa
        ↓
[Discriminador D]  ←←  Imagem real (do dataset)
        ↓
  Real ou Falso?
```

**Objetivo:**
- **Gerador G**: minimizar a probabilidade de D detectar que a imagem é falsa
- **Discriminador D**: maximizar a probabilidade de distinguir real de falso

```python
import torch
import torch.nn as nn
import torch.optim as optim

class Gerador(nn.Module):
    """Gerador: transforma ruído aleatório em imagem sintética."""

    def __init__(self, dim_latente: int = 100, dim_imagem: int = 64*64*3):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(dim_latente, 256),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(256),
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2),
            nn.BatchNorm1d(512),
            nn.Linear(512, 1024),
            nn.LeakyReLU(0.2),
            nn.Linear(1024, dim_imagem),
            nn.Tanh()  # Saída em [-1, 1]
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.model(z)


class Discriminador(nn.Module):
    """Discriminador: classifica imagem como real (1) ou falsa (0)."""

    def __init__(self, dim_imagem: int = 64*64*3):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(dim_imagem, 1024),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid()  # Probabilidade [0, 1]
        )

    def forward(self, imagem: torch.Tensor) -> torch.Tensor:
        return self.model(imagem)


def training_loop_gan(
    gerador: Gerador,
    discriminador: Discriminador,
    dataloader,
    num_epocas: int = 100,
    dim_latente: int = 100,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
):
    """Training loop adversarial completo para GAN."""
    gerador.to(device)
    discriminador.to(device)

    criterio = nn.BCELoss()
    otim_g = optim.Adam(gerador.parameters(), lr=2e-4, betas=(0.5, 0.999))
    otim_d = optim.Adam(discriminador.parameters(), lr=2e-4, betas=(0.5, 0.999))

    for epoca in range(num_epocas):
        for batch_idx, (imagens_reais, _) in enumerate(dataloader):
            batch_size = imagens_reais.size(0)
            imagens_reais = imagens_reais.view(batch_size, -1).to(device)

            # Labels: 1 = real, 0 = falso (com label smoothing)
            rotulos_reais = torch.ones(batch_size, 1).to(device) * 0.9  # Label smoothing
            rotulos_falsos = torch.zeros(batch_size, 1).to(device)

            # ─── Treinar Discriminador ───────────────────────────────
            otim_d.zero_grad()

            # Perda em imagens reais
            pred_reais = discriminador(imagens_reais)
            perda_reais = criterio(pred_reais, rotulos_reais)

            # Gerar imagens falsas
            z = torch.randn(batch_size, dim_latente).to(device)
            imagens_falsas = gerador(z).detach()  # detach: não propagar para G
            pred_falsas = discriminador(imagens_falsas)
            perda_falsas = criterio(pred_falsas, rotulos_falsos)

            perda_d = (perda_reais + perda_falsas) / 2
            perda_d.backward()
            otim_d.step()

            # ─── Treinar Gerador ─────────────────────────────────────
            otim_g.zero_grad()

            z = torch.randn(batch_size, dim_latente).to(device)
            imagens_geradas = gerador(z)
            pred_geradas = discriminador(imagens_geradas)
            # Gerador quer enganar D: label = 1 (real)
            perda_g = criterio(pred_geradas, rotulos_reais)
            perda_g.backward()
            otim_g.step()

        if (epoca + 1) % 10 == 0:
            print(f"Época [{epoca+1}/{num_epocas}] | Perda D: {perda_d:.4f} | Perda G: {perda_g:.4f}")
```

#### Problemas Comuns em GANs

| Problema | Sintoma | Solução |
|---|---|---|
| **Mode Collapse** | Gerador produz sempre mesma imagem | Minibatch discrimination, Wasserstein GAN |
| **Training Instability** | Perdas oscilam sem convergir | Label smoothing, gradient penalty |
| **Vanishing Gradient** | Discriminador muito bom, G não aprende | Usar LeakyReLU, WGAN-GP |
| **Overfitting** | G memoriza dados, sem generalização | Mais dados, augmentation |

### 2. VAEs — Variational Autoencoders

VAEs aprendem uma distribuição probabilística no espaço latente, permitindo geração controlada.

```
Input x → [Encoder] → μ (média), σ (desvio padrão)
                    → z = μ + σ * ε    (reparameterization trick)
                    → [Decoder] → x̂ (reconstrução)
```

```python
class VAE(nn.Module):
    """Variational Autoencoder com reparameterization trick."""

    def __init__(self, dim_entrada: int = 784, dim_latente: int = 20):
        super().__init__()
        self.dim_latente = dim_latente

        # Encoder → produz μ e log(σ²)
        self.encoder = nn.Sequential(
            nn.Linear(dim_entrada, 400),
            nn.ReLU()
        )
        self.fc_mu = nn.Linear(400, dim_latente)       # Média
        self.fc_logvar = nn.Linear(400, dim_latente)   # Log variância

        # Decoder → reconstrói a entrada
        self.decoder = nn.Sequential(
            nn.Linear(dim_latente, 400),
            nn.ReLU(),
            nn.Linear(400, dim_entrada),
            nn.Sigmoid()  # Output [0, 1] para pixels normalizados
        )

    def encode(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_logvar(h)

    def reparametrizar(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """
        Reparameterization trick: z = μ + σ * ε
        Permite backpropagation através da operação estocástica.
        ε ~ N(0, I) é amostrado separadamente.
        """
        std = torch.exp(0.5 * logvar)
        epsilon = torch.randn_like(std)  # ε ~ N(0, I)
        return mu + std * epsilon

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> tuple:
        mu, logvar = self.encode(x)
        z = self.reparametrizar(mu, logvar)
        reconstrucao = self.decode(z)
        return reconstrucao, mu, logvar


def perda_vae(reconstrucao: torch.Tensor, x: torch.Tensor, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
    """
    ELBO Loss = Reconstrução + KL Divergência
    KL: mede quanto a distribuição latente se afasta de N(0, I)
    """
    # Perda de reconstrução (BCE para pixels)
    perda_reconstrucao = nn.functional.binary_cross_entropy(
        reconstrucao, x, reduction='sum'
    )
    # KL Divergência: -0.5 * Σ(1 + log(σ²) - μ² - σ²)
    kl_divergencia = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())

    return perda_reconstrucao + kl_divergencia
```

### 3. Diffusion Models

Diffusion Models aprendem a remover ruído de imagens gradualmente, gerando amostras de alta qualidade.

```
FORWARD PROCESS (treinamento):
Imagem Real → + ruído → + ruído → ... → Ruído Puro (N(0, I))
     x₀    →    x₁    →    x₂   → ... →     xₜ

REVERSE PROCESS (geração):
Ruído Puro → - ruído → - ruído → ... → Imagem Gerada
    xₜ    →   xₜ₋₁  →   xₜ₋₂  → ... →     x₀

O modelo U-Net aprende a predizer o ruído adicionado em cada passo.
```

```python
class DenoisingModel(nn.Module):
    """Modelo de denoising simplificado (U-Net na prática)."""

    def __init__(self, dim_imagem: int, num_passos: int = 1000):
        super().__init__()
        self.num_passos = num_passos

        # Schedule de ruído linear
        self.betas = torch.linspace(1e-4, 0.02, num_passos)
        self.alphas = 1.0 - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)

        # Rede de denoising (U-Net simplificada)
        self.model = nn.Sequential(
            nn.Linear(dim_imagem + 1, 512),  # +1 para embedding do passo t
            nn.SiLU(),
            nn.Linear(512, 512),
            nn.SiLU(),
            nn.Linear(512, dim_imagem)
        )

    def adicionar_ruido(self, x0: torch.Tensor, t: torch.Tensor) -> tuple:
        """Forward process: adiciona ruído gaussiano no passo t."""
        sqrt_alpha = self.alphas_cumprod[t].sqrt().view(-1, 1)
        sqrt_um_menos_alpha = (1 - self.alphas_cumprod[t]).sqrt().view(-1, 1)
        epsilon = torch.randn_like(x0)  # Ruído real
        xt = sqrt_alpha * x0 + sqrt_um_menos_alpha * epsilon
        return xt, epsilon

    def forward(self, xt: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        """Prediz o ruído adicionado em xt no passo t."""
        t_emb = (t.float() / self.num_passos).view(-1, 1)
        entrada = torch.cat([xt, t_emb], dim=1)
        return self.model(entrada)


# Aplicações de Diffusion Models
APLICACOES_DIFFUSION = {
    "Stable Diffusion": "Geração de imagens condicionada em texto (CLIP)",
    "DALL-E 3": "Text-to-Image via diffusion + GPT-4 para prompts",
    "Stable Video Diffusion": "Geração de vídeos a partir de imagens",
    "AudioLDM": "Geração de áudio via diffusion no espaço latente",
    "DreamBooth": "Fine-tuning personalizado com 3-5 fotos",
}
```

### 4. Transformers para Geração

```
Arquitetura base de GPT, T5, BERT, Llama, Claude, Gemini.

Componentes-chave:
- Self-Attention: cada token "vê" todos os outros tokens
- Multi-Head Attention: múltiplas "perspectivas" de atenção
- Feed-Forward Network: transformação por posição
- Layer Normalization: estabilidade de treinamento
- Positional Encoding: injeta informação de ordem
```

| Modelo | Arquitetura | Uso |
|---|---|---|
| **GPT-4** | Decoder-only | Geração de texto (autoregressive) |
| **BERT** | Encoder-only | Classificação, embeddings |
| **T5** | Encoder-Decoder | Tradução, sumarização |
| **Llama 3** | Decoder-only | Geração open-source |

---

## Padrões e Boas Práticas

### Problemas de Treinamento e Soluções

```python
# Detectar overfitting
def monitorar_overfitting(
    perda_treino: list[float],
    perda_validacao: list[float],
    patience: int = 10
) -> bool:
    """Detecta overfitting quando validação para de melhorar."""
    if len(perda_validacao) < patience:
        return False

    melhor_val = min(perda_validacao[:-patience])
    val_recente = min(perda_validacao[-patience:])
    overfitting = val_recente > melhor_val * 1.05  # 5% de tolerância

    if overfitting:
        print(f"⚠️ OVERFITTING DETECTADO: Val={val_recente:.4f} > Melhor={melhor_val:.4f}")
    return overfitting


# Dataset de imagens 64x64 RGB (1400 amostras típicas para GAN simples)
def criar_dataloader_imagens(pasta: str, batch_size: int = 64):
    from torchvision import datasets, transforms
    from torch.utils.data import DataLoader

    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])  # [-1, 1]
    ])

    dataset = datasets.ImageFolder(pasta, transform=transform)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True  # Otimiza transferência para GPU
    )
```

### Data Augmentation para Pequenos Datasets

```python
from torchvision import transforms

augmentation = transforms.Compose([
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
    transforms.RandomResizedCrop(64, scale=(0.8, 1.0)),
])
# Dataset com 1400 imagens → equivalente a ~5600 com augmentation
```

---

## Checklist de Qualidade

- [ ] GAN com LeakyReLU no discriminador (não ReLU padrão)
- [ ] Label smoothing implementado no discriminador (0.9 em vez de 1.0)
- [ ] `detach()` aplicado nas imagens falsas ao treinar o discriminador
- [ ] Reparameterization trick implementado corretamente no VAE
- [ ] KL Divergência incluída na loss do VAE (ELBO = reconstrução + KL)
- [ ] Diffusion Model com schedule de ruído linear ou cosine
- [ ] Data augmentation para datasets com menos de 5.000 imagens
- [ ] Monitoramento de overfitting com early stopping
- [ ] GPU utilizada (`device = "cuda" if torch.cuda.is_available() else "cpu"`)
- [ ] Checkpoints salvos a cada N épocas
- [ ] Métricas FID (Fréchet Inception Distance) calculadas para avaliar qualidade
- [ ] Mode collapse monitorado: diversidade nas amostras geradas
