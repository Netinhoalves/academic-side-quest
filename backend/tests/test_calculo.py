import random
import uuid
from datetime import date
from decimal import Decimal

import pytest

from app import models
from app.calculo import (
    LimitesPPC,
    SolicitacaoAprovada,
    calcular_aproveitamento,
    calcular_pontos_aproveitados,
    recalcular_pontos_do_aluno,
)

D = lambda valor: Decimal(str(valor))  # noqa: E731

# Categoria 1 (subs 10 e 11), categoria 2 (sub 20)
LIMITES = LimitesPPC(
    total_pontos=D(100),
    categoria_total={1: D(40), 2: D(100)},
    categoria_semestre={1: D(20), 2: D(100)},
    subcategoria_semestre={10: D(8), 11: D(20), 20: D(100)},
)


def sol(id, dia, pontos, sub=10, cat=1, ano=2025, sem=1):
    return SolicitacaoAprovada(
        id=id,
        data_atividade=dia,
        ano=ano,
        semestre=sem,
        id_categoria=cat,
        id_subcategoria=sub,
        pontos_calculados=D(pontos),
    )


# ---------- Regra pura ----------

def test_menor_valor_entre_calculado_e_saldos():
    assert calcular_pontos_aproveitados(D(5), D(8), D(20), D(40), D(100)) == 5
    assert calcular_pontos_aproveitados(D(12), D(8), D(20), D(40), D(100)) == 8
    assert calcular_pontos_aproveitados(D(12), D(20), D(3), D(40), D(100)) == 3
    assert calcular_pontos_aproveitados(D(12), D(20), D(20), D(2), D(100)) == 2
    assert calcular_pontos_aproveitados(D(12), D(20), D(20), D(40), D(1)) == 1


def test_saldo_negativo_nao_gera_pontos_negativos():
    assert calcular_pontos_aproveitados(D(5), D(-3), D(20), D(40), D(100)) == 0


def test_dentro_dos_limites_aproveita_tudo():
    r = calcular_aproveitamento([sol(1, date(2025, 3, 1), 5)], LIMITES)
    assert r == {1: 5}


def test_limite_da_subcategoria_no_semestre():
    r = calcular_aproveitamento([sol(1, date(2025, 3, 1), 12)], LIMITES)
    assert r == {1: 8}


def test_limite_da_categoria_no_semestre():
    aprovadas = [
        sol(1, date(2025, 3, 1), 8, sub=10),
        sol(2, date(2025, 3, 2), 15, sub=11),
    ]
    r = calcular_aproveitamento(aprovadas, LIMITES)
    assert r == {1: 8, 2: 12}  # categoria no semestre: 20 - 8 = 12


def test_limite_da_categoria_no_curso():
    aprovadas = [
        sol(1, date(2025, 3, 1), 20, sub=11, ano=2025, sem=1),
        sol(2, date(2025, 9, 1), 20, sub=11, ano=2025, sem=2),
        sol(3, date(2026, 3, 1), 10, sub=11, ano=2026, sem=1),
    ]
    r = calcular_aproveitamento(aprovadas, LIMITES)
    assert r == {1: 20, 2: 20, 3: 0}  # 40 já usados no curso


def test_limite_total_do_ppc():
    limites = LimitesPPC(
        total_pontos=D(10),
        categoria_total={2: D(100)},
        categoria_semestre={2: D(100)},
        subcategoria_semestre={20: D(100)},
    )
    aprovadas = [sol(i, date(2025, 3, i), 7, sub=20, cat=2) for i in (1, 2, 3)]
    assert calcular_aproveitamento(aprovadas, limites) == {1: 7, 2: 3, 3: 0}


def test_novo_semestre_tem_saldo_novo():
    aprovadas = [
        sol(1, date(2025, 3, 1), 8, ano=2025, sem=1),
        sol(2, date(2025, 9, 1), 8, ano=2025, sem=2),
    ]
    assert calcular_aproveitamento(aprovadas, LIMITES) == {1: 8, 2: 8}


