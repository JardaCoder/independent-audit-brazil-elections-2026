"""Audita os logs (logd.dat) das urnas do 2º turno de 2026 e cruza com o BU impresso.

    python3 analise/logs_urna.py AC RR AP
"""
import io
import os
import sys
import zipfile
from collections import Counter

import pandas as pd

from carregar import FUSO
from imagem_bu import PASTA_URNA, parse

DIA = "25/10/2026"


def linhas_log(jez):
    """Linhas de todos os logd.dat do pacote, inclusive os logs arquivados de urnas substituídas."""
    out = []
    with zipfile.ZipFile(io.BytesIO(jez)) as z:
        for n in z.namelist():
            if n.endswith("logd.dat"):
                out += z.read(n).decode("latin1").splitlines()
            elif n.endswith(".jez"):
                out += linhas_log(z.read(n))
    return out


def eventos_secao(log_jez):
    """Percorre o log do dia da eleição eleitor a eleitor e classifica cada habilitação."""
    # Cada logd.dat é lido na ordem original do arquivo; logs de urnas substituídas vêm em sequência (não se sobrepõem).
    linhas = linhas_log(log_jez)
    r, votos_hora, manuais_hora, mesarios, erros = Counter(), Counter(), Counter(), Counter(), Counter()
    ultimo_voto = None
    tipo, mesario, recusou, votou = None, None, False, False
    for ln in linhas:
        if not ln.startswith(DIA):
            continue
        partes = ln.split("\t")
        if len(partes) < 5:
            continue
        hora, nivel, msg = partes[0][11:], partes[1], partes[4]
        if msg.startswith("Aguardando digitação do identificador do eleitor"):
            if recusou and not votou:
                r["sessoes_recusadas_sem_voto"] += 1
            tipo, mesario, recusou, votou = None, None, False, False
        elif msg.startswith("Tipo de habilitação do eleitor [biométrica]"):
            tipo = "biometrica"
        elif msg.startswith("Solicitação de dado pessoal do eleitor para habilitação manual"):
            tipo = "manual"
        elif msg.startswith("Dado digitado não confere"):
            r["dado_pessoal_recusado"] += 1
            recusou = True
        elif msg.startswith("Ano de nascimento digitado é igual ao do cadastro"):
            tipo = "sem_biometria"
        elif msg.startswith("Mesário") and msg.endswith("habilitou o eleitor"):
            mesario = msg.split()[1]
        elif msg.startswith("Digital coletada bate com uma digital gravada após o registro inicial"):
            mesario = "nao_associavel"
        elif msg.startswith("Não encontrou digital coletada em nenhum dos arquivos"):
            mesario = "nao_encontrada"
        elif msg.startswith("Eleitor foi suspenso e não confirmou nenhum voto"):
            r["habilitado_e_suspenso_sem_votar"] += 1
        elif msg == "O voto do eleitor foi computado":
            # Classifica pela sessão inteira do eleitor: o "tipo" pode vir logo depois de "habilitado", no mesmo segundo.
            tipo = tipo or "outro"
            r["hab_" + tipo] += 1
            if tipo == "manual":
                manuais_hora[hora[:2]] += 1
                if mesario in ("nao_associavel", "nao_encontrada"):
                    r["manual_mesario_" + mesario] += 1
                elif mesario:
                    r["manual_mesario_identificado"] += 1
                    mesarios[mesario] += 1
                else:
                    r["manual_sem_registro_de_mesario"] += 1
            tipo, votou = None, True
            r["votos_log"] += 1
            votos_hora[hora[:2]] += 1
            ultimo_voto = hora
        if nivel == "ERRO" or ("Verificação de assinatura" in msg and "SUCESSO" not in msg):
            erros[msg.split("|")[0].strip()] += 1
    r["max_por_mesario"] = max(mesarios.values(), default=0)
    return r, votos_hora, ultimo_voto, manuais_hora, erros


def auditar(uf):
    z = zipfile.ZipFile(os.path.join(PASTA_URNA, f"bu_imgbu_logjez_rdv_vscmr_2026_2t_{uf}.zip"))
    nomes = set(z.namelist())
    base = sorted({n.rsplit("-", 1)[0] for n in nomes if n.endswith("-log.jez")})
    linhas, horas, erros, manuais = [], Counter(), Counter(), Counter()
    for b in base:
        img = parse(z.read(b + "-imgbu.dat").decode("latin1")) if b + "-imgbu.dat" in nomes else {}
        r, vh, ultimo, mh, er = eventos_secao(z.read(b + "-log.jez"))
        horas.update(vh)
        manuais.update(mh)
        erros.update(er)
        for k in ["comparecimento", "hab_biometrica", "hab_biografica", "hab_sem_biometria"]:
            r["bu_" + k] = int(img[k]) if img.get(k) else -1
        r["arquivo"] = b
        r["ultimo_voto"] = ultimo
        r["fechamento_bu"] = img.get("fechamento")
        linhas.append(r)
    df = pd.DataFrame(linhas)
    num = [c for c in df.columns if c not in ("arquivo", "ultimo_voto", "fechamento_bu")]
    df[num] = df[num].fillna(0).astype(int)
    return df, horas, manuais, erros


