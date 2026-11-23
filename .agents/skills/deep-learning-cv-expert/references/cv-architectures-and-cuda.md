# Guia de Referência: Arquiteturas de Computer Vision e Aceleração GPU/CUDA

## 1. Tarefas de Visão Computacional e Modelos Recomendados

| Tarefa | Saída | Arquiteturas Recomendadas | Métrica Principal |
| :--- | :--- | :--- | :--- |
| **Classificação de Imagens** | Classe (`CAT`) | ResNet, ConvNeXt, EfficientNet, ViT | Top-1 Accuracy, F1-Macro |
| **Detecção de Objetos** | Bounding Boxes + Classes | YOLOv8/v11 (tempo real), DETR, Faster R-CNN | mAP@50, mAP@50:95, FPS |
| **Segmentação Semântica** | Máscara pixel-a-pixel | U-Net (saúde/satélite), DeepLabV3+, SAM | IoU (Jaccard), Dice Score |
| **Rastreamento em Vídeo** | Boxes + `track_id` persistente | ByteTrack / BoT-SORT (GPU), OpenCV CSRT (CPU) | MOTA, IDF1 |
| **Estimação de Pose** | Keypoints articulados | YOLOv8-Pose, MediaPipe | OKS (Object Keypoint Similarity) |

## 2. Checklist de Treinamento e Aceleração CUDA
- **Dispositivo Dinâmico:** Sempre use `device = torch.device("cuda" if torch.cuda.is_available() else "cpu")` e mova modelo + tensores explicitamente (`.to(device)`).
- **Modos de Execução:** `model.train()` no treino (ativa Dropout/BatchNorm) e `model.eval()` + `with torch.no_grad():` na validação/inferência.
- **Ordem do Loop:** `optimizer.zero_grad()` → `forward` → `loss` → `loss.backward()` → `optimizer.step()`.
- **Exportação para Produção:** Salve apenas `model.state_dict()` (`.pth`) ou exporte para **TorchScript / ONNX** para inferência desacoplada e rápida em containers enxutos.
