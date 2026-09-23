---
name: springboot-dto-mapper
description: Especialista em DTOs, Bean Validation com constantes regex e Mappers de alta performance com MapStruct 1.5+ no Spring Boot.
license: MIT
metadata:
  framework: Spring Boot 3+ / 4+, MapStruct & Jakarta Validation
  version: '1.0'
---

# Habilidade: DTOs, Jakarta Bean Validation & MapStruct Expert 🔄📐

## Propósito
Você é a autoridade técnica em Isolamento de Domínio, Validação Declarativa de Dados e Mapeamento de Objetos de Alta Performance utilizando **MapStruct 1.5+** e **Jakarta Bean Validation** no ecossistema Spring Boot (Java 21), fundamentado nos padrões do `fitoherb-backend-v2`. Sua missão é blindar a camada de domínio contra vazamento de detalhes internos, garantir validação estrita de contratos na borda e gerar mappers síncronos sem overhead de reflexão (*reflection-free*).

---

## 1. Segregação Estrita de DTOs (`dtos/`)

As entidades JPA NUNCA devem transitar como parâmetros ou retornos de controllers. O projeto segrega os DTOs em duas pastas estritas:
- **`dtos/requests/`**: Contratos de entrada recebidos da API (sufixo `Req`).
- **`dtos/responses/`**: Contratos de saída entregues aos clientes (sufixo `Res`).

---

## 2. Validações Declarativas com `ValidationConstants`

Para evitar duplicação de expressões regulares e mensagens de erro, centralize regras em `utils/validations/ValidationConstants.java`:

```java
package com.fitoherb.fitoherb_backend_v2.utils.validations;

public final class ValidationConstants {
    private ValidationConstants() {}

    public static final String SLUG_REGEX = "^[a-z0-9]+(?:-[a-z0-9]+)*$";
    public static final String MSG_SLUG_INVALID = "O slug deve conter apenas letras minúsculas, números e hífens.";

    public static final String PASSWORD_REGEX = "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=!]).{8,}$";
    public static final String MSG_PASSWORD_INVALID = "A senha deve ter no mínimo 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial.";
}
```

### Uso no Request DTO:
```java
package com.fitoherb.fitoherb_backend_v2.dtos.requests;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import lombok.Getter;
import lombok.Setter;

import static com.fitoherb.fitoherb_backend_v2.utils.validations.ValidationConstants.*;

@Getter
@Setter
public class ProductReq {

    @NotBlank(message = "O nome do produto é obrigatório")
    private String name;

    @NotBlank(message = "O slug é obrigatório")
    @Pattern(regexp = SLUG_REGEX, message = MSG_SLUG_INVALID)
    private String slug;

    @NotNull(message = "A categoria é obrigatória")
    private String categorySlug;
}
```

---

## 3. Mapeamentos com MapStruct 1.5+ (`mappers/`)

O MapStruct gera código puro em tempo de compilação, eliminando o custo de reflexão do ModelMapper ou BeanUtils:

```java
package com.fitoherb.fitoherb_backend_v2.mappers;

import com.fitoherb.fitoherb_backend_v2.dtos.requests.ProductReq;
import com.fitoherb.fitoherb_backend_v2.dtos.responses.ProductRes;
import com.fitoherb.fitoherb_backend_v2.entities.Product;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.MappingTarget;

@Mapper(componentModel = "spring", uses = {ProductCategoryMapper.class, ImageUrlBuilder.class})
public interface ProductMapper {

    @Mapping(target = "createdAt", dateFormat = "dd-MM-yyyy HH:mm:ss")
    @Mapping(target = "imageUrl", source = "imagePath", qualifiedByName = "toPublicUrl")
    ProductRes entityToRes(Product product);

    @Mapping(target = "category", ignore = true)
    @Mapping(target = "supplier", ignore = true)
    Product reqToEntity(ProductReq productReq);

    // Atualização in-place de entidade existente
    void updateEntityFromReq(ProductReq productReq, @MappingTarget Product product);
}
```

### Qualificadores de URL Customizados (`ImageUrlBuilder.java`):
```java
@Component
public class ImageUrlBuilder {
    @Named("toPublicUrl")
    public String toPublicUrl(String imagePath) {
        if (imagePath == null || imagePath.isBlank()) return null;
        return "https://storage.googleapis.com/meu-bucket/" + imagePath;
    }
}
```

---

## 4. Atualização In-Place no Service

Para atualizações parciais ou completas de entidades com `@MappingTarget`:
```java
@Transactional
public ProductRes updateProduct(String slug, ProductReq req) {
    Product product = productRepository.findBySlug(slug)
            .orElseThrow(() -> new ResourceNotFoundException("Produto não encontrado"));

    productMapper.updateEntityFromReq(req, product);
    Product updated = productRepository.save(product);
    return productMapper.entityToRes(updated);
}
```

---

## Quality Gates
- [ ] DTOs segregados nas pastas `dtos/requests/` e `dtos/responses/`.
- [ ] Expressões regulares de validação centralizadas em `ValidationConstants.java`.
- [ ] Mappers definidos como interfaces anotadas com `@Mapper(componentModel = "spring")`.
- [ ] Atualização de entidades existentes utiliza `@MappingTarget` (sem setters manuais repetitivos).
- [ ] Controllers recebem `@Valid` no `@RequestBody` para acionar o Bean Validation.
- [ ] Nenhuma Entidade JPA exposta diretamente nos retornos dos Controllers.
