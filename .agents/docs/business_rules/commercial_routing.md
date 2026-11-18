# Regras de Negócio: Roteirização Comercial Inteligente (P-100 a P-109)

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

---

## [P-107] Relatório de Inteligência de Cidades da Rota (City Insights Report)
1. **Identificação Automática de Municípios:** Sempre que uma rota for prevista (`POST /api/v1/routing/optimize`) ou recalculada (`POST /api/v1/routing/recalculate`), o sistema DEVE extrair todas as cidades únicas que possuem pontos/paradas salvos na rota (incluindo a cidade-base caso possua paradas ou seja relevante ao roteiro, destacando os municípios com visitas ativas).
2. **Indicadores Demográficos, Econômicos e Comerciais por Cidade:** Para cada cidade com pontos na rota, o relatório (`city_insights`) DEVE apresentar informações estratégicas para apoiar o argumento de vendas e o planejamento comercial do vendedor Fitoherb:
   - **Nome do Município e UF** (ex.: *Feira de Santana - BA*) e **Código Oficial IBGE**.
   - **População Estimada (IBGE)** formatada e **Porte Demográfico / Classificação Comercial** (*Metrópole > 1M hab*, *Polo Regional 300k–1M hab*, *Cidade Média 100k–300k hab*, *Cidade de Pequeno Porte < 100k hab*).
   - **Densidade Demográfica** (`hab/km²`) e **Região / Polo Econômico** (ex.: *Região Metropolitana de Salvador*, *Portal do Sertão*, *Litoral Norte*, *Sul Baiano*).
   - **Potencial Econômico / PIB per capita estimado** e **Foco Comercial Recomendado Fitoherb** (ex.: *Alto giro em suplementos esportivos e redes de drogarias*, *Forte demanda por fitoterápicos tradicionais e farmácias independentes*).
   - **Métricas da Rota na Cidade:** Quantidade de paradas confirmadas do vendedor na cidade (`saved_stops_count`), quantidade de novas sugestões descobertas na cidade (`suggested_leads_count`) e tempo total estimado de permanência/atendimento comercial naquele município (`estimated_city_dwell_minutes`).
3. **Resiliência de Dados (IBGE + Base Curada + Fallback Dinâmico):**
   - O enriquecimento demográfico DEVE consultar cache local SQLite (`city_insights_cache`), base curada de municípios brasileiros/baianos e API de Localidades/Agregados do IBGE, com fallback determinístico por porte para nunca falhar ou atrasar a otimização caso o vendedor esteja com conexão instável.
4. **Exibição na Interface e no Manifesto PDF:**
   - Na tela de rotas (Aba *Roteiro da IA*), exibir o painel expansível/cards **"Relatório de Inteligência das Cidades da Rota"** logo acima ou integrado ao itinerário.
   - Na exportação do PDF (`P-105`), incluir um quadro resumo das cidades visitadas na rota com população, porte, nº de visitas e potencial comercial (respeitando a proibição de exibir coordenadas brutas).

---

## [P-108] Descoberta Proativa de Leads no Trajeto (Sugestão de Farmácias e Lojas de Produtos Naturais)
1. **Busca Automática de Oportunidades no Caminho:** Ao prever uma rota (`optimize`), o sistema DEVE pesquisar estabelecimentos comerciais do segmento alvo da Fitoherb situados ao redor das paradas/corredor viário e cidades da rota que **não estão listados** nos pontos atuais do vendedor.
2. **Segmentos Comerciais Alvo (Target POIs):**
   - **Farmácias, Drogarias e Manipulação:** tags OSM `amenity=pharmacy`, `healthcare=pharmacy`, `shop=chemist` e palavras-chave (`Farmácia`, `Drogaria`, `Manipulação`, `Farma`, `Droga`).
   - **Lojas de Produtos Naturais, Fitoterápicos e Suplementos:** tags OSM `shop=health_food`, `shop=herbalist`, `shop=nutrition_supplements`, `shop=vitamins` e palavras-chave (`Produtos Naturais`, `Natural`, `Ervanário`, `Fitoterápicos`, `Suplementos`, `Empório Natural`, `Vida Saudável`, `Bio`, `Nature`).
