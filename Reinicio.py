import streamlit as st

# --- Atualização e limpeza do histórico ---
def update_history(new_value):
    if len(st.session_state.history) >= 9:
        st.session_state.history.pop()  # remove o resultado mais antigo
    st.session_state.history.insert(0, new_value)  # insere o mais recente no início

def clear_history():
    st.session_state.history = []

# --- Análise de padrões básicos ---
def count_alternations(history):
    count = 0
    for i in range(len(history) - 1):
        if history[i] != history[i + 1] and history[i] != '🟡' and history[i + 1] != '🟡':
            count += 1
    return count

def count_consecutive_repetitions(history):
    count = max_count = 1
    for i in range(1, len(history)):
        if history[i] == history[i - 1] and history[i] != '🟡':
            count += 1
            max_count = max(max_count, count)
        else:
            count = 1
    return max_count

def find_doubles_blocks(history):
    blocks, i = 0, 0
    while i < len(history) - 1:
        if history[i] == history[i + 1] and history[i] != '🟡':
            blocks += 1
            i += 2
        else:
            i += 1
    return blocks

def find_triples_blocks(history):
    blocks, i = 0, 0
    while i < len(history) - 2:
        if history[i] == history[i + 1] == history[i + 2] and history[i] != '🟡':
            blocks += 1
            i += 3
        else:
            i += 1
    return blocks

def is_mirror_pattern(history):
    n = len(history)
    if n < 6:
        return False
    mid = n // 2
    for i in range(mid):
        left = history[i]
        right = history[n - 1 - i]
        if left == '🟡' or right == '🟡':
            continue  # ignora empates
        if left != right:
            return False
    return True

def contains_draw_in_last_n(history, n):
    return '🟡' in history[:n]

def detect_zigzag_break(history):
    # Detecta zig-zag com reversões duplas camufladas
    for i in range(len(history) - 3):
        segment = history[i:i + 4]
        if segment[0] == segment[2] and segment[1] == segment[3] and segment[0] != segment[1] and '🟡' not in segment:
            return True
    return False

# --- Detecção e interpretação do padrão conforme sistema unificado ---
def detect_pattern(history):
    if len(history) < 4:
        return 'Insuficientes dados', None

    alternations = count_alternations(history)
    max_reps = count_consecutive_repetitions(history)
    doubles = find_doubles_blocks(history)
    triples = find_triples_blocks(history)
    mirror = is_mirror_pattern(history)
    draws = history.count('🟡')
    zigzag_break = detect_zigzag_break(history)

    # 1. PADRÃO SURF — Onda Controlada
    if alternations >= 4 and max_reps <= 2 and not contains_draw_in_last_n(history, 3):
        # Pico da onda na 5ª ou 6ª alternância com repetição last color
        if len(history) >= 6 and history[4] == history[5]:
            return ('Surf 🌊',
                "Ciclo de 4 a 8 alternâncias, pico na 5ª-6ª em repetição. Após empate 🟡, apostar inversão (lado oposto).")
        return ('Surf 🌊',
            "Alternância suave, após 4 alternâncias apostar repetição da última cor.")

    # 2. PADRÃO PING-PONG — Alternância Perfeita
    if 3 <= alternations <= 6 and max_reps == 1:
        if contains_draw_in_last_n(history, 3):
            return ('Ping-Pong 🏓',
                "Alternância limpa, após empate apostar inversão. Na 5ª jogada apostar repetição da última cor.")
        return ('Ping-Pong 🏓',
            "Alternância direta e limpa; preparar para quebra após 3+ alternâncias.")

    # 3. PADRÃO ALTERNÂNCIA SUJA — Alternância com micro-repetições
    if doubles >= 1 and max_reps == 2:
        return ('Alternância Suja 🔁',
            "Duplas indicam microquebras. Após dupla apostar alternância (cor oposta). Após duas duplas seguidas, preparar inversão.")

    # 4. PADRÃO ZIG-ZAG — Alternância camuflada
    if zigzag_break and doubles >= 1 and max_reps >= 2 and draws <= 1 and len(history) >= 6:
        return ('Zig-Zag ⚡',
            "Simula alternância com reversões duplas. Apostar inversão após dupla; após empate apostar lado anterior ao empate.")

    # 5. PADRÃO 2x2 — Duplas Alternadas
    if doubles >= 2:
        if doubles >= 3:
            return ('2x2 (Duplas) 🟦',
                "Ciclo de 3 a 4 blocos. Após 3ª dupla, apostar inversão total.")
        return ('2x2 (Duplas) 🟦',
            "Duplas alternadas em ciclo. Após 2ª dupla preparar inversão.")

    # 6. PADRÃO 3x3 — Triplas Alternadas
    if triples >= 2:
        return ('3x3 (Triplas) 🔺',
            "Triplas alternadas. Após 2ª tripla apostar lado oposto. Se empate, apostar valor reduzido.")

    # 7. PADRÃO ESPELHADO (MIRROR)
    if mirror:
        return ('Espelhado 🪞',
            "Sequência refletida. Após centro da simetria apostar repetição da metade anterior.")

    # 8. PADRÃO COLAPSO (OU CAOS QUÂNTICO)
    if draws >= 1 and doubles >= 2 and alternations >= 1:
        return ('Colapso / Reverso Quântico 🌀',
            "Padrão irregular e caótico. Evitar apostas. Reentrar após ciclo limpo.")

    # 9. PADRÃO ÂNCORA — Empate como ponto de controle
    if contains_draw_in_last_n(history, 1):
        return ('Âncora (Empate) ⚓',
            "Após empate apostar no lado oposto da última cor. Se novo empate ocorrer, inverter aposta novamente.")

    # 10. PADRÃO CAMUFLADO — Mistura de manipulações
    if draws >= 2 and doubles >= 1 and triples >= 1:
        return ('Camuflado 🕵️‍♂️',
            "Mistura de padrões. Apostar somente após confirmação de 2 blocos coerentes limpos.")

    return ('Padrão Desconhecido', 'Sem sugestão clara')

