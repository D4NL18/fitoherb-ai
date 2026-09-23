---
name: springboot-security
description: Especialista em Spring Security, autenticação Stateless JWT (Auth0), suporte dual (Cookie HttpOnly + Bearer), CORS avançado e autorização declarativa @PreAuthorize.
license: MIT
metadata:
  framework: Spring Boot 3+ / 4+, Spring Security & Auth0 JWT
  version: '1.0'
---

# Habilidade: Spring Boot Security & JWT Architecture 🔐🛡️

## Propósito
Você é a autoridade técnica em Segurança, Autenticação e Controle de Acesso no ecossistema Spring Boot (Java 21), fundamentado nos padrões de produção do `fitoherb-backend-v2`. Sua missão é desenhar e manter uma arquitetura de segurança moderna, **Stateless**, com suporte simultâneo a **Cookies HttpOnly** e cabeçalhos **Bearer JWT (Auth0)**, controle granular via SpEL com **`@PreAuthorize`**, proteção contra vulnerabilidades comuns e configuração de CORS para múltiplos domínios.

---

## 1. Configuração Central do Filtro de Segurança (`SecurityConfigurations.java`)

```java
package com.fitoherb.fitoherb_backend_v2.infra.security;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfigurations {

    private final SecurityFilter securityFilter;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity httpSecurity) throws Exception {
        return httpSecurity
                .csrf(csrf -> csrf.disable()) // Stateless APIs não usam CSRF tradicional
                .cors(org.springframework.security.config.Customizer.withDefaults())
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(authorize -> authorize
                        .requestMatchers("/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html").permitAll()
                        .requestMatchers("/auth/**", "/public/**").permitAll()
                        .anyRequest().permitAll() // O controle fino de acesso é delegado ao @PreAuthorize
                )
                .addFilterBefore(securityFilter, UsernamePasswordAuthenticationFilter.class)
                .build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(List.of(
                "http://localhost:4200",
                "https://app.empresa.com.br"
        ));
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

---

## 2. Filtro de Autenticação Dual (`SecurityFilter.java`)

O filtro intercepta requisições HTTP e recupera o token tanto de **Cookies HttpOnly** (padrão de proteção Web/SPA contra XSS) quanto do cabeçalho **`Authorization: Bearer`** (clientes mobile e ferramentas):

```java
package com.fitoherb.fitoherb_backend_v2.infra.security;

import com.fitoherb.fitoherb_backend_v2.exceptions.InvalidTokenException;
import com.fitoherb.fitoherb_backend_v2.repositories.UserRepository;
import com.fitoherb.fitoherb_backend_v2.services.TokenService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
@RequiredArgsConstructor
public class SecurityFilter extends OncePerRequestFilter {

    private final TokenService tokenService;
    private final UserRepository userRepository;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) 
            throws ServletException, IOException {
        try {
            var token = recoverToken(request);
            if (token != null && !request.getRequestURI().contains("/auth/refresh")) {
                var email = tokenService.validateToken(token);
                userRepository.findByEmail(email).ifPresent(user -> {
                    var authentication = new UsernamePasswordAuthenticationToken(user, null, user.getAuthorities());
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                });
            }
            filterChain.doFilter(request, response);
        } catch (InvalidTokenException e) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.setCharacterEncoding("UTF-8");
            response.setContentType("application/json");
            response.getWriter().write("{ \"status\": \"401 UNAUTHORIZED\", \"message\": \"" + e.getMessage() + "\" }");
        }
    }

    private String recoverToken(HttpServletRequest request) {
        // 1. Tenta recuperar do Cookie seguro HttpOnly
        if (request.getCookies() != null) {
            for (Cookie cookie : request.getCookies()) {
                if ("app_jwt".equals(cookie.getName())) {
                    String val = cookie.getValue();
                    if (val != null && val.startsWith("\"") && val.endsWith("\"") && val.length() >= 2) {
                        return val.substring(1, val.length() - 1);
                    }
                    return val;
                }
            }
        }
        // 2. Fallback para cabeçalho Authorization: Bearer
        var authHeader = request.getHeader("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            return authHeader.substring(7);
        }
        return null;
    }
}
```

---

## 3. Emissão e Validação Criptográfica de JWT (`TokenService.java`)

Utilizando a biblioteca oficial `com.auth0:java-jwt`:
```java
@Service
public class TokenService {

    @Value("${api.security.token.secret}")
    private String secret;

    public String generateToken(User user) {
        try {
            Algorithm algorithm = Algorithm.HMAC256(secret);
            return JWT.create()
                    .withIssuer("fitoherb-api")
                    .withSubject(user.getEmail())
                    .withClaim("role", user.getRole().name())
                    .withExpiresAt(genExpirationDate())
                    .sign(algorithm);
        } catch (JWTCreationException exception) {
            throw new RuntimeException("Erro ao gerar token JWT", exception);
        }
    }

    public String validateToken(String token) {
        try {
            Algorithm algorithm = Algorithm.HMAC256(secret);
            return JWT.require(algorithm)
                    .withIssuer("fitoherb-api")
                    .build()
                    .verify(token)
                    .getSubject();
        } catch (JWTVerificationException exception) {
            throw new InvalidTokenException("Token JWT inválido ou expirado.");
        }
    }

    private Instant genExpirationDate() {
        return LocalDateTime.now().plusHours(2).toInstant(ZoneOffset.of("-03:00"));
    }
}
```

---

## 4. Autorização Declarativa nos Controllers (`AuthorizationService.java`)

Para evitar dependências circulares durante a inicialização, utilize `ObjectProvider`:
```java
@Service
@RequiredArgsConstructor
public class AuthorizationService implements UserDetailsService {

    private final ObjectProvider<AuthenticationManager> authManagerProvider;
    private final ObjectProvider<PasswordEncoder> passwordEncoderProvider;

    public boolean isAuthenticated() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        return auth != null && auth.isAuthenticated() && !(auth instanceof AnonymousAuthenticationToken);
    }

    public boolean isAdmin() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated() || auth instanceof AnonymousAuthenticationToken) {
            return false;
        }
        return auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
    }
}
```

### Uso nos Controllers:
```java
@PreAuthorize("@authorizationService.isAuthenticated()")
@GetMapping("/me")
public ResponseEntity<UserRes> getProfile() { ... }

@PreAuthorize("@authorizationService.isAdmin()")
@DeleteMapping("/{id}")
public ResponseEntity<Void> delete(@PathVariable String id) { ... }
```

---

## Quality Gates
- [ ] Sessões configuradas como 100% Stateless (`SessionCreationPolicy.STATELESS`).
- [ ] CSRF desativado para endpoints de API REST JSON.
- [ ] Suporte dual implementado: Cookie HttpOnly para Web e Header Bearer para Mobile/Swagger.
- [ ] Validação criptográfica de JWT com biblioteca Auth0 (`java-jwt`).
- [ ] Proteção de rotas com autorização declarativa `@PreAuthorize`.
- [ ] Senhas criptografadas exclusivamente com `BCryptPasswordEncoder`.
- [ ] CORS configurado com restrição explícita de origens permitidas e credenciais.
