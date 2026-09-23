---
name: springboot-error-handling
description: Especialista em tratamento global de exceções no Spring Boot com @RestControllerAdvice, envelopes padronizados (RestErrorMessage / RestValidationErrorMessage) e mensagens amigáveis.
license: MIT
metadata:
  framework: Spring Boot 3+ / 4+, Bean Validation & Global Exceptions
  version: '1.0'
---

# Habilidade: Spring Boot Global Error Handling & Resilience ⚠️🛡️

## Propósito
Você é a autoridade técnica em Tratamento Global de Erros, Resiliência e Padronização de Respostas HTTP no ecossistema Spring Boot (Java 21), fundamentado nos padrões de produção do `fitoherb-backend-v2`. Sua missão é interceptar todas as falhas da aplicação através de um **`@RestControllerAdvice`** centralizado, eliminando *Stack Traces* em produção e retornando envelopes JSON estritamente tipados com mensagens claras e suporte a múltiplos erros de validação de formulários.

---

## 1. Modelos de Envelopes de Erro (`infra/exceptions/`)

A API NUNCA retorna mensagens soltas em texto puro. Utiliza dois envelopes padronizados:

### 1.1 Envelope para Erros Gerais (`RestErrorMessage.java`)
Para erros de negócio, autorização, autenticação e falhas internas:
```java
package com.fitoherb.fitoherb_backend_v2.infra.exceptions;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.http.HttpStatus;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class RestErrorMessage {
    private HttpStatus status;
    private String message;
}
```

### 1.2 Envelope para Erros de Validação (`RestValidationErrorMessage.java`)
Para capturar erros de Bean Validation (`@Valid`) associando cada campo à sua mensagem específica:
```java
package com.fitoherb.fitoherb_backend_v2.infra.exceptions;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.http.HttpStatus;

import java.util.Map;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
public class RestValidationErrorMessage {
    private HttpStatus status;
    private String message;
    private Map<String, String> fieldErrors;
}
```

---

## 2. O Interceptor Central (`RestExceptionHandler.java`)

```java
package com.fitoherb.fitoherb_backend_v2.infra.exceptions;

import com.fitoherb.fitoherb_backend_v2.exceptions.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.dao.InvalidDataAccessApiUsageException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authorization.AuthorizationDeniedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.HandlerMethodValidationException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestControllerAdvice
public class RestExceptionHandler {

    // 1. Falhas em DTOs anotados com @Valid (@RequestBody)
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<RestValidationErrorMessage> handleValidationExceptions(MethodArgumentNotValidException ex) {
        Map<String, String> fieldErrors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error ->
                fieldErrors.put(error.getField(), error.getDefaultMessage())
        );
        var response = new RestValidationErrorMessage(
                HttpStatus.BAD_REQUEST,
                "Falha na validação de um ou mais campos",
                fieldErrors
        );
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    // 2. Falhas em validações de @PathVariable ou @RequestParam
    @ExceptionHandler(HandlerMethodValidationException.class)
    public ResponseEntity<RestValidationErrorMessage> handleMethodValidation(HandlerMethodValidationException ex) {
        Map<String, String> fieldErrors = new HashMap<>();
        ex.getParameterValidationResults().forEach(result -> {
            String paramName = result.getMethodParameter().getParameterName();
            result.getResolvableErrors().forEach(error -> {
                fieldErrors.put(paramName, error.getDefaultMessage());
            });
        });
        var response = new RestValidationErrorMessage(
                HttpStatus.BAD_REQUEST,
                "Falha na validação de parâmetros da requisição",
                fieldErrors
        );
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    // 3. Recurso não encontrado (404)
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<RestErrorMessage> handleNotFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(new RestErrorMessage(HttpStatus.NOT_FOUND, ex.getMessage()));
    }

    // 4. Conflito / Recurso duplicado (409)
    @ExceptionHandler(ResourceAlreadyExistsException.class)
    public ResponseEntity<RestErrorMessage> handleConflict(ResourceAlreadyExistsException ex) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(new RestErrorMessage(HttpStatus.CONFLICT, ex.getMessage()));
    }

    // 5. Autenticação e Credenciais Inválidas (401)
    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<RestErrorMessage> handleBadCredentials(BadCredentialsException ex) {
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                .body(new RestErrorMessage(HttpStatus.UNAUTHORIZED, "E-mail ou senha inválidos."));
    }

    // 6. Autorização e Acesso Negado (403)
    @ExceptionHandler(AuthorizationDeniedException.class)
    public ResponseEntity<RestErrorMessage> handleForbidden(AuthorizationDeniedException ex) {
        return ResponseEntity.status(HttpStatus.FORBIDDEN)
                .body(new RestErrorMessage(HttpStatus.FORBIDDEN, "Acesso negado: permissões insuficientes."));
    }

    // 7. Violação de Integridade do Banco (ex: FK inexistente ou Unique)
    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<RestErrorMessage> handleDataIntegrity(DataIntegrityViolationException ex) {
        return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(new RestErrorMessage(HttpStatus.CONFLICT, "Violação de integridade: conflito com dados existentes."));
    }

    // 8. Payload JSON malformado ou tipo inválido
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<RestErrorMessage> handleNotReadable(HttpMessageNotReadableException ex) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new RestErrorMessage(HttpStatus.BAD_REQUEST, "Formato de dados inválido no corpo da requisição."));
    }

    // 9. Upload de arquivo excedendo o tamanho máximo
    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ResponseEntity<RestErrorMessage> handleMaxSize(MaxUploadSizeExceededException ex) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new RestErrorMessage(HttpStatus.BAD_REQUEST, "O arquivo enviado excedeu o limite máximo permitido (10MB)."));
    }

    // 10. Fallback Geral (500) - Log estruturado e proteção de informações sensíveis
    @ExceptionHandler(Exception.class)
    public ResponseEntity<RestErrorMessage> handleGeneral(Exception ex) {
        log.error("Exceção não tratada capturada pelo RestExceptionHandler: ", ex);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new RestErrorMessage(HttpStatus.INTERNAL_SERVER_ERROR, "Ocorreu um erro interno inesperado. Contate o administrador."));
    }
}
```

---

## 3. Catálogo de Exceções Customizadas de Domínio (`exceptions/`)

As regras de negócio em `services/` devem disparar exceções de runtime semânticas:
- **`ResourceNotFoundException`**: *"Produto não encontrado com o slug: cha-verde"*
- **`ResourceAlreadyExistsException`**: *"Já existe um fornecedor cadastrado com este CNPJ"*
- **`DatabaseOperationException`**: Falhas de transação ou persistência.
- **`InvalidTokenException`**: Falha no token JWT.
- **`UnauthorizedAccessException`**: Violação de isolamento multi-tenant ou tentativa de edição indevida.

---

## Quality Gates
- [ ] `@RestControllerAdvice` configurado capturando validações, banco, segurança e fallback geral.
- [ ] Respostas de validação retornam mapa de campos inválidos (`RestValidationErrorMessage`).
- [ ] Exceção genérica (`Exception.class`) registra log com `log.error` e oculta stack trace do usuário.
- [ ] Exceções de negócio utilizam classes de domínio customizadas derivadas de `RuntimeException`.
- [ ] Status HTTP semanticamente corretos para cada falha (`400`, `401`, `403`, `404`, `409`, `500`).
