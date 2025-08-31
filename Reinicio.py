import streamlit as st
from collections import Counter

# ==============================
# Função de análise combinada de padrões
# ==============================
def analyze_patterns(history):
    if not history:
        return [], None, {"🔴":33.3,"🔵":33.3,"🟡":33.3}

    patterns_detected = []
    prob = {"🔴":0,"🔵":0,"🟡":0}
    streaks = []

    # ======= Detectar streaks =======
    current_color = history[-1]
    streak_count = 1
    for i in range(len(history)-2,-1,-1):
        if history[i] == current_color:
            streak_count += 1
        else:
            break
    if current_color != "🟡" and streak_count>=2:
        patterns_detected.append(f"Streak {current_color} ≥{streak_count}")
        streaks.append((current_color, streak_count))

    # ======= Detectar alternâncias simples e longas =======
    if len(history) >= 4:
        recent4 = history[-4:]
        if recent4 in [["🔴","🔵","🔴","🔵"], ["🔵","🔴","🔵","🔴"]]:
            patterns_detected.append("Alternância 4 cores")
            # Probabilidade: próxima cor da alternância
            next_color = recent4[-2]
            prob[next_color] += 50
            prob[recent4[-1]] += 30
            prob["🟡"] += 20

    # ======= Detectar resets por empate =======
    if history[-1]=="🟡" and len(history)>=2 and history[-2] in ["🔴","🔵"]:
        patterns_detected.append("Reset 🟡")
        next_color = "🔴" if history[-2]=="🔵" else "🔵"
        prob[next_color] += 60
        prob["🟡"] += 10
        prob[history[-2]] += 30

    # ======= Detectar padrões repetidos complexos =======
    for size in range(4,7):
        if len(history) >= size*2:
            if history[-size:] == history[-2*size:-size]:
                patterns_detected.append(f"Padrão repetido {size} cores")
                repeated_color = history[-size]
                prob[repeated_color] += 60
                # Ajuste para outras cores
                for c in ["🔴","🔵","🟡"]:
                    if c != repeated_color:
                        prob[c] += 20 if c==history[-1] else 10

    # ======= Alternância interrompida por empate =======
    if len(history) >= 3 and history[-2]=="🟡" and history[-3]!=history[-1]:
        patterns_detected.append("Empate na alternância")
        prob[history[-3]] += 60
        prob[history[-1]] += 30
        prob["🟡"] += 10

    # ======= Ajustar probabilidade baseada em streaks =======
    for color, count in streaks:
        prob[color] += min(count*10,50)
        other_color = "🔴" if color=="🔵" else "🔵"
        prob[other_color] += 30

    # Normalizar probabilidades para somar 100
    total = sum(prob.values())
    if total == 0:
        prob = {"🔴":33.3,"🔵":33.3,"🟡":33.3}
    else:
        for c in prob:
            prob[c] = round(prob[c]/total*100,1)

    # ======= Sugestão final =======
    # Cor com maior probabilidade
    suggestion = max(prob, key=prob.get)

    return patterns_detected, suggestion, prob

# ==============================
# Interface Streamlit
# ==============================
st.set_page_config(page_title="Football Studio Analyzer Inteligente", layout="centered")
st.title("🎲 Football Studio Analyzer Inteligente")
st.write("Insira os resultados e veja a sugestão de aposta com confiança baseada em múltiplos padrões.")

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
patterns, suggestion, prob = analyze_patterns(st.session_state.history)

# Mostrar padrões detectados
if patterns:
    st.write("**Padrões detectados:**")
    for p in patterns:
        st.write(f"- {p} 🔥")

# Probabilidades
st.write("**Probabilidades ponderadas (%):**")
c1,c2,c3 = st.columns(3)
c1.metric("🔴", f"{prob['🔴']}%")
c2.metric("🔵", f"{prob['🔵']}%")
c3.metric("🟡", f"{prob['🟡']}%")

# Sugestão de entrada
st.write(f"**Sugestão de entrada (maior confiança):** {suggestion}")

# Reset histórico
if st.button("🔄 Resetar Histórico"):
    st.session_state.history = []
    st.success("Histórico limpo!")