def resumo(uf):
    df, horas, manuais, erros = auditar(uf)
    for c in ["hab_biometrica", "hab_manual", "hab_sem_biometria", "hab_outro", "manual_mesario_identificado",
              "manual_mesario_nao_associavel", "manual_mesario_nao_encontrada", "manual_sem_registro_de_mesario",
              "dado_pessoal_recusado", "habilitado_e_suspenso_sem_votar", "sessoes_recusadas_sem_voto"]:
        if c not in df:
            df[c] = 0
    ok = lambda a, b: int((df[a] == df[b]).sum())  # noqa: E731
    s = {
        "seções (logs)": len(df),
        "votos computados no log = comparecimento do BU": ok("votos_log", "bu_comparecimento"),
        "habilitações biométricas: log = BU": ok("hab_biometrica", "bu_hab_biometrica"),
        "liberações manuais (digital falhou): log = 'biográfica' do BU": ok("hab_manual", "bu_hab_biografica"),
        "sem biometria cadastrada (ano de nasc.): log = BU": ok("hab_sem_biometria", "bu_hab_sem_biometria"),
        "total de liberações manuais (log)": int(df.hab_manual.sum()),
        "total 'biográfica' (BU) = campo da BWeb": int(df.bu_hab_biografica.sum()),
        "  manuais com digital do mesário identificada": int(df.manual_mesario_identificado.sum()),
        "  manuais com digital de mesário não associável a um nome": int(df.manual_mesario_nao_associavel.sum()),
        "  manuais com digital do mesário capturada mas não encontrada": int(df.manual_mesario_nao_encontrada.sum()),
        "  manuais sem registro de mesário": int(df.manual_sem_registro_de_mesario.sum()),
        "vezes em que o dado pessoal digitado foi recusado pela urna": int(df.dado_pessoal_recusado.sum()),
        "  …eleitores que, depois da recusa, saíram sem votar": int(df.sessoes_recusadas_sem_voto.sum()),
        "habilitados e suspensos sem votar": int(df.habilitado_e_suspenso_sem_votar.sum()),
        "votos sem habilitação identificada no log": int(df.hab_outro.sum()),
        "maior nº de liberações por um único mesário na seção": int(df.max_por_mesario.max()),
        "seções com voto registrado após o fechamento do BU": int((df.ultimo_voto.notna() & df.fechamento_bu.notna()
                                                                   & (df.ultimo_voto.astype(str) > df.fechamento_bu.astype(str))).sum()),
    }
    return s, horas, manuais, erros, df


if __name__ == "__main__":
    tabela, linhas_h = {}, []
    for uf in sys.argv[1:] or ["AC"]:
        s, horas, manuais, erros, df = resumo(uf)
        tabela[uf] = s
        tot, tm = sum(horas.values()), sum(manuais.values())
        for h in sorted(horas):
            hb = int(h) + FUSO.get(uf, 0)
            linhas_h.append({"UF": uf, "hora local": h, "hora Brasília": f"{hb:02d}", "votos": horas[h],
                             "% votos": round(horas[h] / tot * 100, 2),
                             "liberações manuais": manuais.get(h, 0),
                             "% manuais na hora": round(manuais.get(h, 0) / horas[h] * 100, 2)})
        dif = df[(df.votos_log != df.bu_comparecimento) | (df.hab_manual != df.bu_hab_biografica)]
        print(uf, "divergências:", len(dif))
        print(dif[["arquivo", "votos_log", "bu_comparecimento", "hab_manual", "bu_hab_biografica"]].head(8).to_string())
        print(uf, "erros mais comuns:", erros.most_common(4))
    txt = ("# Logs das urnas × BU — 2º turno 2026\n\n"
           f"UFs auditadas: {', '.join(tabela)}. Fonte: arquivos originais transmitidos para totalização "
           "(`dados/tse/2026/arquivos_urna/2turno/`), lendo também os logs arquivados de urnas substituídas.\n\n"
           + pd.DataFrame(tabela).to_markdown() + "\n\n## Votos e liberações manuais por hora\n\n"
           + pd.DataFrame(linhas_h).to_markdown(index=False) + "\n")
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "LOGS.md"), "w", encoding="utf-8").write(txt)
    print(txt)
