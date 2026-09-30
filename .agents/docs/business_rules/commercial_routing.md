# Regras de Negócio: Roteirização Comercial Inteligente (P-100 a P-105)

Este documento define as regras de negócio normativas que regem o microserviço `fitoherb-ai`, o backend `fitoherb-backend-v2` e o frontend `fitoherb-frontend-v2`.

---

## [P-100] Perfil de Usuário Vendedor (SELLER) e Isolamento de Telas
1. O sistema deve suportar o perfil de usuário `SELLER` ("Vendedor") além de `ADMIN` e `USER`.
2. Usuários com o perfil `SELLER` possuem autorização restrita no painel administrativo (`/admin`):
   - **Permitido:** Visualizar e operar a aba **Rotas** e a aba **Alterar Senha**.
   - **Proibido:** Visualizar, listar, criar, editar ou excluir quaisquer entidades dos CRUDs administrativos (`Produtos`, `Categorias de Produtos`, `Fornecedores`, `Banners` e `Usuários`).
3. Administradores (`ADMIN`) possuem acesso irrestrito a todas as abas, incluindo a aba **Rotas**.

---

## [P-101] Gestão de Locais Salvos (`saved_locations`) e Definição de Ponto de Partida
1. O sistema deve manter a tabela `saved_locations` para persistência dos locais cadastrados por cada usuário.
2. Cada local possui a classificação `type` (`SavedLocationType`):
   - `BASE`: Ponto de partida do vendedor (residência ou base operacional).
   - `FAVORITE`: Parada ou cliente frequente (drogaria, farmácia, parceiro comercial).
3. **Regra de Base Única:** Cada vendedor pode manter apenas uma `BASE` ativa. Ao registrar um novo local com o tipo `BASE`, qualquer local anterior do mesmo usuário marcado como `BASE` deve ser desmarcado ou atualizado.
4. **Regra de Centralização Padrão do Mapa:**
   - **Com Base Definida:** Se o usuário autenticado possuir uma `BASE` cadastrada, ao abrir o mapa de rotas a visualização deve ser centralizada nas coordenadas da sua base (residência), configurando-a automaticamente como o ponto de partida do itinerário.
   - **Sem Base Definida (Fallback):** Se o usuário não possuir uma `BASE`, o mapa deve ser centralizado no endereço institucional da matriz Fitoherb:
     - Endereço: *Rua Itaeté, 434 - Pitangueiras, Lauro de Freitas - BA, CEP: 42701-360*
     - Coordenadas de Fallback: *Lat: -12.8992, Lon: -38.3242*

---

## [P-102] Captura Automática de Endereço via Geocodificação Reversa
1. Ao clicar no mapa ou realizar uma busca por endereço, o sistema deve executar a geocodificação reversa de forma transparente (via Nominatim / OpenStreetMap), obtendo os campos estruturados: logradouro (`street`), número (`number`), bairro (`neighborhood`), cidade (`city`), estado (`state`) e CEP (`postalCode`).
2. O formulário interativo exibido ao usuário não deve exigir a digitação manual de endereço nem de coordenadas, solicitando apenas:
   - Título/Nome do local (ex: "Drogaria São Paulo - Pituba").
   - Tipo do local (`BASE` ou `FAVORITE`).
   - Prioridade comercial (`REGULAR`, `ALTA` ou `URGENTE`).
   - Definição opcional de ordem fixa de parada (1ª, 2ª, etc.).

---

## [P-103] Roteamento Genético de Vendedor Único com Parâmetros Otimizados Fixos
1. A roteirização comercial é calculada para um **vendedor individual** (`num_vehicles = 1`), saindo do ponto de partida (Base ou Fitoherb HQ), visitando todas as paradas solicitadas e retornando à base.
2. Não há divisão de entregas em frotas ou múltiplas vans.
3. Os hiperparâmetros do Algoritmo Genético no `fitoherb-ai` são fixos e pré-otimizados em backend:
   - Tamanho da População: `50` indivíduos.
   - Gerações: `35` épocas.
   - Taxa de Mutação: `0.20`.
   - Taxa de Crossover (Locked-OX): `0.85`.
   - Elitismo: `2` melhores indivíduos preservados.
4. A interface do usuário não deve apresentar modais ou campos de configuração de hiperparâmetros do AG.

---

