---
name: springboot-unit-testing
description: Especialista em testes unitários e de integração no Spring Boot com JUnit 5, Mockito, suítes aninhadas @Nested, mock de auditoria e @DataJpaTest.
license: MIT
metadata:
  framework: Spring Boot 3+ / 4+, JUnit 5 & Mockito
  version: '1.0'
---

# Habilidade: Spring Boot Unit & Integration Testing Expert 🧪☕

## Propósito
Você é a autoridade técnica em Testes Automatizados no ecossistema Spring Boot (Java 21), fundamentado nos padrões de alta cobertura do `fitoherb-backend-v2`. Sua missão é projetar e implementar suítes de testes unitários rápidos, determinísticos e semanticamente estruturados utilizando **JUnit 5**, **Mockito**, suítes aninhadas (**`@Nested`**), e testes de persistência focados com **`@DataJpaTest`**.

---

## 1. Estrutura Canônica de Testes de Serviços com Mockito

Os testes de regras de negócio em `services/` devem ser puramente unitários, sem carregar o contexto pesado do Spring (`@SpringBootTest`), garantindo execução em milissegundos.

### 1.1 Anotações e Setup Padrão
```java
package com.fitoherb.fitoherb_backend_v2.services;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock private ProductRepository productRepository;
    @Mock private ProductCategoryRepository categoryRepository;
    @Mock private ProductMapper productMapper;

    @InjectMocks
    private ProductService productService;

    private Product productEntity;
    private ProductRes productRes;

    @BeforeEach
    void setup() {
        productEntity = new Product();
        productEntity.setId("uuid-teste");
        productEntity.setSlug("cha-verde");

        productRes = new ProductRes();
    }
```

---

## 2. Organização Semântica com `@Nested` e `@DisplayName`

Agrupe os testes em classes internas estáticas anotadas com `@Nested` para que o relatório de execução reflita as intenções de negócio:

```java
    @Nested
    @DisplayName("Cenários de Busca e Leitura")
    class RetrievalTests {

        @Test
        @DisplayName("Deve retornar detalhes do produto com sucesso quando o slug existir")
        void getProductBySlugSuccess() {
            when(productRepository.findBySlug("cha-verde")).thenReturn(Optional.of(productEntity));
            when(productMapper.entityToRes(productEntity)).thenReturn(productRes);

            ProductRes result = productService.getProductBySlug("cha-verde");

            assertNotNull(result);
            verify(productRepository, times(1)).findBySlug("cha-verde");
            verify(productMapper, times(1)).entityToRes(productEntity);
        }

        @Test
        @DisplayName("Deve lançar ResourceNotFoundException quando o slug não existir")
        void getProductBySlugNotFound() {
            when(productRepository.findBySlug("slug-inexistente")).thenReturn(Optional.empty());

            assertThrows(ResourceNotFoundException.class, () -> 
                productService.getProductBySlug("slug-inexistente")
            );

            verify(productRepository).findBySlug("slug-inexistente");
            verifyNoInteractions(productMapper);
        }
    }

    @Nested
    @DisplayName("Cenários de Criação e Cadastro")
    class CreationTests {

        @Test
        @DisplayName("Deve lançar ResourceAlreadyExistsException se o slug já estiver cadastrado")
        void createProductDuplicateSlug() {
            ProductReq req = new ProductReq();
            req.setName("Chá Verde");

            when(productRepository.existsBySlug(anyString())).thenReturn(true);

            assertThrows(ResourceAlreadyExistsException.class, () -> productService.createProduct(req));

            verify(productRepository, never()).save(any());
        }
    }
```

---

## 3. Mock de Consultas Dinâmicas (`Specification` & `Pageable`)

Para testar métodos de listagem que utilizam especificações dinâmicas e paginação:
```java
@Test
@DisplayName("Deve listar produtos paginados com filtros")
void getAllProductsPaginatedSuccess() {
    Page<Product> page = new PageImpl<>(List.of(productEntity));
    when(productRepository.findAll(any(Specification.class), any(Pageable.class))).thenReturn(page);
    when(productMapper.entityToRes(any())).thenReturn(productRes);

    Page<ProductRes> result = productService.getAllProductsPaginated("termo", null, null, 0, "name", "ASC");

    assertEquals(1, result.getTotalElements());
    verify(productRepository).findAll(any(Specification.class), any(Pageable.class));
}
```

---

## 4. Testes de Repositório com `@DataJpaTest` e Mock de Auditoria

Para validar queries customizadas do Spring Data JPA e constraints do banco sem subir a aplicação inteira:

```java
package com.fitoherb.fitoherb_backend_v2.repositories;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.data.domain.AuditorAware;
import org.springframework.test.context.ActiveProfiles;

import java.util.Optional;
import static org.junit.jupiter.api.Assertions.*;

@DataJpaTest
@ActiveProfiles("test")
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(ProductRepositoryTest.AuditorTestConfig.class)
class ProductRepositoryTest {

    @Autowired
    private ProductRepository productRepository;

    @TestConfiguration
    public static class AuditorTestConfig {
        @Bean(name = "auditorAwareImpl")
        public AuditorAware<String> auditorAwareImpl() {
            return () -> Optional.of("test-user");
        }
    }

    @BeforeEach
    void setup() {
        productRepository.deleteAll();
    }

    @Test
    @DisplayName("Deve persistir produto e preencher datas de auditoria automaticamente")
    void shouldPersistWithAuditDates() {
        Product p = new Product();
        p.setName("Camomila");
        p.setSlug("camomila");

        Product saved = productRepository.save(p);

        assertNotNull(saved.getId());
        assertNotNull(saved.getCreatedAt());
        assertEquals("test-user", saved.getCreatedBy());
    }
}
```

---

## Quality Gates
- [ ] Testes de serviço usam exclusivamente `@ExtendWith(MockitoExtension.class)` (zero `@SpringBootTest` para testes unitários de regras de negócio).
- [ ] Casos agrupados semanticamente com `@Nested` e `@DisplayName`.
- [ ] Cenários de exceção e caminho infeliz validados com `assertThrows` e verificação de não-interação (`never()`).
- [ ] Assertivas do JUnit 5 (`assertNotNull`, `assertEquals`, `assertTrue`) priorizadas.
- [ ] Testes de repositório isolados com `@DataJpaTest` e bean de auditoria mockado em `@TestConfiguration`.
