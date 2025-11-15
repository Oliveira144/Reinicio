import streamlit as st
import pandas as pd

# Mapeamento dos valores das cartas
valores_carta = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7,
                 "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}

def valor_carta(carta):
    return valores_carta.get(carta, 0)

def winner(row):
    home_val = valor_carta(row["Carta Home"])
    away_val = valor_carta(row["Carta Away"])
    if home_val > away_val:
        return "Home"
    elif away_val > home_val:
        return "Away"
    else:
        return "Draw"

def identifica_streaks(df):
    streaks = []
    streak_len = 1

    for i in range(1, len(df)):
        prev_winner = winner(df.iloc[i - 1])
        curr_winner = winner(df.iloc[i])

        if curr_winner == prev_winner and curr_winner != "Draw":
            streak_len += 1
        else:
            if streak_len > 1:
                streaks.append((i - streak_len, i - 1, prev_winner, streak_len))
            streak_len = 1
    if streak_len > 1:
        streaks.append((len(df) - streak_len, len(df) - 1, winner(df.iloc[-1]), streak_len))
    return streaks

def identificar_alternancia(df):
    alternancias = []
    for i in range(1, len(df)):
        if winner(df.iloc[i]) != winner(df.iloc[i - 1]):
            alternancias.append(i)
    return alternancias

def identificar_empate_apos_streak(df):
    empates_pos_streak = []
    streaks = identifica_streaks(df)
    for (start, end, vencedor, length) in streaks:
        if end + 1 < len(df):
            if winner(df.iloc[end + 1]) == "Draw":
                empates_pos_streak.append(end + 1)
    return empates_pos_streak

def tendencia_pos_empate(df):
    resultados = []
    for i in range(1, len(df)):
        if winner(df.iloc[i - 1]) == "Draw":
            resultados.append((i, winner(df.iloc[i])))
    return resultados

def analise_avancada(df):
    if len(df) < 2:
        return "Dados insuficientes para análise"

    analises = []

    # Analisar streaks
    streaks = identifica_streaks(df)
    if streaks:
        analises.append(f"Identificados {len(streaks)} streak(s) de vitórias consecutivas.")

    # Analisar alternâncias
    alternancias = identificar_alternancia(df)
    analises.append(f"Foram identificadas {len(alternancias)} alternância(s) de vencedor.")

    # Analisar empates após streaks
    empates_pos_streak = identificar_empate_apos_streak(df)
    analises.append(f"Empates detectados após streaks: {len(empates_pos_streak)} vezes.")

    # Analisar tendências após empates
    tendencia_empates = tendencia_pos_empate(df)
    if tendencia_empates:
        analises.append(f"Tendências observadas após empates em {len(tendencia_empates)} rodadas.")

    return "
".join(analises)

# Streamlit app
st.title("Analisador Profissional Football Studio")

# Session state para armazenar dados
if 'cards_df' not in st.session_state:
    st.session_state['cards_df'] = pd.DataFrame(columns=["Rodada", "Carta Home", "Carta Away"])

# Inputs para o usuário
st.header("Registrar rodada")
rodada = st.number_input("Número da rodada", min_value=1, step=1)
carta_home = st.selectbox("Carta Home", options=list(valores_carta.keys()))
carta_away = st.selectbox("Carta Away", options=list(valores_carta.keys()))

# Registrar rodada
if st.button("Registrar rodada"):
    new_row = {"Rodada": rodada, "Carta Home": carta_home, "Carta Away": carta_away}
    # Método recomendado para adicionar linha sem warning
    st.session_state['cards_df'] = pd.concat([st.session_state['cards_df'], pd.DataFrame([new_row])], ignore_index=True)
    st.success("Rodada registrada com sucesso!")

# Mostrar dados
st.header("Dados Registrados")
st.dataframe(st.session_state['cards_df'])

# Análise avançada
st.header("Análise Avançada dos Padrões")
df = st.session_state['cards_df']
resultado_analise = analise_avancada(df)
st.text_area(label="Resultados da Análise", value=resultado_analise, height=150)

# Sugestão de aposta baseada na análise
if len(df) >= 3:
    streaks = identifica_streaks(df)
    if streaks and streaks[-1][3] >= 3:
        st.write("Recomendação: Apostar no mesmo vencedor da última sequência longa (streak).")
    else:
        st.write("Recomendação: Observar padrão de alternância ou empates para decidir a aposta.")
else:
    st.write("Mais dados são necessários para sugestões precisas.")