## [P-104] Fixação Manual de Ordem de Visita (Locked-Order)
1. O vendedor pode fixar uma ou mais paradas em posições específicas da sua rota (ex: definir Ponto X como a 1ª visita do dia e Ponto Y como a 4ª visita).
2. O motor genético deve validar que não haja colisões de posições manuais (`fixed_order`).
3. O algoritmo deve garantir que os pontos com posição fixada permaneçam inalterados em todas as gerações da evolução (através de cruzamento Locked-OX e mutação restrita a nós livres), otimizando estritamente a sequência das paradas intermediárias não fixadas.

---

## [P-105] Exportação de Roteiro Oficial em PDF sem Coordenadas Brutas
1. O vendedor deve poder exportar o plano de rota em formato PDF formatado com a identidade visual da Fitoherb.
2. O documento deve conter:
   - Cabeçalho com logotipo da Fitoherb, nome do vendedor, data e total de paradas.
   - Imagem estática/screenshot do mapa com a rota traçada e os marcadores numerados.
   - Resumo consolidado: Distância total percorrida (km) e tempo estimado de trânsito (horas/minutos).
   - Tabela sequencial com número da parada, título do cliente e endereço completo legível (rua, número, bairro e cidade).
3. **Privacidade e Usabilidade:** É terminantemente proibido exibir dados de latitude e longitude na interface de usuário e no PDF gerado. As coordenadas devem permanecer restritas aos cálculos viários matemáticos internos.

---

## [P-106] Horário Marcado no Cliente (Prioridade Máxima) e Detecção de Inviabilidade Viária
1. **Definição de Horário Específico:** O vendedor pode estipular um horário alvo de chegada (`target_arrival_time`, no formato `HH:MM`) em qualquer cliente/parada de visita ou intervalo de almoço.
2. **Prioridade Máxima no Algoritmo Genético:** O motor de otimização prioriza a chegada no horário marcado como restrição de máxima prioridade, ordenando os pontos cronologicamente e aplicando penalidade extrema caso a previsão viária atinja o ponto após o horário marcado.
3. **Minimização de Ociosidade e Chegada Otimizada Próxima ao Horário Marcado:**
   - O algoritmo genético penaliza severamente a chegada excessivamente antecipada ao horário marcado (`early_arrival_penalties`), além de uma margem de cortesia/segurança de 15 minutos.
   - Isso incentiva ativamente o algoritmo a preencher os períodos da manhã/tarde alocando outras paradas comerciais viáveis no trajeto, convergindo para o ponto marcado o mais próximo possível do horário estipulado (sempre antes ou pontual, ex: 10 a 15 minutos antes).
   - O vendedor pode ser roteado para pontos distantes no caminho pela manhã e depois retornar ao local marcado pontualmente para a visita.
   - Pontos com horário marcado futuro (> 30 min adiante do relógio atual) não sofrem penalidades do filtro anti-overshoot antes do seu horário de atendimento.
4. **Validação Imediata no Cadastro/Edição de Ponto:**
   - Se o usuário tentar agendar dois ou mais pontos cujos intervalos de atendimento se sobreponham (ex: Ponto A às 13:00 com 60 min de visita, e Ponto B às 13:30), o sistema emite um alerta imediato na janela de cadastro/edição advertindo que é humanamente impossível estar em ambos os locais simultaneamente.
5. **Detecção e Destaque de Inviabilidade no Itinerário da IA:**
   - Se, após a resolução viária com trânsito e tempos de deslocamento reais entre os endereços, for impossível chegar a tempo (ex: Ponto A às 13:00 com 50 min de atendimento + 20 min de deslocamento = chegada às 14:10 para horário marcado de 14:00), o sistema deve:
     - Sinalizar `has_any_time_conflict = true` e total de conflitos `time_conflict_count`.
     - Exibir um banner de alerta vermelho em destaque no topo da coluna de itinerário da IA.
     - Destacar o card da parada com borda e fundo avermelhados e pílula pulsante contendo a mensagem explicativa e o atraso em minutos (ex: *"Previsão de chegada às 14:10 (10 min após o horário marcado de 14:00)"*).
     - Quando o itinerário conseguir cumprir o horário marcado com sucesso, exibir uma pílula verde de confirmação (*"Marcado: 14:00 (No Horário)"*).

