# API Contracts: Banner

> **Autor:** Arquiteto de Software
> **Objetivo:** Definir os contratos de integração (API) para Banners promocionais.

## `GET /api/banners`
- **Descrição:** Lista paginada/ordenada de banners para preenchimento dos carrosséis no front-end.

## `GET /api/banners/{id}`
- **Descrição:** Busca detalhes de um banner pelo seu UUID.

## `POST /api/banners` e `PUT /api/banners/{id}`
- **Content-Type:** `multipart/form-data`. (JSON com titulo/subtitulo + imagem).
- *Nota do Arquiteto: Em virtude de restrições de tela, requisições que enviam imagens que não respeitem a orientação paisagem resultarão em Bad Request/Erro de Validação interna.*

## `DELETE /api/banners/{id}`
- **Descrição:** Apaga o banner.
