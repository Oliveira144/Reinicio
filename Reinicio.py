import streamlit as st

# Função para atualizar o histórico - adiciona o novo valor no início da lista
def update_history(new_value):
    if len(st.session_state.history) >= 9:
        st.session_state.history.pop()  # remove o último item (mais antigo)
    st.session_state.history.insert(0, new_value)  # insere o mais recente no início

# Contar alternâncias
def count_alternations(history):
    count = 0
    for i in range(len(history)-1):
        if history[i] != history[i+1]:
            count += 1
    return count

# Detectar padrão Surf
def detect_surf_pattern(history):
    alternacao = count_alternations(history)
    return alternacao >= 3

# Contar repetições consecutivas
def count_consecutive_repetitions(history):
    count = 1
    max_count = 1
    for i in range(1, len(history)):
        if history[i] == history[i-1]:
            count += 1
            max_count = max(max_count, count)
        else:
            count = 1
    return max_count

# Calcular nível de manipulação
def calculate_manipulation_level(history):
    level = 1
    alternacoes = count_alternations(history)
    draws = history.count('🟡')
    max_reps = count_consecutive_repetitions(history)

    if alternacoes <= 2 and draws == 0:
        level = 1
    elif draws <= 2 and max_reps <= 2:
        level = 3
    elif alternacoes >= 4 and draws >= 1:
        level = 5
    elif max_reps >= 3:
        level = 7
    elif max_reps >= 4 or draws >= 3:
        level = 9
    return level

# Previsão para próxima jogada
def predict_next(history, manipulation_level):
    last = history[0] if history else None  # o mais recente agora é o índice 0
    prediction = {'🔴': 0, '🔵': 0, '🟡': 0}

    if manipulation_level <= 2:
        prediction = {'🔴': 33, '🔵': 33, '🟡': 34}
    elif manipulation_level <= 4:
        if len(history) >= 2 and history[0] != history[1]:
            prediction[history[0]] = 30
            prediction[history[1]] = 50
            prediction['🟡'] = 20
        else:
            prediction = {'🔴': 40, '🔵': 40, '🟡': 20}
    elif manipulation_level <= 6:
        if last == '🟡' and len(history) >= 2:
            prediction[history[1]] = 70
            prediction['🟡'] = 10
            for k in prediction:
                if k != history[1]:
                    prediction[k] = 10
        else:
            prediction[last] = 70
            prediction['🟡'] = 5
            for k in prediction:
                if k != last:
                    prediction[k] = 25
    else:
        prediction = {'🔴': 33, '🔵': 33, '🟡': 34}

    total = sum(prediction.values())
    for key in prediction:
        prediction[key] = round(prediction[key] / total * 100)

    return prediction

# Alerta conforme nível
def alert_signal(level):
    if 4 <= level <= 6:
        return '🟢 Brecha Detectada'
    elif 7 <= level <= 8:
        return '🟡 Risco Médio'
    elif level == 9:
        return '🔴 Manipulação Alta'
    else:
        return '🟢 Normal'

# Sugestão de aposta
def suggest_bet(history, level):
    if len(history) < 2:
        return 'Aguardando mais dados'

    if detect_surf_pattern(history):
        last = history[0]
        return f'Apostar na repetição da última cor: {last}'

    if '🟡' in history[:3]:
        last_color = history[0]
        if last_color != '🟡':
            return f'Apostar no oposto da última cor: {"🔴" if last_color == "🔵" else "🔵"}'

    for i in range(len(history) - 3):
        if history[i] == history[i+1] and history[i+2] == history[i+3] and history[i] != history[i+2]:
            return 'Apostar na alternância'

    max_reps = count_consecutive_repetitions(history)
    if max_reps >= 3:
        return 'Apostar na inversão'

    if level >= 8:
        return 'Aguardar, não apostar devido à manipulação alta'

    return 'Sem sugestão clara'

# Inicializar histórico
if 'history' not in st.session_state:
    st.session_state.history = []

# Interface
st.title('Football Studio - Padrão Surf Inteligente')

st.sidebar.header('Clique para adicionar novo resultado')
col1, col2, col3 = st.sidebar.columns(3)
if col1.button('🔴'):
    update_history('🔴')
if col2.button('🔵'):
    update_history('🔵')
if col3.button('🟡'):
    update_history('🟡')

st.subheader('Histórico dos últimos 9 resultados (mais recente à esquerda)')
st.write(' '.join(st.session_state.history))

level = calculate_manipulation_level(st.session_state.history)
surf = detect_surf_pattern(st.session_state.history)
prediction = predict_next(st.session_state.history, level)
alert_msg = alert_signal(level)
bet_suggestion = suggest_bet(st.session_state.history, level)

st.subheader('Painel Resumo')
st.write(f'Nível de Manipulação: {level}')
st.write(f'Padrão Atual: {"Surf Controlado 🌊" if surf else "Nenhum padrão definido"}')
st.write('Probabilidades de próxima jogada:')
st.write(f'🔴 {prediction["🔴"]}% | 🔵 {prediction["🔵"]}% | 🟡 {prediction["🟡"]}%')
st.write(f'Sinal de Alerta: {alert_msg}')
st.write(f'Sugestão de Aposta: {bet_suggestion}')