# --- Nível de manipulação ---
def calculate_manipulation_level(history):
    alternations = count_alternations(history)
    draws = history.count('🟡')
    max_reps = count_consecutive_repetitions(history)
    doubles = find_doubles_blocks(history)
    triples = find_triples_blocks(history)

    if alternations <= 2 and draws == 0 and max_reps <= 2:
        return 1  # Natural / aleatório
    elif draws <= 2 and max_reps <= 2 and doubles <= 1:
        return 3  # Controle leve
    elif alternations >= 4 and draws >= 1:
        return 5  # Manipulação média
    elif max_reps >= 3 or doubles >= 3:
        return 7  # Manipulação profunda
    elif triples >= 2 or draws >= 3 or doubles >= 4:
        return 9  # Manipulação quântica
    return 4  # Default intermediário

# --- Previsão da próxima jogada com normalização segura ---
def normalize_prediction(pred_raw):
    keys = ['🔴', '🔵', '🟡']
    total = sum(pred_raw.get(k, 0) for k in keys)
    if total == 0:
        # Distribuir igualmente em caso de erro
        return {k: 33 for k in keys}
    return {k: round(pred_raw.get(k, 0) / total * 100) for k in keys}

def predict_next(history, manipulation_level, pattern):
    if not history:
        return {'🔴': 33, '🔵': 33, '🟡': 34}

    last = history[0]
    inverse = '🔴' if last == '🔵' else '🔵'

    if pattern.startswith('Surf'):
        if contains_draw_in_last_n(history, 1) and len(history) > 1:
            return {history[1]: 70, '🟡': 10, last: 20}
        return {last: 75, '🟡': 5, inverse: 20}

    if pattern.startswith('Ping-Pong'):
        if contains_draw_in_last_n(history, 1) and len(history) > 1:
            return {history[1]: 80, '🟡': 10, last: 10}
        return {last: 70, '🟡': 10, inverse: 20}

    if pattern.startswith('Alternância Suja'):
        return {inverse: 70, last: 25, '🟡': 5}

    if pattern.startswith('Zig-Zag'):
        return {inverse: 75, last: 20, '🟡': 5}

    if pattern.startswith('2x2'):
        return {inverse: 80, last: 15, '🟡': 5}

    if pattern.startswith('3x3'):
        return {inverse: 80, last: 15, '🟡': 5}

    if pattern.startswith('Espelhado'):
        return {last: 70, '🟡': 10, inverse: 20}

    if pattern.startswith('Colapso'):
        return {'🔴': 33, '🔵': 33, '🟡': 34}

    if pattern.startswith('Âncora'):
        return {inverse: 75, last: 20, '🟡': 5}

    if pattern.startswith('Camuflado'):
        return {'🔴': 33, '🔵': 33, '🟡': 34}

    return {'🔴': 33, '🔵': 33, '🟡': 34}

