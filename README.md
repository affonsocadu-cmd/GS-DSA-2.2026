# Citizen Assist AI — Segurança do Cidadão

Protótipo em **Python** desenvolvido para a **Global Solution 2026.2 (FIAP)**, na disciplina de **Data Structures and Algorithms (DSA)**.

O sistema organiza e permite consultar serviços e orientações de **segurança pública e proteção ao cidadão**, como números de emergência, canais de denúncia, Defesa Civil, boletim de ocorrência online e dicas de segurança digital. Tudo roda no terminal, sem dependências externas.

## Autores

| Nome | RM |
|---|---|
| Carlos Eduardo Affonso | 569676 |
| Igor Massone Monteiro | 573853 |

## Funcionalidades

- **Cadastro** de serviços com ID único e campos validados (título, categoria, descrição, requisitos e local de atendimento)
- **Consulta** por ID
- **Pesquisa** por título ou categoria, ignorando maiúsculas e acentos
- **Atualização** de registros (Enter mantém o valor atual)
- **Exclusão** com confirmação
- **Ordenação** por ID, título ou categoria
- **Análise** com o total de registros e a quantidade e o percentual por categoria
- **Persistência** opcional em JSON, salva ao encerrar o programa
- **Validações** para entradas inválidas, opções inexistentes, IDs duplicados, consultas sem resultado e lista vazia

## Estruturas de dados e algoritmos

- **Lista encadeada própria** (`No` e `ListaEncadeada`) com ponteiros para cabeça e cauda. Os registros ficam apenas nos nós, sem `list` ou `dict`.
- **Busca linear** por ID e por atributo de texto.
- **Merge Sort** implementado na própria lista encadeada. É estável e não usa funções prontas de ordenação.

| Operação | Complexidade |
|---|---|
| Inserção no fim | O(n), pela checagem de ID duplicado |
| Busca por ID | O(n) |
| Pesquisa por texto | O(n·m) |
| Atualização | O(n) |
| Remoção | O(n) |
| Ordenação (Merge Sort) | O(n log n) |

A justificativa de cada item está em [`DOCUMENTACAO.md`](DOCUMENTACAO.md).

## Como executar

Requisito: **Python 3.8 ou superior**.

```bash
# Clonar o repositório
git clone <https://github.com/affonsocadu-cmd/GS-DSA-2.2026>
cd <GS-DSA-2.2026>

# Executar o sistema
python citizen_assist.py        # no Windows também funciona: py citizen_assist.py

# Executar os testes automatizados
python test_citizen_assist.py
```

Ao abrir, o sistema carrega 8 registros iniciais, caso não exista um `dados_servicos.json`. Para voltar aos dados iniciais, apague esse arquivo.

## Menu

```
1 - Cadastrar        5 - Pesquisar
2 - Consultar por ID 6 - Ordenar e exibir
3 - Atualizar        7 - Análise
4 - Excluir          8 - Listar (ordem atual)
0 - Encerrar
```

## Testes

O arquivo `test_citizen_assist.py` traz 22 testes com `unittest`, cobrindo:

- operações com lista vazia
- inserção, busca e remoção (cabeça, meio e fim)
- IDs duplicados e entradas inválidas
- pesquisa com e sem resultado
- ordenação, estabilidade e lista grande
- fluxo do menu e persistência, incluindo JSON corrompido

## Estrutura do projeto

```
.
├── citizen_assist.py        # Sistema completo (modelo, lista, algoritmos e menu)
├── test_citizen_assist.py   # Testes automatizados
├── DOCUMENTACAO.md          # Documentação técnica e análise Big-O
└── README.md
```

> O arquivo `dados_servicos.json` é gerado automaticamente ao encerrar o programa. Se quiserem, adicionem-no ao `.gitignore`.
