import streamlit as st

# ==============================
# Definição dos 15 padrões principais
# ==============================
PATTERNS = [
    {"nome": "Streak 🔴 ≥2", "check": lambda h: len(h)>=2 and h[-1]=="🔴" and h[-2]=="🔴", "sugestao": lambda h: "🔵"},
    {"nome": "Streak 🔵 ≥2", "check": lambda h: len(h)>=2 and h[-1]=="🔵" and h[-2]=="🔵", "sugestao": lambda h: "🔴"},
    {"nome": "Alternância 🔴🔵🔴🔵", "check": lambda h: len(h)>=4 and h[-4:]==["🔴","🔵","🔴","🔵"], "sugestao": lambda h: "🔴"},
    {"nome": "Alternância 🔵🔴🔵🔴", "check": lambda h: len(h)>=4 and h[-4:]==["🔵","🔴","🔵","🔴"], "sugestao": lambda h: "🔵"},
    {"nome": "Reset 🟡 depois de streak", "check": lambda h: len(h)>=2 and h[-1]=="🟡" and h[-2] in ["🔴","🔵"], 
     "sugestao": lambda h: "🔴" if h[-2]=="🔵" else "🔵"},
    {"nome": "Duplo 🔴🔴 seguido de 🔵", "check": lambda h: len(h)>=3 and h[-3:]==["🔴","🔴","🔵"], "sugestao": lambda h: "🔵"},
    {"nome": "Duplo 🔵🔵 seguido de 🔴", "check": lambda h: len(h)>=3 and h[-3:]==["🔵","🔵","🔴"], "sugestao": lambda h: "🔴"},
    {"nome": "Triplo 🔴🔴🔴", "check": lambda h: len(h)>=3 and h[-3:]==["🔴","🔴","🔴"], "sugestao": lambda h: "🔵"},
    {"nome": "Triplo 🔵🔵🔵", "check": lambda h: len(h)>=3 and h[-3:]==["🔵","🔵","🔵"], "sugestao": lambda h: "🔴"},
    {"nome": "Empate no meio da alternância", "check": lambda h: len(h)>=3 and h[-2]=="🟡" and h[-3]!=h[-1], 
     "sugestao": lambda h: h[-3]},
    {"nome": "Sequência 🔴🔵🔵🔴", "check": lambda h: len(h)>=4 and h[-4:]==["🔴","🔵","🔵","🔴"], "sugestao": lambda h: "🔵"},
    {"nome": "Sequência 🔵🔴🔴🔵", "check": lambda h: len(h)>=4 and h[-4:]==["🔵","🔴","🔴","🔵"], "sugestao": lambda h: "🔴"},
    {"nome": "Padrão repetido 4 cores", "check": lambda h: len(h)>=8 and h[-8:-4]==h[-4:], "sugestao": lambda h: h[-4]},
    {"nome": "Padrão repetido 5 cores", "check": lambda h: len(h)>=10 and h[-10:-5]==h[-5:], "sugestao": lambda h: h[-5]},
    {"nome": "Padrão complexo reset+streak", "check": lambda h: len(h)>=4 and h[-1]=="🟡" and h[-2]==h[-3]==h[-4], 
     "sugestao": lambda h: "🔴" if h[-2]=="🔵" else "🔵"}
]

# ==============================
# Função de análise com padrões
# ==============================
def analyze_history(history):
    if not history:
        return {"nivel":0, "prob":{"🔴":33.3,"🔵":33.3,"🟡":33.3}, "sugestao":"Aguardando resultados...", "padrao":None, "padrao_repetido":False}

    last = history[-1]
    streak = 1
    for i in range(len(history)-2,-1,-1):
        if history[i]==last:
            streak += 1
        else:
            break

    probs = {"🔴":33.3,"🔵":33.3,"🟡":33.3}
    nivel = 1
    sugestao = ""
    padrao_encontrado = None
    padrao_repetido = False

    # Verificar padrões
    for p in PATTERNS:
        try:
            if p["check"](history):
                padrao_encontrado = p["nome"]
                sugestao = p["sugestao"](history) if callable(p["sugestao"]) else p["sugestao"]
                # Verifica se padrão se repetiu antes
                padrao_repetido = history[:-len(history)//2].count(history[-1])>=1
                break
        except:
            continue

    # Se nenhum padrão encontrado, heurística simples
    if not padrao_encontrado:
        if streak >=2 and last != "🟡":
            nivel = 3
            options = ["🔴","🔵"]
            options.remove(last)
            sugestao = options[0]
            probs[last]=20
            probs[options[0]]=60
            probs["🟡"]=20
        elif last=="🟡":
            nivel=2
            sugestao = "Apostar 🔴 ou 🔵"
            probs["🟡"]=5
            probs["🔴"]=47.5
            probs["🔵"]=47.5
        else:
            nivel=1
            count_r=history.count("🔴")
            count_b=history.count("🔵")
            if count_r<count_b:
                sugestao="🔴"
            elif count_b<count_r:
                sugestao="🔵"
            else:
                sugestao="🔴 ou 🔵"

    return {"nivel":nivel, "prob":probs, "sugestao":sugestao, "padrao":padrao_encontrado, "padrao_repetido":padrao_repetido}

# ==============================
# Interface Streamlit
# ==============================
st.set_page_config(page_title="Football Studio Analyzer", layout="centered")
st.title("🎲 Football Studio Analyzer")
st.write("Insira os resultados e veja a sugestão da IA baseada em padrões.")

if "history" not in st.session_state:
    st.session_state.history = []

# Botões de entrada
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

# Histórico da esquerda para direita, mais recente à esquerda
st.subheader("📜 Histórico (mais recente → mais antigo)")
if st.session_state.history:
    max_per_line = 9
    reversed_history = list(reversed(st.session_state.history))  # inverter para mostrar mais recente à esquerda
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

# Análise
st.subheader("🤖 Análise da IA")
analysis = analyze_history(st.session_state.history)
st.write(f"**Nível de manipulação:** {analysis['nivel']}")
st.write("**Probabilidades:**")
c1,c2,c3=st.columns(3)
c1.metric("🔴", f"{analysis['prob']['🔴']}%")
c2.metric("🔵", f"{analysis['prob']['🔵']}%")
c3.metric("🟡", f"{analysis['prob']['🟡']}%")

# Padrão detectado
if analysis["padrao"]:
    destaque = " 🔥" if analysis["padrao_repetido"] else ""
    st.write(f"**Padrão detectado:** {analysis['padrao']}{destaque}")
st.write(f"**Sugestão de entrada:** {analysis['sugestao']}")

# Reset
if st.button("🔄 Resetar Histórico"):
    st.session_state.history=[]
    st.success("Histórico limpo!")