3. **Filtro Rigoroso de Deduplicação (Exclusão de Pontos Já Listados):**
   - O sistema NÃO DEVE sugerir estabelecimentos que já estejam na lista de paradas da rota (`stops`), na base de partida (`depot`) ou nos locais salvos/favoritos enviados pelo vendedor (`excluded_locations`).
   - Um estabelecimento candidato é considerado duplicado e descartado se:
     - Estiver a uma distância geodésica **<= 80 metros** (`0.08 km`) de qualquer ponto já listado na rota; **OU**
     - Possuir nome normalizado/fonético com alta similaridade (**>= 0.82**) na mesma cidade/bairro de um ponto já listado.
4. **Enriquecimento e Relevância Comercial da Sugestão:**
   - Cada sugestão descoberta DEVE conter: identificador único (`sug-...`), nome do estabelecimento, categoria comercial (`FARMACIA` ou `PRODUTOS_NATURAIS`), endereço legível (logradouro, número, bairro, cidade, UF), distância/desvio estimado a partir do ponto mais próximo da rota (`detour_distance_km` e `detour_time_minutes`) e marcador `is_suggestion = true`.
   - Limitar a quantidade de sugestões injetadas por previsão (ex.: top `5` a `8` melhores oportunidades ordenadas pelo menor desvio viário do corredor da rota) para não poluir o itinerário do vendedor.
5. **Provedor Multi-Camada Resiliente:**
   - Utilizar consulta espacial via **Overpass API (OpenStreetMap)** / **Photon Komoot** com cache SQLite de 7 dias por célula geográfica e fallback heurístico resiliente caso as APIs externas sofram timeout, garantindo que a otimização da rota nunca quebre.

---

## [P-109] Manejo em Lote (Staging/Batch) de Sugestões e Remoções com Recálculo Diferido
1. **Inserção Inicial como Sugestão na Lista da Rota:**
   - Ao concluir a previsão da rota, os novos estabelecimentos descobertos (`P-108`) são apresentados integrados à lista de manejo da rota (e no mapa com pino visual distinto de **Sugestão / Oportunidade**), devidamente identificados com a badge **`SUGESTÃO`** (`FARMÁCIA` / `LOJA NATURAL`) e o desvio estimado (`+X.X km`).
2. **Proibição de Recálculo Automático a Cada Clique Individual:**
   - Quando o vendedor estiver manejando a lista da rota — seja **removendo sugestões** que não deseja visitar, **confirmando/adicionando sugestões**, ou **removendo paradas** da lista — o sistema **NÃO DEVE disparar o recálculo da rota no backend a cada alteração individual**.
3. **Modo de Manejo de Lista (Batch Staging State):**
   - Toda remoção de sugestão, aceitação de sugestão ou exclusão de parada altera apenas o estado local de preparo (*staging* / `pendingStopsChanges = true`), marcando visualmente o contador de alterações pendentes (ex.: *"3 alterações pendentes na lista — Remova ou mantenha as sugestões desejadas e clique em Recalcular Rota ao finalizar"*).
   - O vendedor pode remover várias sugestões seguidas com resposta visual instantânea (`0 ms` de bloqueio de rede), limpar todas as sugestões não desejadas de uma só vez (*"Remover todas as sugestões"*) ou converter uma sugestão em cliente favorito salvo.
4. **Recálculo Único ao Finalizar o Manejo:**
   - Somente quando o vendedor clicar explicitamente no botão de confirmação **"Concluir Manejo e Recalcular Rota"** (barra de ação fixa/destacada no painel), o sistema envia a lista consolidada final de paradas mantidas para o motor de IA (`optimizeRoute` / `recalculateRoute`), recalcula o traçado viário OSRM, os horários e o relatório de cidades em **uma única chamada**, e persiste a rota atualizada.
   - O vendedor também dispõe da ação **"Desfazer / Restaurar Lista"** enquanto estiver no modo de manejo antes de confirmar o recálculo.
