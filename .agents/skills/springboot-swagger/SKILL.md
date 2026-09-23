---
name: springboot-swagger
description: Especialista em documentação viva de APIs REST com Springdoc OpenAPI 3 no Spring Boot, anotações @Operation, @ApiResponses, Schemas, exemplos e segurança Bearer JWT.
license: MIT
metadata:
  framework: Spring Boot 3+ / 4+ & Springdoc OpenAPI
  version: '1.0'
---

# Habilidade: Spring Boot Swagger & OpenAPI 3 Documentation 📜✨

## Propósito
Você é a autoridade em Documentação Viva de APIs RESTful utilizando **Springdoc OpenAPI 3** no ecossistema Spring Boot (Java 21), fundamentado nos padrões de produção do `fitoherb-backend-v2`. Sua missão é garantir que cada endpoint, DTO, cabeçalho de autenticação e formato de resposta de erro seja documentado de forma clara, rica e interativa, servindo como contrato canônico entre o backend, frontend e consumidores externos.

---

## 1. Configuração Global do OpenAPI (`SwaggerConfiguration.java`)

A aplicação deve conter uma classe de configuração central em `infra/config/` registrando os metadados do projeto e o esquema de segurança global JWT:

```java
package com.fitoherb.fitoherb_backend_v2.infra.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfiguration {

    @Bean
    public OpenAPI customOpenAPI() {
        final String securitySchemeName = "bearerAuth";
        return new OpenAPI()
                .info(new Info()
                        .title("Application API")
                        .description("Plataforma de serviços RESTful com alta confiabilidade.")
                        .version("v2.0")
                        .contact(new Contact()
                                .name("Engineering Team")
                                .email("eng@empresa.com.br")
                                .url("https://github.com/empresa")))
                .addSecurityItem(new SecurityRequirement().addList(securitySchemeName))
                .components(new Components()
                        .addSecuritySchemes(securitySchemeName,
                                new SecurityScheme()
                                        .name(securitySchemeName)
                                        .type(SecurityScheme.Type.HTTP)
                                        .scheme("bearer")
                                        .bearerFormat("JWT")));
    }
}
```

---

## 2. Padrão de Anotação em Controllers

Todo `@RestController` deve conter a anotação `@Tag` no nível da classe e metadados detalhados em cada endpoint:

### 2.1 Anotação no Nível da Classe
```java
@RestController
@RequiredArgsConstructor
@RequestMapping("/products")
@Tag(name = "Products", description = "Gestão completa do catálogo de produtos e inventário.")
public class ProductController { ... }
```

### 2.2 Anotação de Endpoints (`@Operation` e `@ApiResponses`)
Cada método deve explicitar:
- **`@Operation`**: `summary` curto e `description` rica contextualizando a regra de negócio e permissões.
- **`@ApiResponses`**: Mapeamento de todos os cenários possíveis de retorno HTTP:
  - `200` / `201`: Sucesso com schema da resposta (`content = @Content(schema = @Schema(implementation = ResourceRes.class)))`).
  - `400`: Falha de validação ou payload malformado (`RestValidationErrorMessage.class`).
  - `401`: Token JWT ausente ou expirado (`RestErrorMessage.class`).
  - `403`: Acesso negado por falta de perfil de acesso (`RestErrorMessage.class`).
  - `404`: Recurso não encontrado (`RestErrorMessage.class`).
  - `409`: Conflito ou recurso duplicado (`RestErrorMessage.class`).

```java
@Operation(
    summary = "Obter detalhes do produto por slug",
    description = "Recupera as informações completas de um produto a partir de seu slug único. Requer autenticação."
)
@ApiResponses(value = {
    @ApiResponse(responseCode = "200", description = "Produto recuperado com sucesso",
            content = @Content(schema = @Schema(implementation = ProductRes.class))),
    @ApiResponse(responseCode = "404", description = "Produto não encontrado",
            content = @Content(schema = @Schema(implementation = RestErrorMessage.class),
                    examples = @ExampleObject(name = "Não Encontrado", value = "{\"status\": \"NOT_FOUND\", \"message\": \"Produto não encontrado com o slug: cha-verde\"}"))),
    @ApiResponse(responseCode = "403", description = "Acesso negado",
            content = @Content(schema = @Schema(implementation = RestErrorMessage.class),
                    examples = @ExampleObject(name = "Acesso Negado", value = "{\"status\": \"FORBIDDEN\", \"message\": \"Acesso negado: permissões insuficientes.\"}")))
})
@PreAuthorize("@authorizationService.isAuthenticated()")
@GetMapping("/{slug}")
public ResponseEntity<ProductRes> getBySlug(
    @Parameter(description = "Slug único do produto", example = "cha-verde-organico")
    @PathVariable String slug
) { ... }
```

---

## 3. Documentação de Uploads Multipart (Arquivos + DTO)

Para endpoints que combinam envio de arquivo binário e dados JSON:
```java
@Operation(summary = "Criar novo produto com imagem", description = "Cadastra um produto e processa o upload de sua imagem.")
@ApiResponses(value = {
    @ApiResponse(responseCode = "201", description = "Produto cadastrado com sucesso"),
    @ApiResponse(responseCode = "400", description = "Imagem excede 10MB ou formato inválido")
})
@PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
public ResponseEntity<ProductRes> create(
    @Parameter(description = "Arquivo de imagem (JPEG, PNG, WebP)")
    @RequestPart("image") MultipartFile image,

    @Parameter(description = "Dados cadastrais do produto em formato JSON")
    @RequestPart("data") @Valid ProductReq data
) { ... }
```

---

## 4. Schemas em DTOs (`@Schema`)

Nas classes de request (`dtos/requests/`) e response (`dtos/responses/`), utilize anotações `@Schema` para documentar campos, formatos, exemplos e obrigatoriedade:
```java
public class ProductReq {

    @Schema(description = "Nome comercial do produto", example = "Chá de Camomila Orgânico", requiredMode = Schema.RequiredMode.REQUIRED)
    @NotBlank(message = "O nome é obrigatório")
    private String name;

    @Schema(description = "Preço unitário em centavos", example = "2490")
    @NotNull
    private Long priceInCents;
}
```

---

## Quality Gates
- [ ] Classe `SwaggerConfiguration` configurada com metadados e autenticação Bearer JWT.
- [ ] Todo Controller anotado com `@Tag` descritivo.
- [ ] Todos os métodos mapeiam explicitamente os status de sucesso e as falhas esperadas (`400`, `401`, `403`, `404`).
- [ ] Respostas de erro utilizam os schemas canônicos `RestErrorMessage` e `RestValidationErrorMessage`.
- [ ] Exemplos práticos com `@ExampleObject` fornecidos para respostas de erro comuns.
- [ ] Rotas `/swagger-ui/**`, `/swagger-ui.html` e `/v3/api-docs/**` liberadas no Spring Security.
