---
name: deep-learning-cv-expert
description: Especialista em Redes Neurais Profundas, Visão Computacional, CNNs, U-Net, transfer learning e aceleração por GPU/CUDA com PyTorch.
---
# Habilidade: Deep Learning & Computer Vision Architect 👁️🧠

## Propósito
Você é o arquiteto especialista no projeto, treinamento, fine-tuning e otimização de Redes Neurais Profundas e sistemas de **Visão Computacional** utilizando **PyTorch** e **Torchvision**. Sua especialidade engloba desde a classificação de imagens com redes convolucionais e transfer learning (ResNet, DenseNet, EfficientNet) até tarefas de segmentação semântica (U-Net) e aceleração por hardware GPU (CUDA/MPS).

---

## Gatilhos de Uso (Trigger & Scope)
Utilize esta skill obrigatoriamente quando:
- Desenvolver pipelines de classificação, detecção ou segmentação de imagens e dados não-estruturados.
- Implementar redes neurais com PyTorch utilizando aceleração dinâmica por GPU (`torch.device("cuda" if torch.cuda.is_available() else "cpu")`).
- Aplicar *Transfer Learning* com modelos pré-treinados no ImageNet congelando camadas iniciais e ajustando a cabeça de classificação (`classifier` / `fc`).
- Estruturar loops modulares de treinamento com cálculo de perda, retropropagação (`backward`), passo do otimizador (`step`), *learning rate scheduling* e *early stopping*.
- Exportar modelos treinados como State Dict (`.pth`), TorchScript (`torch.jit.trace`) ou formato interoperável ONNX para inferência otimizada.

---

## Competências Principais e Boas Práticas

### 1. Detecção Dinâmica de Dispositivo (Hardware Agnostic)
- **Regra Obrigatória:** Nunca assuma estaticamente que `cuda` está disponível. Utilize verificação dinâmica:
  ```python
  device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
  ```
- Garanta que tanto o modelo quanto os tensores de entrada e rótulos sejam movidos para o mesmo dispositivo (`model.to(device)`, `inputs.to(device)`).

### 2. Transfer Learning e Fine-Tuning Eficiente
- Em problemas com datasets limitados (ex: imagens médicas de mamografia ou raio-X), inicialize com pesos consolidados (`weights='DEFAULT'`).
- Congele os parâmetros das camadas convolucionais (`param.requires_grad = False`) para treinar inicialmente apenas as camadas totalmente conectadas, evitando destruir os extratores de features prévios.

### 3. Modos `model.train()` vs `model.eval()` e `torch.no_grad()`
- Antes de qualquer inferência ou loop de validação, chame obrigatoriamente `model.eval()` e envolva o bloco com `with torch.no_grad():`. Isso desativa camadas de *Dropout* e congela as estatísticas de *BatchNorm*.

### 4. Data Augmentation e Normalização
- Aplique transformações de pré-processamento via `torchvision.transforms.v2` (Resize, CenterCrop, RandomHorizontalFlip, Normalização com médias do ImageNet `mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]`).

---

## Template de Implementação (PyTorch + Transfer Learning + Loop Modular + Exportação)

```python
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from torch.utils.data import DataLoader, Dataset
from PIL import Image

# 1. Configuração Dinâmica de Dispositivo
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 2. Definição do Modelo com Transfer Learning (DenseNet121 / ResNet)
def create_vision_model(num_classes=2, freeze_backbone=True):
    model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)
    
    if freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False
            
    num_ftrs = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Linear(num_ftrs, 256),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(256, num_classes)
    )
    return model.to(device)

# 3. Loop de Treinamento Modular com Validação
def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=10, save_path="weights/model.pth"):
    best_val_acc = 0.0
    
    for epoch in range(num_epochs):
        # Fase de Treino
        model.train()
        running_loss = 0.0
        corrects = 0
        total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            corrects += torch.sum(preds == labels.data)
            total += labels.size(0)
            
        epoch_loss = running_loss / total
        epoch_acc = corrects.double() / total
        
        # Fase de Validação
        model.eval()
        val_corrects = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                val_corrects += torch.sum(preds == labels.data)
                val_total += labels.size(0)
                
        val_acc = val_corrects.double() / val_total
        print(f"Epoch {epoch+1}/{num_epochs} - Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f} | Val Acc: {val_acc:.4f}")
        
        # Salvamento do Melhor Checkpoint
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            torch.save(model.state_dict(), save_path)
            print(f"-> Checkpoint salvo em {save_path} com Val Acc: {val_acc:.4f}")
            
    return model
```

---

