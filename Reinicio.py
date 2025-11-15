    import streamlit as st
import pandas as pd

# Definição dos valores das cartas
VALORES_CARTA = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10,
    "J": 11, "Q": 12, "K": 13, "A": 14
}

def valor_carta(carta):
    return VALORES_CARTA.get(carta, 0)

def vencedor(rodada):
    home = valor_carta(rodada["Carta Home"])
    away = valor_carta(rodada["Carta Away"])
    if home > away:
        return "Home"
    elif away > home:
        return "Away"
    else:
        return "Draw"

def identifica_streaks(df):
    streaks = []
    streak_len = 1

    for i in range(1, len(df)):
        prev_winner = vencedor(df.iloc[i - 1])
        curr_winner = vencedor(df.iloc[i])

        if curr_winner == prev_winner and curr_winner != "Draw":
            streak_len += 1
        else:
            if streak_len > 1:
                streaks.append({
                    "início": i - streak_len,
                    "fim": i - 1,
                    "vencedor": prev_winner,
                    "tamanho": streak_len
                })
            streak_len = 1
    # Último streak
    if streak_len > 1:
        streaks.append({
            "início": len(df) - streak_len,
            "fim": len(df) - 1,
            "vencedor": vencedor(df.iloc[-1]),
            "tamanho": streak_len
        })
    return streaks

def identificar_alternancia(df):
    alternancias = []
    for i in range(1, len(df)):
        if vencedor(df.iloc[i]) != vencedor(df.iloc[i - 1]):
            alternancias.append(i)
    return alternancias

def identificar_empate_apos_streak(df):
    empates = []
    streaks = identifica_streaks(df)
    for streak in streaks:
        pos_apos_streak = streak["fim"] + 1
        if pos_apos_streak < len(df):
            if vencedor(df.iloc[pos_apos_streak]) == "Draw":
                empates.append(pos_apos_streak)
    return empates

def tendencia_pos_empate(df):
    resultados = []
    for i in range(1, len(df)):
        if vencedor(df.iloc[i - 1]) == "Draw":
            resultados.append((i, vencedor(df.iloc[i])))
    return resultados

def analise_avancada(df):
    if len(df) < 2:
        return "Dados insuficientes para análise."

    analises = []

    streaks = identifica_streaks(df)
    if streaks:
        analises.append(f"Foram identificados {len(streaks)} streak(s) de vitórias consecutivas.")

    alternancias = identificar_alternancia(df)
    analises.append(f"Foram observadas {len(alternancias)} alternância(s) de vencedor.")

    empates = identificar_empate_apos_streak(df)
    analises.append(f"{len(empates)} empates ocorreram imediatamente após streaks.")

    tendencias = tendencia_pos_empate(df)
    if tendencias:
        analises.append(f"Foram observadas tendências em {len(tendencias)} rodadas após empates.")

    return "
".join(analises)

# --- STREAMLIT APP ---

st.title("Analisador Profissional Football Studio")

if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=["Rodada", "Carta Home", "Carta Away"])

st.header("Registrar nova rodada")

rodada_num = st.number_input("Número da rodada", min_value=1, step=1)
carta_home = st.selectbox("Carta Home", options=list(VALORES_CARTA.keys()))
carta_away = st.selectbox("Carta Away", options=list(VALORES_CARTA.keys()))

if st.button("Adicionar rodada"):
    nova_rodada = {
        "Rodada": rodada_num,
        "Carta Home": carta_home,
        "Carta Away": carta_away
    }
    st.session_state.dados = pd.concat([st.session_state.dados, pd.DataFrame([nova_rodada])], ignore_index=True)
    st.success("Rodada adicionada com sucesso!")

st.header("Histórico de Rodadas")
st.dataframe(st.session_state.dados)

st.header("Análise e Recomendações")

resultado_analise = analise_avancada(st.session_state.dados)
st.text_area("Resultado da Análise", resultado_analise, height=150)

if len(st.session_state.dados) >= 3:
    streaks = identifica_streaks(st.session_state.dados)
    if streaks and streaks[-1]["tamanho"] >= 3:
        st.markdown("**Recomendação:** Apostar no mesmo vencedor da última sequência longa (streak).")
    else:
        st.markdown("**Recomendação:** Observar alternâncias ou empates para definir sua aposta.")
else:
    st.markdown("Mais dados são necessários para gerar recomendações confiáveis.")
