/**
 * @file ExampleController.java
 * @description Exemplo de estrutura de um Controller REST usando Spring Boot.
 * Este arquivo serve como "Espelho" para a IA, impondo o uso de injeção de dependência via @RequiredArgsConstructor, 
 * anotações do Swagger e documentação (JavaDoc) exaustiva.
 */
package com.example.controllers;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Controller responsável por gerenciar as operações de exemplo na API.
 */
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/example")
@Tag(name = "Example", description = "Endpoints de exemplo para validação do fluxo da aplicação.")
public class ExampleController {

    /**
     * Serviço injetado automaticamente pelo Lombok via construtor final.
     */
    private final ExampleService exampleService;

    /**
     * Endpoint para buscar um recurso pelo seu identificador único.
     * 
     * @param id Identificador do recurso a ser buscado.
     * @return ResponseEntity contendo o ResponseDTO da entidade encontrada.
     */
    @Operation(summary = "Busca recurso por ID", description = "Retorna os detalhes de um recurso específico baseado no ID fornecido.")
    @GetMapping("/{id}")
    public ResponseEntity<ExampleResDTO> getById(@PathVariable Long id) {
        // O Controller não contém regra de negócio, apenas chama o serviço e retorna a resposta mapeada.
        ExampleResDTO response = exampleService.findById(id);
        return ResponseEntity.ok(response);
    }
}