## Quality Gates
- [ ] Detecção dinâmica de dispositivo (`torch.device`) sem dependência fixa em CUDA.
- [ ] Separação clara entre modos `model.train()` e `model.eval()`.
- [ ] Inferência encapsulada em bloco `with torch.no_grad():`.
- [ ] Camadas congeladas adequadamente em rotinas de *Transfer Learning*.
- [ ] Checkpoint exportado no formato State Dict (`.pth`) ou TorchScript.

---

## Computer Vision Clássica e OCR (Pós IA para Devs, p. 238-322)

### OpenCV Essencial: Pré-Processamento de Imagens
- **Conversão para Grayscale:** Redução de dimensionalidade de 3 canais (BGR/RGB) para 1 canal de intensidade luminosa (`cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)`), cortando em 66% a carga computacional de etapas subsequentes de extração de bordas e OCR.
- **Gaussian Blur (Filtro Gaussiano):** Convolução com kernel gaussiano 2D (`cv2.GaussianBlur(gray, (5, 5), 0)`) para atenuação de ruídos de alta frequência e suavização sem destruir bordas estruturais.

### Limiarização Adaptativa e Binarização de Otsu
- **Binarização de Otsu:** Determinação automática do limiar ideal minimizando a variância intraclasse dos pixels de fundo e primeiro plano:
  ```python
  _, thresh_otsu = cv2.threshold(gray_blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
  ```
- **Limiarização Adaptativa (Adaptive Gaussian / Mean):** Fundamental para documentos digitalizados com iluminação não uniforme ou sombras:
  ```python
  adaptive_thresh = cv2.adaptiveThreshold(
      gray_blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
  )
  ```

### Pipeline de OCR Moderno (Deskew + Preprocessing -> Tesseract / EasyOCR)
```python
import cv2
import numpy as np
import pytesseract
import easyocr

def preprocess_and_ocr(image_path: str, engine: str = "easyocr") -> str:
    # 1. Leitura da Imagem
    image = cv2.imread(image_path)
    
    # 2. Escala de cinza e redução de ruído
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    
    # 3. Deskew (Correção de inclinação de página)
    coords = np.column_stack(np.where(blurred < 200))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle
            
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(blurred, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    else:
        rotated = blurred

    # 4. Binarização adaptativa para contraste de texto
    processed = cv2.adaptiveThreshold(
        rotated, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 4
    )

    # 5. Extração de Texto via Engine Escolhido
    if engine == "tesseract":
        # Configuração OEM (LSTM) + PSM (Automático)
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed, lang='por+eng', config=custom_config)
    else:
        reader = easyocr.Reader(['pt', 'en'], gpu=False)
        results = reader.readtext(processed)
        text = "\n".join([res[1] for res in results])

    return text.strip()
```

### Detecção em Tempo Real com YOLOv8 (Ultralytics)
```python
from ultralytics import YOLO
import cv2

# Carregar modelo pré-treinado (nano para borda/tempo real ou x-large para alta precisão)
model = YOLO("yolov8n.pt")

def detect_objects_frame(frame):
    # Inferência em batch ou frame unitário
    results = model(frame, conf=0.45, iou=0.5)[0]
    
    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls_id = int(box.cls[0])
        class_name = model.names[cls_id]
        confidence = float(box.conf[0])
        
        detections.append({
            "bbox": [x1, y1, x2, y2],
            "class": class_name,
            "confidence": confidence
        })
        
        # Desenhar bounding box e anotação
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{class_name} {confidence:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
    return frame, detections
```

### Rastreamento de Objetos em Vídeo com Persistência de ID
- **TrackerCSRT:** Algoritmo clássico de correlação discriminativa com confiabilidade espacial no OpenCV (`cv2.TrackerCSRT_create()`), ideal para alvos pontuais de alto valor quando não há GPU disponível.
- **ByteTrack e DeepSORT:** Rastreamento moderno baseado em associação de dados entre frames via Filtro de Kalman e Hungarian Algorithm, preservando identificadores únicos (`track_id`) mesmo sob oclusões temporárias.

```python
# Rastreamento integrado via Ultralytics com ByteTrack / BoT-SORT
def track_video_stream(video_path: str):
    cap = cv2.VideoCapture(video_path)
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
            
        # track() associa detecções consecutivas com ByteTrack
        results = model.track(frame, persist=True, tracker="bytetrack.yaml")
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.int().cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            clss = results[0].boxes.cls.int().cpu().tolist()
            
            for box, track_id, cls_idx in zip(boxes, track_ids, clss):
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(
                    frame,
                    f"ID:{track_id} {model.names[cls_idx]}",
                    (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 0, 0),
                    2
                )

        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
```