# --- Gerar sinal visual de alerta conforme nível ---
def alert_signal(level):
    if 4 <= level <= 6:
        return '🟢 Brecha Detectada'
    elif 7 <= level <= 8:
        return '🟡 Risco Médio'
    elif level == 9:
        return '🔴 Manipulação Alta'
    else:
        return '🟢 Normal'

# --- Sugestões diretas para apostas ---
def suggest_bet(pattern, history):
    if not history or len(history) < 2:
        return 'Aguardando mais dados.'

    if pattern == 'Insuficientes dados':
        return 'Dados insuficientes.'

    last = history[0]
    opposite = '🔴' if last == '🔵' else '🔵'

    if pattern == 'Surf 🌊':
        if '🟡' in history[:3]:
            return f'Aposte na inversão: {opposite}'
        return f'Aposte na última cor: {last}'

    if pattern == 'Ping-Pong 🏓':
        if '🟡' in history[:3]:
            return f'Aposte na inversão: {opposite}'
        return f'Aposte na última cor: {last}'

    if pattern == 'Alternância Suja 🔁':
        return f'Aposte na alternância: {opposite}'

    if pattern == 'Zig-Zag ⚡':
        return f'Aposte na inversão após dupla: {opposite}'

    if pattern.startswith('2x2'):
        return f'Aposte no lado oposto após segunda dupla: {opposite}'

    if pattern.startswith('3x3'):
        if '🟡' in history[:3]:
            return f'Após empate, inverta e reduza aposta: {opposite}'
        return f'Aposte na inversão após 2 triplas: {opposite}'

    if pattern == 'Espelhado 🪞':
        return f'Repita metade anterior: {last}'

    if pattern == 'Colapso / Reverso Quântico 🌀':
        return 'Não apostar; aguarde padrão limpo.'

    if pattern == 'Âncora (Empate) ⚓':
        if '🟡' in history[:2]:
            if len(history) > 2 and history[2] == last:
                return f'Aposte no mesmo lado após empate: {last}'
            return f'Aposte na inversão: {opposite}'
        return f'Aposte na inversão: {opposite}'

    if pattern == 'Camuflado 🕵️‍♂️':
        return 'Aposte após confirmação de blocos limpos.'

    return 'Sem sugestão clara.'

# --- Inicialização do estado do Streamlit ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- Interface ---
st.title('Football Studio - Sistema Unificado de Padrões (Cartas Físicas)')

st.sidebar.header('Registrar novo resultado (mais recente à esquerda)')
cols = st.sidebar.columns(4)
if cols[0].button('🔴'):
    update_history('🔴')
if cols[1].button('🔵'):
    update_history('🔵')
if cols[2].button('🟡'):
    update_history('🟡')
if cols[3].button('Limpar Histórico'):
    clear_history()

st.subheader('Histórico (mais recente → mais antigo):')
st.write(' '.join(st.session_state.history))

# Detectar padrão e nível de manipulação
pattern, strategy = detect_pattern(st.session_state.history)
level = calculate_manipulation_level(st.session_state.history)
prediction_raw = predict_next(st.session_state.history, level, pattern)

# Normalizar previsão para porcentagem com segurança de chaves
prediction = normalize_prediction(prediction_raw)

alert_msg = alert_signal(level)
bet_recommendation = suggest_bet(pattern, st.session_state.history)

# Exibir resultados
st.subheader('Resumo da Análise')
st.markdown(f"- **Padrão Detectado:** {pattern}")
st.markdown(f"- **Descrição do Padrão / Estratégia:** {strategy}")
st.markdown(f"- **Nível de Manipulação:** {level}")
st.markdown(f"- **Sinal de Alerta:** {alert_msg}")

st.subheader('Previsão da Próxima Jogada')
st.write(f"🔴 {prediction['🔴']}% | 🔵 {prediction['🔵']}% | 🟡 {prediction['🟡']}%")

st.subheader('Sugestão de Aposta')
st.write(bet_recommendation)
