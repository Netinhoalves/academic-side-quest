from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable

from sqlalchemy.orm import Session

from app import models

ZERO = Decimal("0")


@dataclass(frozen=True)
class LimitesPPC:
    total_pontos: Decimal
    categoria_total: dict[int, Decimal]  # Categoria.limite_total (no curso)
    categoria_semestre: dict[int, Decimal]  # Categoria.limite_semestre
    subcategoria_semestre: dict[int, Decimal]  # Subcategoria.limite_semestre


@dataclass(frozen=True)
class SolicitacaoAprovada:

    id: int
    data_atividade: date
    ano: int  # ano da solicitação
    semestre: int  # semestre da solicitação
    id_categoria: int
    id_subcategoria: int
    pontos_calculados: Decimal


def calcular_pontos_aproveitados(
    pontos_calculados: Decimal,
    saldo_subcategoria_semestre: Decimal,
    saldo_categoria_semestre: Decimal,
    saldo_categoria_curso: Decimal,
    saldo_ppc: Decimal,
) -> Decimal:
    return max(
        min(
            pontos_calculados,
            saldo_subcategoria_semestre,
            saldo_categoria_semestre,
            saldo_categoria_curso,
            saldo_ppc,
        ),
        ZERO,
    )


def calcular_aproveitamento(
    aprovadas: Iterable[SolicitacaoAprovada],
    limites: LimitesPPC,
) -> dict[int, Decimal]:
    usado_sub_sem: dict[tuple[int, int, int], Decimal] = {}
    usado_cat_sem: dict[tuple[int, int, int], Decimal] = {}
    usado_cat_curso: dict[int, Decimal] = {}
    usado_total = ZERO

    resultado: dict[int, Decimal] = {}
    for s in sorted(aprovadas, key=lambda x: (x.data_atividade, x.id)):
        k_sub = (s.id_subcategoria, s.ano, s.semestre)
        k_cat = (s.id_categoria, s.ano, s.semestre)

        aproveitados = calcular_pontos_aproveitados(
            s.pontos_calculados,
            limites.subcategoria_semestre[s.id_subcategoria] - usado_sub_sem.get(k_sub, ZERO),
            limites.categoria_semestre[s.id_categoria] - usado_cat_sem.get(k_cat, ZERO),
            limites.categoria_total[s.id_categoria] - usado_cat_curso.get(s.id_categoria, ZERO),
            limites.total_pontos - usado_total,
        )

        usado_sub_sem[k_sub] = usado_sub_sem.get(k_sub, ZERO) + aproveitados
        usado_cat_sem[k_cat] = usado_cat_sem.get(k_cat, ZERO) + aproveitados
        usado_cat_curso[s.id_categoria] = usado_cat_curso.get(s.id_categoria, ZERO) + aproveitados
        usado_total += aproveitados
        resultado[s.id] = aproveitados

    return resultado


def limites_do_ppc(ppc: models.PPC) -> LimitesPPC:
    """Monta os limites a partir do PPC (categorias e subcategorias já vêm do banco)."""
    return LimitesPPC(
        total_pontos=ppc.total_pontos,
        categoria_total={c.id: c.limite_total for c in ppc.categorias},
        categoria_semestre={c.id: c.limite_semestre for c in ppc.categorias},
        subcategoria_semestre={
            sub.id: sub.limite_semestre for c in ppc.categorias for sub in c.subcategorias
        },
    )


def recalcular_pontos_do_aluno(db: Session, id_aluno: int) -> dict[int, Decimal]:

    aluno = db.query(models.Aluno).filter(models.Aluno.id == id_aluno).with_for_update().first()
    if not aluno:
        raise ValueError(f"Aluno {id_aluno} não encontrado")

    solicitacoes = db.query(models.Solicitacao).filter(models.Solicitacao.id_aluno == id_aluno).with_for_update().all()
    aprovadas = [
        SolicitacaoAprovada(
            id=s.id,
            data_atividade=s.data_atividade,
            ano=s.ano,
            semestre=s.semestre,
            id_categoria=s.regra.subcategoria.id_categoria,
            id_subcategoria=s.regra.id_subcategoria,
            pontos_calculados=s.pontos_calculados,
        )
        for s in solicitacoes
        if s.status == "APROVADA"
    ]

    resultado = calcular_aproveitamento(aprovadas, limites_do_ppc(aluno.ppc))
    for s in solicitacoes:
        s.pontos_aproveitados = resultado.get(s.id)
    db.flush()
    return resultado