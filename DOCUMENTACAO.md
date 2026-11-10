# Citizen Assist AI — Segurança do Cidadão
GS 2026.2 | Data Structures and Algorithms | Python 3.8+

## 1. Recorte escolhido
Serviços e orientações de **segurança pública e proteção ao cidadão**: números de emergência (190, 192, 193), violência doméstica (180, medida protetiva), Defesa Civil (199), boletim de ocorrência online e orientações de segurança digital (golpes). O sistema organiza esses registros para consulta rápida.

## 2. Como executar
```
python citizen_assist.py          # abre o menu
python test_citizen_assist.py     # roda os 22 testes automatizados
```
Não há dependências externas. Os dados são salvos em `dados_servicos.json` ao encerrar (opcional); se o arquivo não existir ou estiver corrompido, o sistema carrega 8 registros iniciais.

## 3. Modelo dos registros (`Servico`)
| Campo | Descrição | Validação |
|---|---|---|
| id | Identificador único | Inteiro positivo, sem duplicidade |
| titulo | Nome do serviço | 3–80 caracteres |
| categoria | Ex.: Emergência, Violência doméstica | 3–40 caracteres |
| descricao | O que o serviço oferece | 5–300 caracteres |
| requisitos | Documentos/informações exigidos | 2–200 caracteres |
| local_atendimento | Onde ou como acessar | 2–120 caracteres |

## 4. Lista encadeada
- `No`: guarda um `Servico` (`dado`) e a referência `proximo`.
- `ListaEncadeada`: mantém `cabeca`, `cauda` e `tamanho`.
- Operações: `inserir_fim`, `percorrer` (gerador), `buscar_por_id`, `pesquisar`, `atualizar`, `remover` (cabeça, meio e fim, com ajuste da cauda) e `ordenar`.
- Os registros ficam **apenas** nos nós; nenhuma `list`/`dict` armazena os dados. O resultado de uma pesquisa é outra `ListaEncadeada`.

## 5. Algoritmos
**Busca (linear):** percorre nó a nó e para ao achar o ID. Na pesquisa por título/categoria, compara o termo como substring, ignorando maiúsculas e acentos (`normalizar`). Sem resultado, devolve `None` (consulta por ID) ou lista vazia (pesquisa), e o menu exibe mensagem clara.

**Ordenação (Merge Sort em lista encadeada):** divide a lista ao meio com ponteiros lento/rápido, ordena cada metade recursivamente e mescla religando os nós. É estável (usa `<=` na mescla) e não usa funções prontas de ordenação. Critérios: ID, título ou categoria (desempate por título).

**Análise:** total de registros e quantidade/percentual por categoria.

## 6. Complexidade (Big-O)
n = número de registros; m = tamanho do texto comparado; c = número de categorias distintas.

| Operação | Tempo | Justificativa |
|---|---|---|
| Inserção no fim | O(n) | A cauda dá O(1) para encadear, mas a checagem de ID duplicado percorre a lista. |
| Busca por ID | O(n) pior caso, O(1) melhor | Linear com parada antecipada. |
| Pesquisa por texto | O(n·m) | Uma comparação de substring por nó. |
| Atualização | O(n) | Localiza o nó; alterar campos é O(1). |
| Remoção | O(n) | Localiza o nó e religa ponteiros em O(1). |
| Ordenação (Merge Sort) | O(n log n) em todos os casos | log n níveis de divisão, O(n) de mescla por nível. Espaço extra O(log n) de pilha; a mescla religa nós sem copiar dados. |
| Análise por categoria | O(n·c) | Para cada nó, procura a categoria na contagem. |

## 7. Menu
`1` Cadastrar · `2` Consultar por ID · `3` Atualizar (Enter mantém o valor) · `4` Excluir (com confirmação) · `5` Pesquisar por título/categoria · `6` Ordenar e exibir · `7` Análise · `8` Listar na ordem atual · `0` Encerrar.
Entradas inválidas repetem a pergunta; opções inexistentes, IDs duplicados, consultas sem resultado e lista vazia têm mensagens próprias.

## 8. Evidências de testes (`test_citizen_assist.py`: 22 testes, todos OK)
| Caso | Entrada | Esperado | Observado |
|---|---|---|---|
| Lista vazia | buscar, remover, atualizar, ordenar, pesquisar, analisar | Sem erro; `None`/`False`/lista vazia | OK |
| Inserção | IDs 3, 1, 2 | Ordem 3, 1, 2; tamanho 3 | OK |
| ID duplicado | Inserir ID 1 de novo | `ValueError`; tamanho não muda | OK |
| Busca por ID | ID 2 / ID 99 | Registro / `None` | OK |
| Remoção | Cabeça, meio, fim, até esvaziar | Lista consistente; inserir depois funciona (cauda correta) | OK |
| Remoção inexistente | ID 99 | `False`; lista intacta | OK |
| Atualização válida | Novo título e categoria | Campos alterados | OK |
| Atualização inválida | Categoria em branco; campo `id` | `ValueError`; nada é alterado | OK |
| Pesquisa | "EMERGENCIA", "policia" | Acha "Emergência" e "Polícia" | OK |
| Pesquisa sem resultado | "inexistente" | Lista vazia | OK |
| Ordenação | Título, ID, categoria | Ordens corretas, tamanho preservado | OK |
| Estabilidade | 5 registros de mesma categoria | Ordem original mantida; inserção posterior no fim | OK |
| Lista grande | 500 registros em ordem inversa | 1..500 | OK |
| IDs inválidos | "", "abc", "-1", "0", "1.5", "1a" | `ValueError` | OK |
| Textos inválidos | Vazio, curto, longo | `ValueError` | OK |
| Menu | Opções "9", "abc", "" | "Opção inexistente" (3x) | OK |
| Cadastro pelo menu | ID "abc", ID 1 (duplicado), título vazio | Mensagens de erro e nova pergunta | OK |
| Consulta/pesquisa | ID 999; termo "zzzz"; opção 3 | Mensagens de "não encontrado"/"opção inválida" | OK |
| Exclusão | Cancelar (n) e confirmar (s) | "Exclusão cancelada" / "Registro removido" | OK |
| Persistência | Salvar, recarregar, JSON corrompido | Dados mantidos; corrompido cai nos dados iniciais | OK |
