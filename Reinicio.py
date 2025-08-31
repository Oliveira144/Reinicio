import streamlit as st
import random

=============================================================

Motor de Análise de Manipulação

=============================================================

def analyze_history(seq): if not seq: return { "nivel": 0, "prob": {"🔴": 0, "🔵": 0, "🟡": 0}, "sugestao": "Aguardando entradas..." }

last = seq[-1]
count = 1
for i in range(len(seq) - 2, -1, -1):
    if seq[i] == last:
        count += 1
    else:
        break

# Probabilidades iniciais equilibradas
probs = {"🔴": 33.3, "🔵": 33.3, "🟡": 33.3}
nivel = 1
sugestao = "Sem leitura clara ainda."

# Heurísticas simples de manipulação
if count >= 3:
    nivel = 3
    # Quando há streak, maior chance de quebra
    next_options = ["🔴", "🔵"]
    next_options.remove(last)
    probs[next_options[0]] = 60
    probs[last] = 30
    probs["🟡"] = 10
    sugestao = f"Possível quebra da sequência de {count} {last}. Sugestão: {next_options[0]}"

elif len(seq) >= 4 and seq[-4:] in (["🔴","🔵","🔴","🔵"], ["🔵","🔴","🔵","🔴"]):
    nivel = 4
    # Alternância forte → chance de quebra
    next_options = ["🔴", "🔵"]
    next_options.remove(last)
    probs[last] = 20
    probs[next_options[0]] = 70
    probs["🟡"] = 10
    sugestao = f"Alternância detectada. Sugestão: {next_options[0]}"

elif last == "🟡":
    nivel = 2
    # Reset → próxima tende a ser vermelho ou azul
    probs["🟡"] = 5
    probs["🔴"] = 47.5
    probs["🔵"] = 47.5
    sugestao = "Reset detectado. Apostar em 🔴 ou 🔵 com equilíbrio."

else:
    nivel = 1
    sugestao = "Jogo em equilíbrio, sem manipulação clara."

return {
    "nivel": nivel,
    "prob": probs,
    "sugestao": sugestao
}

=============================================================

Interface Streamlit

=============================================================

st.set_page_config(page_title="Football Studio Manipulation Analyzer", layout="centered")

st.title("🎲 Football Studio Manipulation Analyzer") st.write("Insira manualmente os resultados e veja a análise preditiva da manipulação.")

Sessão de histórico

if "history" not in st.session_state: st.session_state.history = []

Botões de entrada

col1, col2, col3 = st.columns(3) with col1: if st.button("🔴 Vermelho"): st.session_state.history.append("🔴") with col2: if st.button("🔵 Azul"): st.session_state.history.append("🔵") with col3: if st.button("🟡 Empate"): st.session_state.history.append("🟡")

Mostrar histórico

st.subheader("📜 Histórico") if st.session_state.history: max_per_line = 9 for i in range(0, len(st.session_state.history), max_per_line): st.write(" ".join(st.session_state.history[i:i+max_per_line])) else: st.write("Nenhum resultado inserido ainda.")

Análise

st.subheader("🤖 Análise da IA") analysis = analyze_history(st.session_state.history)

st.write(f"Nível de manipulação: {analysis['nivel']}")

st.write("Probabilidades próximas:") col1, col2, col3 = st.columns(3) col1.metric("🔴", f"{analysis['prob']['🔴']}%") col2.metric("🔵", f"{analysis['prob']['🔵']}%") col3.metric("🟡", f"{analysis['prob']['🟡']}%")

st.write(f"Sugestão: {analysis['sugestao']}")

Botão para resetar histórico

if st.button("🔄 Resetar Histórico"): st.session_state.history = [] st.success("Histórico limpo!")