def test_saldo_nunca_fica_negativo():
    aprovadas = [sol(i, date(2025, 3, i), 9) for i in range(1, 8)]
    r = calcular_aproveitamento(aprovadas, LIMITES)
    assert all(v >= 0 for v in r.values())


def test_resultado_nao_depende_da_ordem_de_avaliacao():
    aprovadas = [
        sol(1, date(2025, 3, 10), 8),
        sol(2, date(2025, 3, 1), 8),  # mais antiga, mesmo avaliada depois
        sol(3, date(2025, 3, 10), 8),  # empate de data com o id 1: id menor primeiro
    ]
    esperado = calcular_aproveitamento(aprovadas, LIMITES)
    assert esperado == {2: 8, 1: 0, 3: 0}
    for _ in range(10):
        embaralhada = aprovadas[:]
        random.shuffle(embaralhada)
        assert calcular_aproveitamento(embaralhada, LIMITES) == esperado


def test_recusa_libera_saldo_para_as_seguintes():
    a = sol(1, date(2025, 3, 1), 8)
    b = sol(2, date(2025, 3, 2), 8)
    assert calcular_aproveitamento([a, b], LIMITES) == {1: 8, 2: 0}
    assert calcular_aproveitamento([b], LIMITES) == {2: 8}  # a foi recusada


@pytest.mark.skip(reason="Preencher com os valores do exemplo do documento (curso online de 15 horas) e os cenários do João")
def test_exemplo_do_documento_curso_online_15_horas():
    ...


# ---------- Com o banco (PPC TADS 2019 do seed_base) ----------
# Regra 3 = subcategoria 1.3 (cursos, 1 ponto por hora): limite 40 por
# semestre, categoria 1 com 80 por semestre e 120 no curso.

REGRA_CURSOS = 3


@pytest.fixture
def db():
    from app.database import SessionLocal

    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.rollback()  # nada deste teste fica no banco
        sessao.close()


@pytest.fixture
def aluno_novo(db):
    sufixo = uuid.uuid4().hex[:8]
    usuario = models.Usuario(
        nome=f"Aluno {sufixo}", email=f"calc{sufixo}@teste.local",
        senha_hash="x", matricula=f"C{sufixo}", id_perfil=1,
    )
    db.add(usuario)
    db.flush()
    aluno = models.Aluno(id_usuario=usuario.id, id_ppc=1, data_ingresso=date(2025, 1, 1))
    db.add(aluno)
    db.flush()
    return aluno


def solicitar(db, aluno, dia, pontos, status="APROVADA", ano=2025, semestre=1):
    s = models.Solicitacao(
        id_aluno=aluno.id,
        id_regra_pontuacao=REGRA_CURSOS,
        descricao_atividade="Curso de teste",
        data_atividade=dia,
        ano=ano,
        semestre=semestre,
        quantidade=D(pontos),
        arquivo="teste.pdf",
        pontos_calculados=D(pontos),
        status=status,
    )
    db.add(s)
    db.flush()
    return s


def test_recalcular_grava_pontos_aproveitados(db, aluno_novo):
    a = solicitar(db, aluno_novo, date(2025, 3, 1), 30)
    b = solicitar(db, aluno_novo, date(2025, 3, 2), 30)
    c = solicitar(db, aluno_novo, date(2025, 3, 3), 10, status="PENDENTE")

    recalcular_pontos_do_aluno(db, aluno_novo.id)

    assert (a.pontos_aproveitados, b.pontos_aproveitados) == (30, 10)
    assert c.pontos_aproveitados is None


def test_recalcular_apos_recusa_devolve_o_saldo(db, aluno_novo):
    a = solicitar(db, aluno_novo, date(2025, 3, 1), 30)
    b = solicitar(db, aluno_novo, date(2025, 3, 2), 30)
    recalcular_pontos_do_aluno(db, aluno_novo.id)
    assert b.pontos_aproveitados == 10

    a.status = "REJEITADA"
    recalcular_pontos_do_aluno(db, aluno_novo.id)

    assert a.pontos_aproveitados is None
    assert b.pontos_aproveitados == 30


def test_recalcular_aluno_que_nao_existe(db):
    with pytest.raises(ValueError):
        recalcular_pontos_do_aluno(db, 999999)