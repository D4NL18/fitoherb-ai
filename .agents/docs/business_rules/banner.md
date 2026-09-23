# Business Rules: Banner

> **Autor:** Analista de Requisitos
> **Objetivo:** Travar requisitos técnicos mínimos para as artes expostas no E-commerce.

## Regras de Dimensão e Formato das Artes
- **P-018:** Um banner promocional está sumariamente invalidado se a requisição de cadastro chegar sem uma imagem anexa.
- **P-019:** Existe uma política de resolução mínima. Banners cuja imagem extraída apresentar largura inferior a `1000px` serão rejeitados, disparando `FileStorageException`.
- **P-020:** Banners seguem a política de *Aspect Ratio* estrita de paisagem (orientação horizontal). A largura geométrica do arquivo (`width`) deverá ser matematicamente e estritamente superior à altura (`height`). Imagens verticais ou quadradas disparam erro de validação (FileStorageException).
