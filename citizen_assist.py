"""
Citizen Assist AI - Recorte: Segurança Pública e Proteção ao Cidadão
GS 2026.2 | Data Structures and Algorithms | Python

Estruturas implementadas pela equipe (sem list/dict para armazenar os registros):
  - Servico        : registro (modelo de dados)
  - No             : nó da lista encadeada
  - ListaEncadeada : inserção, percurso, busca, atualização, remoção e Merge Sort
"""
import json
import os
import unicodedata

ARQUIVO_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_servicos.json")


# ----------------------------------------------------------------------------
# Utilitários e validação
# ----------------------------------------------------------------------------
def normalizar(texto):
    """Minúsculas e sem acentos, para comparações de busca/ordenação."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return sem_acento.casefold().strip()


def validar_id(texto):
    """Converte para inteiro positivo ou levanta ValueError."""
    texto = str(texto).strip()
    if not texto:
        raise ValueError("O identificador não pode ficar vazio.")
    if not texto.isdigit() or int(texto) <= 0:
        raise ValueError("O identificador deve ser um número inteiro positivo.")
    return int(texto)


def validar_texto(texto, campo, minimo=3, maximo=200):
    """Valida campo textual obrigatório e devolve o texto sem espaços nas pontas."""
    texto = str(texto).strip()
    if not texto:
        raise ValueError(f"O campo '{campo}' é obrigatório.")
    if len(texto) < minimo:
        raise ValueError(f"O campo '{campo}' precisa ter ao menos {minimo} caracteres.")
    if len(texto) > maximo:
        raise ValueError(f"O campo '{campo}' excede {maximo} caracteres.")
    return texto


CAMPOS_EDITAVEIS = ("titulo", "categoria", "descricao", "requisitos", "local_atendimento")


# ----------------------------------------------------------------------------
# Modelo de dados
# ----------------------------------------------------------------------------
class Servico:
    """Registro de um serviço/orientação de segurança ao cidadão."""

    def __init__(self, id, titulo, categoria, descricao, requisitos, local_atendimento):
        self.id = validar_id(id)
        self.titulo = validar_texto(titulo, "título", 3, 80)
        self.categoria = validar_texto(categoria, "categoria", 3, 40)
        self.descricao = validar_texto(descricao, "descrição", 5, 300)
        self.requisitos = validar_texto(requisitos, "requisitos", 2, 200)
        self.local_atendimento = validar_texto(local_atendimento, "local de atendimento", 2, 120)

    def para_dict(self):
        return {"id": self.id, "titulo": self.titulo, "categoria": self.categoria,
                "descricao": self.descricao, "requisitos": self.requisitos,
                "local_atendimento": self.local_atendimento}

    def __str__(self):
        return (f"[{self.id}] {self.titulo}\n"
                f"    Categoria : {self.categoria}\n"
                f"    Descrição : {self.descricao}\n"
                f"    Requisitos: {self.requisitos}\n"
                f"    Local     : {self.local_atendimento}")


# ----------------------------------------------------------------------------
# Lista encadeada
# ----------------------------------------------------------------------------
class No:
    """Nó: guarda um Servico e a referência para o próximo nó."""

    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class ListaEncadeada:
    """Lista simplesmente encadeada com ponteiros para cabeça e cauda."""

    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self.tamanho = 0

    def esta_vazia(self):
        return self.cabeca is None

    # -- inserção: O(n) por causa da checagem de ID duplicado (o encadeamento em si é O(1))
    def inserir_fim(self, servico):
        if self.buscar_por_id(servico.id) is not None:
            raise ValueError(f"Já existe um registro com o ID {servico.id}.")
        novo = No(servico)
        if self.cabeca is None:
            self.cabeca = self.cauda = novo
        else:
            self.cauda.proximo = novo
            self.cauda = novo
        self.tamanho += 1

    # -- percurso: O(n)
    def percorrer(self):
        atual = self.cabeca
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    # -- busca por ID (linear com parada antecipada): O(n)
    def buscar_por_id(self, id):
        atual = self.cabeca
        while atual is not None:
            if atual.dado.id == id:
                return atual.dado
            atual = atual.proximo
        return None

    # -- busca por atributo (substring, sem acento/maiúsculas): O(n * m)
    def pesquisar(self, atributo, termo):
        """Devolve uma NOVA ListaEncadeada com os registros encontrados (vazia se nenhum)."""
        termo = normalizar(termo)
        resultado = ListaEncadeada()
        atual = self.cabeca
        while atual is not None:
            if termo in normalizar(getattr(atual.dado, atributo)):
                resultado.inserir_fim(atual.dado)  # IDs já são únicos
            atual = atual.proximo
        return resultado

    # -- atualização: O(n); valida tudo antes de alterar (all-or-nothing)
    def atualizar(self, id_servico, **campos):
        servico = self.buscar_por_id(id_servico)
        if servico is None:
            return False
        limites = {"titulo": (3, 80), "categoria": (3, 40), "descricao": (5, 300),
                   "requisitos": (2, 200), "local_atendimento": (2, 120)}
        novos = {}
        for nome, valor in campos.items():
            if nome not in CAMPOS_EDITAVEIS:
                raise ValueError(f"Campo '{nome}' não pode ser atualizado.")
            novos[nome] = validar_texto(valor, nome.replace("_", " "), *limites[nome])
        for nome, valor in novos.items():
            setattr(servico, nome, valor)
        return True

    # -- remoção: O(n)
    def remover(self, id):
        anterior, atual = None, self.cabeca
        while atual is not None and atual.dado.id != id:
            anterior, atual = atual, atual.proximo
        if atual is None:
            return False
        if anterior is None:                 # remove a cabeça
            self.cabeca = atual.proximo
        else:                                # remove meio ou fim
            anterior.proximo = atual.proximo
        if atual is self.cauda:              # mantém a cauda consistente
            self.cauda = anterior
        atual.proximo = None
        self.tamanho -= 1
        return True

    # -- ordenação: Merge Sort em lista encadeada, O(n log n), estável
    def ordenar(self, chave):
        """Reordena a lista in-place religando os nós. `chave` recebe um Servico."""
        self.cabeca = self._merge_sort(self.cabeca, chave)
        self.cauda = self.cabeca
        while self.cauda is not None and self.cauda.proximo is not None:
            self.cauda = self.cauda.proximo

    def _merge_sort(self, cabeca, chave):
        if cabeca is None or cabeca.proximo is None:
            return cabeca
        esquerda, direita = self._dividir(cabeca)
        return self._mesclar(self._merge_sort(esquerda, chave),
                             self._merge_sort(direita, chave), chave)

    @staticmethod
    def _dividir(cabeca):
        """Divide ao meio com ponteiros lento/rápido."""
        lento, rapido = cabeca, cabeca.proximo
        while rapido is not None and rapido.proximo is not None:
            lento = lento.proximo
            rapido = rapido.proximo.proximo
        meio = lento.proximo
        lento.proximo = None
        return cabeca, meio

    @staticmethod
    def _mesclar(a, b, chave):
        sentinela = No(None)
        atual = sentinela
        while a is not None and b is not None:
            if chave(a.dado) <= chave(b.dado):   # <= mantém estabilidade
                atual.proximo, a = a, a.proximo
            else:
                atual.proximo, b = b, b.proximo
            atual = atual.proximo
        atual.proximo = a if a is not None else b
        return sentinela.proximo


CRITERIOS_ORDENACAO = {
    "1": ("ID", lambda s: s.id),
    "2": ("Título", lambda s: normalizar(s.titulo)),
    "3": ("Categoria (depois título)", lambda s: (normalizar(s.categoria), normalizar(s.titulo))),
}


# ----------------------------------------------------------------------------
# Processamento / análise
# ----------------------------------------------------------------------------
def contar_por_categoria(lista):
    """Devolve [(categoria, quantidade), ...] em ordem de aparição. O(n * c)."""
    contagem = []
    for s in lista.percorrer():
        for i, (cat, qtd) in enumerate(contagem):
            if normalizar(cat) == normalizar(s.categoria):
                contagem[i] = (cat, qtd + 1)
                break
        else:
            contagem.append((s.categoria, 1))
    return contagem


# ----------------------------------------------------------------------------
# Persistência (opcional)
# ----------------------------------------------------------------------------
def salvar(lista, caminho):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump([s.para_dict() for s in lista.percorrer()], f, ensure_ascii=False, indent=2)


def carregar(caminho):
    """Carrega do JSON; devolve None se o arquivo não existir ou estiver inválido."""
    if not os.path.exists(caminho):
        return None
    try:
        with open(caminho, encoding="utf-8") as f:
            itens = json.load(f)
        lista = ListaEncadeada()
        for item in itens:
            lista.inserir_fim(Servico(**item))
        return lista
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None


def dados_iniciais():
    lista = ListaEncadeada()
    base = [
        (1, "Polícia Militar - Emergência (190)", "Emergência",
         "Atendimento 24h para crimes em andamento e situações de risco imediato.",
         "Informar endereço e descrição da ocorrência.", "Telefone 190"),
        (2, "SAMU - Emergência médica (192)", "Emergência",
         "Socorro médico em casos de urgência, acidentes e mal súbito.",
         "Informar endereço, estado da vítima e ponto de referência.", "Telefone 192"),
        (3, "Corpo de Bombeiros (193)", "Emergência",
         "Combate a incêndios, resgates e salvamentos.",
         "Informar endereço e tipo de ocorrência.", "Telefone 193"),
        (4, "Central de Atendimento à Mulher (180)", "Violência doméstica",
         "Recebe denúncias e orienta mulheres em situação de violência, de forma gratuita.",
         "Nenhum documento exigido.", "Telefone 180"),
        (5, "Solicitação de medida protetiva", "Violência doméstica",
         "Pedido de medidas de proteção para vítimas de violência doméstica.",
         "Documento com foto e relato dos fatos.", "Delegacia de Defesa da Mulher"),
        (6, "Boletim de ocorrência online", "Documentação",
         "Registro de ocorrências de menor gravidade, como furto e perda de documentos.",
         "CPF, documento com foto e dados da ocorrência.", "Delegacia eletrônica"),
        (7, "Defesa Civil (199)", "Defesa Civil",
         "Orientação e acionamento em risco de enchente, deslizamento e desabamento.",
         "Informar endereço e tipo de risco.", "Telefone 199"),
        (8, "Como evitar golpes por mensagem e telefone", "Segurança digital",
         "Orientações: não compartilhar códigos, desconfiar de urgência e confirmar por canal oficial.",
         "Nenhum.", "Material informativo online"),
    ]
    for item in base:
        lista.inserir_fim(Servico(*item))
    return lista


# ----------------------------------------------------------------------------
# Interface (terminal)
# ----------------------------------------------------------------------------
def ler_texto(rotulo, minimo=3, maximo=200, atual=None):
    """Pede um texto repetindo até ser válido. Se `atual` for dado, Enter mantém o valor."""
    while True:
        sufixo = f" [{atual}]" if atual is not None else ""
        bruto = input(f"{rotulo}{sufixo}: ")
        if atual is not None and not bruto.strip():
            return atual
        try:
            return validar_texto(bruto, rotulo.lower(), minimo, maximo)
        except ValueError as erro:
            print(f"  ! {erro}")


def ler_id(rotulo="ID"):
    while True:
        try:
            return validar_id(input(f"{rotulo}: "))
        except ValueError as erro:
            print(f"  ! {erro}")


def mostrar(lista):
    if lista.esta_vazia():
        print("Nenhum registro para exibir.")
        return
    for s in lista.percorrer():
        print(s)
        print()


def opcao_cadastrar(lista):
    print("\n-- Cadastrar --")
    while True:
        novo_id = ler_id()
        if lista.buscar_por_id(novo_id) is None:
            break
        print(f"  ! Já existe um registro com o ID {novo_id}. Informe outro.")
    servico = Servico(novo_id,
                      ler_texto("Título", 3, 80), ler_texto("Categoria", 3, 40),
                      ler_texto("Descrição", 5, 300), ler_texto("Requisitos", 2, 200),
                      ler_texto("Local de atendimento", 2, 120))
    lista.inserir_fim(servico)
    print("Registro cadastrado com sucesso.")


def opcao_consultar(lista):
    print("\n-- Consultar por ID --")
    if lista.esta_vazia():
        print("A lista está vazia.")
        return
    s = lista.buscar_por_id(ler_id())
    print(s if s else "Nenhum registro encontrado com esse ID.")


def opcao_atualizar(lista):
    print("\n-- Atualizar (Enter mantém o valor atual) --")
    if lista.esta_vazia():
        print("A lista está vazia.")
        return
    s = lista.buscar_por_id(ler_id())
    if s is None:
        print("Nenhum registro encontrado com esse ID.")
        return
    lista.atualizar(s.id,
                    titulo=ler_texto("Título", 3, 80, s.titulo),
                    categoria=ler_texto("Categoria", 3, 40, s.categoria),
                    descricao=ler_texto("Descrição", 5, 300, s.descricao),
                    requisitos=ler_texto("Requisitos", 2, 200, s.requisitos),
                    local_atendimento=ler_texto("Local de atendimento", 2, 120, s.local_atendimento))
    print("Registro atualizado.")


def opcao_excluir(lista):
    print("\n-- Excluir --")
    if lista.esta_vazia():
        print("A lista está vazia.")
        return
    s = lista.buscar_por_id(ler_id())
    if s is None:
        print("Nenhum registro encontrado com esse ID.")
        return
    print(s)
    if input("Confirmar exclusão? (s/n): ").strip().lower() == "s":
        lista.remover(s.id)
        print("Registro removido.")
    else:
        print("Exclusão cancelada.")


def opcao_pesquisar(lista):
    print("\n-- Pesquisar --")
    if lista.esta_vazia():
        print("A lista está vazia.")
        return
    escolha = input("Pesquisar por (1) Título ou (2) Categoria: ").strip()
    if escolha not in ("1", "2"):
        print("Opção inválida.")
        return
    termo = ler_texto("Termo de busca", 1, 80)
    achados = lista.pesquisar("titulo" if escolha == "1" else "categoria", termo)
    if achados.esta_vazia():
        print(f"Nenhum registro encontrado para '{termo}'.")
    else:
        print(f"{achados.tamanho} registro(s) encontrado(s):\n")
        mostrar(achados)


def opcao_ordenar(lista):
    print("\n-- Ordenar e exibir --")
    if lista.esta_vazia():
        print("A lista está vazia.")
        return
    escolha = input("Critério: (1) ID  (2) Título  (3) Categoria: ").strip()
    if escolha not in CRITERIOS_ORDENACAO:
        print("Critério inválido.")
        return
    nome, chave = CRITERIOS_ORDENACAO[escolha]
    lista.ordenar(chave)
    print(f"Lista ordenada por {nome} (Merge Sort):\n")
    mostrar(lista)


def opcao_analise(lista):
    print("\n-- Análise --")
    print(f"Total de registros: {lista.tamanho}")
    if lista.esta_vazia():
        return
    print("Registros por categoria:")
    for cat, qtd in contar_por_categoria(lista):
        print(f"  {cat:<25} {qtd:>3}  ({qtd * 100 / lista.tamanho:.0f}%)")


MENU = """
===== Citizen Assist AI - Segurança do Cidadão =====
1 - Cadastrar        5 - Pesquisar
2 - Consultar por ID 6 - Ordenar e exibir
3 - Atualizar        7 - Análise
4 - Excluir          8 - Listar (ordem atual)
0 - Encerrar
"""


def main(arquivo=ARQUIVO_PADRAO):
    lista = carregar(arquivo) if arquivo else None
    if lista is None:
        lista = dados_iniciais()
    acoes = {"1": opcao_cadastrar, "2": opcao_consultar, "3": opcao_atualizar,
             "4": opcao_excluir, "5": opcao_pesquisar, "6": opcao_ordenar,
             "7": opcao_analise, "8": lambda l: (print(), mostrar(l))}
    try:
        while True:
            print(MENU)
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "0":
                break
            if opcao in acoes:
                acoes[opcao](lista)
            else:
                print("Opção inexistente. Escolha um número do menu.")
    except (EOFError, KeyboardInterrupt):
        print()
    if arquivo:
        salvar(lista, arquivo)
    print("Encerrando. Dados salvos. Até logo!")


if __name__ == "__main__":
    main()
