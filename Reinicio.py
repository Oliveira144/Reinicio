import streamlit as st
from collections import Counter

# ==============================
# Definição dos padrões avançados
# ==============================
def detect_patterns(history):
    patterns_detected = []
    suggestion = None
    prob = {"🔴":33.3,"🔵":33.3,"🟡":33.3}

    if not history:
        return patterns_detected, suggestion, prob

    last = history[-1]
    streak = 1
    for i in range(len(history)-2,-1,-1):
        if history[i]==last:
            streak += 1
        else:
            break

    # ======= Streaks =======
    if last != "🟡" and streak>=2:
        patterns_detected.append(f"Streak {last} ≥ {streak}")
        # Probabilidade adaptativa
        prob[last] = max(10, 50-streak*5)
        prob["🔴" if last=="🔵" else "🔵"] = 100-prob[last]-10
        prob["🟡"] = 10
        suggestion = "🔴" if last=="🔵" else "🔵"

    # ======= Alternâncias =======
    if len(history)>=4:
        recent4 = history[-4:]
        if recent4 in [["🔴","🔵","🔴","🔵"], ["🔵","🔴","🔵","🔴"]]:
            patterns_detected.append("Alternância 4 cores")
            # Sugere próxima cor da alternância
            suggestion = recent4[-2]
            prob[suggestion] = 60
            prob[last] = 30
            prob["🟡"] = 10

    # ======= Reset por empate =======
    if last == "🟡" and len(history)>=2 and history[-2] in ["🔴","🔵"]:
        patterns_detected.append("Reset 🟡")
        suggestion = "🔴" if history[-2]=="🔵" else "🔵"
        prob = {"🔴":47.5,"🔵":47.5,"🟡":5}

    # ======= Padrões repetidos complexos =======
    for size in range(4,7):
        if len(history)>=size*2:
            if history[-size:] == history[-2*size:-size]:
                patterns_detected.append(f"Padrão repetido {size} cores")
                suggestion = history[-size]
                prob[suggestion] = 60
                prob[last] = 30
                prob["🟡"] = 10

    # ======= Alternância interrompida por empate =======
    if len(history)>=3 and history[-2]=="🟡" and history[-3]!=history[-1]:
        patterns_detected.append("Empate na alternância")
        suggestion = history[-3]
        prob[suggestion] = 60
        prob[last] = 30
        prob["🟡"] = 10

    # ======= Caso nenhum padrão detectado =======
    if not patterns_detected:
        # Heurística simples com contagem
        count = Counter(history[-10:])  # últimos 10 resultados
        most_common = count.most_common()
        if most_common[0][0] != "🟡":
            suggestion = most_common[0][0]
            prob[suggestion] = 50
            others = ["🔴","🔵","🟡"]
            others.remove(suggestion)
            prob[others[0]] = 30
            prob[others[1]] = 20
        else:
            suggestion = "🔴"
            prob = {"🔴":40,"🔵":40,"🟡":20}

    return patterns_detected, suggestion, prob

# ==============================
# Interface Streamlit
# ==============================
st.set_page_config(page_title="Football Studio Analyzer Avançado", layout="centered")
st.title("🎲 Football Studio Analyzer Avançado")
st.write("Insira os resultados e veja a sugestão da IA baseada em padrões complexos e análise adaptativa.")

if "history" not in st.session_state:
    st.session_state.history = []

# Botões de entrada
col1,col2,col3 = st.columns(3)
with col1:
    if st.button("🔴 Vermelho"):
        st.session_state.history.append("🔴")
with col2:
    if st.button("🔵 Azul"):
        st.session_state.history.append("🔵")
with col3:
    if st.button("🟡 Empate"):
        st.session_state.history.append("🟡")

# Histórico da esquerda para direita, mais recente à esquerda
st.subheader("📜 Histórico (mais recente → mais antigo)")
if st.session_state.history:
    max_per_line = 9
    reversed_history = list(reversed(st.session_state.history))
    lines=[]
    current_line=[]
    for idx,res in enumerate(reversed_history):
        current_line.append(res)
        if (idx+1)%max_per_line==0:
            lines.append(current_line)
            current_line=[]
    if current_line:
        lines.append(current_line)
    for line in lines:
        st.write(" ".join(line))
else:
    st.write("Nenhum resultado inserido ainda.")

# Análise inteligente
st.subheader("🤖 Análise Avançada da IA")
patterns, suggestion, prob = detect_patterns(st.session_state.history)

# Mostrar padrões detectados
if patterns:
    st.write("**Padrões detectados:**")
    for p in patterns:
        st.write(f"- {p} 🔥")

# Probabilidades
st.write("**Probabilidades adaptativas:**")
c1,c2,c3 = st.columns(3)
c1.metric("🔴", f"{prob['🔴']}%")
c2.metric("🔵", f"{prob['🔵']}%")
c3.metric("🟡", f"{prob['🟡']}%")

# Sugestão de entrada
st.write(f"**Sugestão de entrada:** {suggestion}")

# Reset histórico
if st.button("🔄 Resetar Histórico"):
    st.session_state.history = []
    st.success("Histórico limpo!")
