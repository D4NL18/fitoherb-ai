---
name: springboot-jpa-audit
description: Especialista em persistência Spring Data JPA, entidades com UUID, auditoria automática (AuditingEntityListener), Specifications e paginação de alta performance.
license: MIT
metadata:
  framework: Spring Boot 3+ / 4+, Spring Data JPA & PostgreSQL
  version: '1.0'
---

# Habilidade: Spring Data JPA, UUID Entities & Automatic Auditing 🗄️⏱️

## Propósito
Você é a autoridade técnica em Modelagem de Entidades, Persistência com **Spring Data JPA**, chaves primárias **UUID** e **Auditoria Automática** no ecossistema Spring Boot (Java 21), fundamentado nos padrões do `fitoherb-backend-v2`. Sua missão é projetar entidades relacionais eficientes, sem problemas de *N+1 queries*, com rastreabilidade completa de criação e modificação (`AuditingEntityListener`) e suporte a filtros dinâmicos via `Specification`.

---

## 1. Padrão de Entidade com UUID e Auditoria JPA

Toda entidade JPA de produção deve seguir a convenção de identificador UUID, carregamento preguiçoso de relacionamentos e listener de auditoria:

```java
package com.fitoherb.fitoherb_backend_v2.entities;

import jakarta.persistence.*;
import lombok.*;
import org.springframework.data.annotation.CreatedBy;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedBy;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Table(name = "products")
@Entity(name = "products")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(of = "id")
@EntityListeners(AuditingEntityListener.class)
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String slug;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    // Relacionamentos SEMPRE com FetchType.LAZY para evitar N+1 queries
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private ProductCategory category;

    // Campos de Auditoria Automática
    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(name = "created_by", updatable = false)
    private String createdBy;

    @LastModifiedBy
    @Column(name = "updated_by")
    private String updatedBy;
}
```

---

## 2. Configuração do Auditor da Aplicação (`AuditorAwareImpl.java`)

Para que as anotações `@CreatedBy` e `@LastModifiedBy` capturem automaticamente o e-mail ou username do usuário logado:

```java
package com.fitoherb.fitoherb_backend_v2.infra.security;

import org.springframework.data.domain.AuditorAware;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.util.Optional;

@Component("auditorAwareImpl")
public class AuditorAwareImpl implements AuditorAware<String> {

    @Override
    public Optional<String> getCurrentAuditor() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || !authentication.isAuthenticated() || 
                authentication instanceof AnonymousAuthenticationToken) {
            return Optional.of("system");
        }

        return Optional.ofNullable(authentication.getName());
    }
}
```

E no `@Configuration` ou classe principal, ative a auditoria:
```java
@Configuration
@EnableJpaAuditing(auditorAwareRef = "auditorAwareImpl")
public class JpaConfig { ... }
```

---

## 3. Consultas Dinâmicas com `Specification` e Paginação

Em vez de criar dezenas de métodos complexos com `@Query`, utilize `JpaSpecificationExecutor<T>` para compor filtros dinâmicos sob demanda:

```java
public interface ProductRepository extends JpaRepository<Product, String>, JpaSpecificationExecutor<Product> {
    Optional<Product> findBySlug(String slug);
    boolean existsBySlug(String slug);
}
```

### Composição da Specification:
```java
public class ProductSpecifications {

    public static Specification<Product> withFilters(String search, List<String> categories) {
        return (root, query, cb) -> {
            var predicates = cb.conjunction();

            if (search != null && !search.isBlank()) {
                String pattern = "%" + search.toLowerCase() + "%";
                predicates = cb.and(predicates, cb.like(cb.lower(root.get("name")), pattern));
            }

            if (categories != null && !categories.isEmpty()) {
                predicates = cb.and(predicates, root.get("category").get("slug").in(categories));
            }

            return predicates;
        };
    }
}
```

### Execução Paginada no Service:
```java
Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.fromString(direction), sortBy));
Page<Product> productPage = productRepository.findAll(ProductSpecifications.withFilters(search, categories), pageable);
```

---

## Quality Gates
- [ ] Entidades usam `GenerationType.UUID` e `@EqualsAndHashCode(of = "id")`.
- [ ] Anotação `@EntityListeners(AuditingEntityListener.class)` presente nas entidades auditadas.
- [ ] Relacionamentos `@ManyToOne` e `@OneToOne` configurados com `fetch = FetchType.LAZY`.
- [ ] Beans de auditoria (`AuditorAware`) configurados e cobrindo requisições anônimas ("system").
- [ ] Repositórios com buscas compostas implementam `JpaSpecificationExecutor`.
- [ ] Paginação obrigatória em consultas de listagem aberta com `Pageable`.
