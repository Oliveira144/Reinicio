import streamlit as st
from collections import Counter

# ==============================
# Função de análise avançada
# ==============================
def analyze_advanced(history):
    if not history:
        return [], None, {"🔴":33.3,"🔵":33.3,"🟡":33.3}

    # Considerar apenas os últimos 18 resultados
    h = history[-18:]

    patterns_detected = []
    prob = {"🔴":0,"🔵":0,"🟡":0}

    # ===== Função de camada =====
    def layer_analysis(seq, weight):
        layer_prob = {"🔴":0,"🔵":0,"🟡":0}
        l = len(seq)

        # --- Streaks ---
        i = l-1
        while i>=0:
            color = seq[i]
            if color=="🟡":
                i-=1
                continue
            streak = 1
            j = i-1
            while j>=0 and seq[j]==color:
                streak+=1
                j-=1
            if streak>=2:
                patterns_detected.append(f"Streak {color} ≥{streak} (camada {weight})")
                layer_prob[color] += streak*5*weight
            i = j

        # --- Alternâncias simples ---
        if l>=4:
            for start in range(l-3):
                sub = seq[start:start+4]
                if sub in [["🔴","🔵","🔴","🔵"], ["🔵","🔴","🔵","🔴"]]:
                    patterns_detected.append(f"Alternância 4 cores (camada {weight})")
                    next_color = sub[-2]
                    layer_prob[next_color]+=30*weight
                    layer_prob[sub[-1]]+=20*weight
                    layer_prob["🟡"]+=10*weight

        # --- Reset por empate ---
        for k in range(1,l):
            if seq[k]=="🟡" and seq[k-1] in ["🔴","🔵"]:
                patterns_detected.append(f"Reset 🟡 (camada {weight})")
                next_color = "🔴" if seq[k-1]=="🔵" else "🔵"
                layer_prob[next_color]+=40*weight
                layer_prob[seq[k-1]]+=20*weight
                layer_prob["🟡"]+=10*weight

        # --- Padrões repetidos complexos ---
        for size in range(4,7):
            if l>=size*2:
                if seq[-size:]==seq[-2*size:-size]:
                    patterns_detected.append(f"Padrão repetido {size} cores (camada {weight})")
                    repeated_color = seq[-size]
                    layer_prob[repeated_color]+=50*weight
                    for c in ["🔴","🔵","🟡"]:
                        if c!=repeated_color:
                            layer_prob[c]+=10*weight

        return layer_prob

    # ===== Análise por camadas =====
    layer1 = layer_analysis(h[-6:], 1)       # superficial
    layer2 = layer_analysis(h[-12:], 2)      # intermediária
    layer3 = layer_analysis(h, 3)            # profunda

    # Combinar probabilidades
    for c in prob:
        prob[c] = layer1[c]+layer2[c]+layer3[c]

    # Normalizar
    total = sum(prob.values())
    if total==0:
        prob = {"🔴":33.3,"🔵":33.3,"🟡":33.3}
    else:
        for c in prob:
            prob[c]=round(prob[c]/total*100,1)

    # Sugestão: cor com maior probabilidade
    suggestion = max(prob, key=prob.get)

    return patterns_detected, suggestion, prob

# ==============================
# Interface Streamlit
# ==============================
st.set_page_config(page_title="Football Studio Analyzer Profissional", layout="centered")
st.title("🎲 Football Studio Analyzer Profissional")
st.write("IA avançada analisando os últimos 18 resultados com múltiplas camadas e padrões complexos.")

# Inicializar histórico
if "history" not in st.session_state:
    st.session_state.history = []

# ===== Entrada de resultados =====
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔴 Vermelho"):
        st.session_state.history.append("🔴")
with col2:
    if st.button("🔵 Azul"):
        st.session_state.history.append("🔵")
with col3:
    if st.button("🟡 Empate"):
        st.session_state.history.append("🟡")

# ===== Histórico =====
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

# ===== Análise avançada =====
st.subheader("🤖 Análise Profunda da IA")
patterns, suggestion, prob = analyze_advanced(st.session_state.history)

# Padrões detectados
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

# ===== Reset do histórico =====
if st.button("🔄 Resetar Histórico"):
    st.session_state.history = []
    st.success("Histórico limpo!")
