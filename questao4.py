## QUESTÃO4
#Aluno: Gustavo de Almeida Leite
#Matrícula: 202504002

import curses
import time
import random

# ─────────────────────────────────────────────
# PARÂMETROS GERAIS
# ─────────────────────────────────────────────
PREVIEW_ROWS = 4
GAME_ROWS    = 20
INNER_W      = 20                       # largura útil entre <!  !>
LINHA_VAZIA  = "<!" + " ." * 10 + " !>"

BASE_SLEEP   = 0.05                     # intervalo base do loop
LEVEL_STEP   = 30                       # segundos para subir de nível
SPEED_STEP   = 0.005                    # quanto reduz o sleep a cada nível
MIN_SLEEP    = 0.02                     # limite inferior

def linha_texto(txt: str) -> str:
    return "<!" + txt.center(INNER_W) + " !>"

# ─────────────────────────────────────────────
# PEÇAS
# ─────────────────────────────────────────────
peca_I = [['[]'], ['[]'], ['[]'], ['[]']]
peca_O = [['[]', '[]'], ['[]', '[]']]
peca_T = [['.', '[]', '.'], ['[]', '[]', '[]']]
peca_L = [['[]', '.'], ['[]', '.'], ['[]', '[]']]
peca_J = [['.', '[]'], ['.', '[]'], ['[]', '[]']]
peca_S = [['.', '[]', '[]'], ['[]', '[]', '.']]
peca_Z = [['[]', '[]', '.'], ['.', '[]', '[]']]
TODAS  = [peca_I, peca_O, peca_T, peca_L, peca_J, peca_S, peca_Z]

rotacionar = lambda p: [list(reversed(c)) for c in zip(*p)]

# ─────────────────────────────────────────────
# TABULEIROS
# ─────────────────────────────────────────────
def criar_tabuleiro():
    preview = [[LINHA_VAZIA] for _ in range(PREVIEW_ROWS)]
    jogo    = [[LINHA_VAZIA] for _ in range(GAME_ROWS)]
    rodape  = [["<!=-=-=-=-=-=-=-=-=-=-=!>"],
               ["\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/\\/"]]
    return preview + jogo + rodape

def piece_to_preview_lines(peca):
    linhas = [''.join('[]' if c == '[]' else '  ' for c in row).rstrip()
              for row in peca]
    larg = max((len(s) for s in linhas), default=0)
    return [l.ljust(larg) for l in linhas]

def aplicar_preview(tab, peca):
    for i in range(PREVIEW_ROWS):
        tab[i][0] = LINHA_VAZIA
    tab[0][0] = linha_texto("PRÓXIMA PEÇA")
    for i, ln in enumerate(piece_to_preview_lines(peca)[:PREVIEW_ROWS-1], 1):
        tab[i][0] = linha_texto(ln)

# ─────────────────────────────────────────────
# PEÇA ↔ TABULEIRO
# ─────────────────────────────────────────────
def desenhar_peca(tab, peca, x, y):
    for i, ln in enumerate(peca):
        py = y - i
        if PREVIEW_ROWS <= py < PREVIEW_ROWS + GAME_ROWS:
            linha_tab = list(tab[py][0])
            for j, bloco in enumerate(ln):
                if bloco == '[]':
                    pos = 2 + (x + j) * 2
                    if pos+1 < len(linha_tab):
                        linha_tab[pos:pos+2] = '[', ']'
            tab[py][0] = ''.join(linha_tab)

def largura_peca(p): return len(p[0])

def colisao(tab, p, x, y):
    for i, ln in enumerate(p):
        py = y - i + 1
        if py >= PREVIEW_ROWS + GAME_ROWS: return True
        if py >= PREVIEW_ROWS:
            for j, bloco in enumerate(ln):
                if bloco == '[]':
                    pos = 2 + (x + j) * 2
                    if pos+1 >= len(tab[py][0]) or tab[py][0][pos] in ['[',']']:
                        return True
    return False

def colisao_topo(tab, p, x, y):
    for i, ln in enumerate(p):
        py = y - i
        if py >= PREVIEW_ROWS:
            for j, bloco in enumerate(ln):
                if bloco == '[]':
                    pos = 2 + (x + j) * 2
                    if pos+1 >= len(tab[py][0]) or tab[py][0][pos] in ['[',']']:
                        return True
    return False

def limpar_linhas(tab):
    jogo = tab[PREVIEW_ROWS:PREVIEW_ROWS+GAME_ROWS]
    keep = []
    cleared = 0
    for ln in jogo:
        if ln[0].count('[') == 10:
            cleared += 1
        else:
            keep.append(ln[0])
    while len(keep) < GAME_ROWS:
        keep.insert(0, LINHA_VAZIA)
    for i in range(GAME_ROWS):
        tab[PREVIEW_ROWS+i][0] = keep[i]
    return cleared

def rotacao_valida(tab, pr, x, y):
    return x + largura_peca(pr) <= 10 and not colisao(tab, pr, x, y)

# ─────────────────────────────────────────────
# RENDERIZAÇÃO
# ─────────────────────────────────────────────
def quadro_score(score1, score2, lvl):
    linhas = [LINHA_VAZIA for _ in range(PREVIEW_ROWS+GAME_ROWS+2)]
    linhas[PREVIEW_ROWS]        = linha_texto("PLACAR")
    linhas[PREVIEW_ROWS+2]      = linha_texto(f"P1: {score1:05}")
    linhas[PREVIEW_ROWS+4]      = linha_texto(f"P2: {score2:05}")
    linhas[PREVIEW_ROWS+6]      = linha_texto(f"NÍVEL: {lvl}")
    return linhas

def render_duo(stdscr, t1, t2, sc1, sc2, level, extra=None):
    center = quadro_score(sc1, sc2, level)
    stdscr.clear()
    for a, c, b in zip(t1, center, t2):
        stdscr.addstr(a[0] + "  " + c + "  " + b[0] + '\n')
    if extra: stdscr.addstr(extra + '\n')
    stdscr.refresh()

def render_single(stdscr, tab, score, level, extra=None):
    stdscr.clear()
    for l in tab:
        stdscr.addstr(l[0] + '\n')
    stdscr.addstr(linha_texto(f"SCORE: {score:05}") + '\n')
    stdscr.addstr(linha_texto(f"NÍVEL: {level}") + '\n')
    if extra: stdscr.addstr(extra + '\n')
    stdscr.refresh()

# ─────────────────────────────────────────────
# TELAS DE MENU
# ─────────────────────────────────────────────
def tela_comandos(stdscr):
    stdscr.nodelay(False)
    tab = criar_tabuleiro()
    textos = [
        "COMANDOS",
        " Player1 (a/d/s/w)",
        " Player2 (←/→/↓/↑)",
        " w ou ↑ gira",
        " s ou ↓ desce",
        " níveis ↑ a cada 30s",
        " p pausa | q sai",
        " ENTER confirma"
    ]
    for i, t in enumerate(textos, PREVIEW_ROWS+1):
        tab[i][0] = linha_texto(t)
    render_single(stdscr, tab, 0, 1)
    stdscr.getch()

def menu(stdscr):
    opts = ["Jogar 1P", "Jogar 2P", "Comandos", "Sair"]
    sel  = 0
    stdscr.keypad(True)
    pontos = ["", ".", "..", "..."]
    t0 = time.time()
    anim_idx = 0

    while True:
        stdscr.nodelay(True)
        tab = criar_tabuleiro()

        # Animação no título
        if time.time() - t0 > 0.4:
            anim_idx = (anim_idx + 1) % len(pontos)
            t0 = time.time()

        tab[PREVIEW_ROWS][0] = linha_texto(f"TETRIS{pontos[anim_idx]}")

        for i, op in enumerate(opts):
            prefix = ">" if i == sel else " "
            tab[PREVIEW_ROWS+3+i][0] = linha_texto(f"{prefix} {op}")

        # Créditos institucionais
        tab[PREVIEW_ROWS+8][0]  = linha_texto("BIA UFG - 2025")
        tab[PREVIEW_ROWS+9][0]  = linha_texto("IP - PROF. LEO")
        tab[PREVIEW_ROWS+10][0] = linha_texto("ALUNO: GUSTAVO L.")

        render_single(stdscr, tab, 0, 1)

        try:
            k = stdscr.getkey()
        except:
            k = None

        if k:
            stdscr.nodelay(False)
            if k in ('w', 'KEY_UP'):
                sel = (sel - 1) % len(opts)
            elif k in ('s', 'KEY_DOWN'):
                sel = (sel + 1) % len(opts)
            elif k in ('\n', '\r'):
                return ["1P", "2P", "CMD", "QUIT"][sel]

# ─────────────────────────────────────────────
# PARTIDA 1P
# ─────────────────────────────────────────────
def partida_single(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    score = 0
    level = 1
    tab   = criar_tabuleiro()
    atual, proxima = random.choice(TODAS), random.choice(TODAS)
    x, y = 3, PREVIEW_ROWS
    last_rot = 0
    start_time = time.time()
    tick = 0
    paused = False

    while True:
        # atualiza nível e velocidade
        elapsed = time.time() - start_time
        level   = 1 + int(elapsed // LEVEL_STEP)
        sleep_t = max(MIN_SLEEP, BASE_SLEEP - (level-1)*SPEED_STEP)

        tmp = [l[:] for l in tab]
        desenhar_peca(tmp, atual, x, y)
        aplicar_preview(tmp, proxima)
        render_single(stdscr, tmp, score, level, "PAUSE" if paused else None)

        try: key = stdscr.getkey()
        except curses.error: key=None

        if key=='p': paused=not paused
        if paused: time.sleep(sleep_t); continue

        if   key=='a' and x>0 and not colisao(tab,atual,x-1,y): x-=1
        elif key=='d' and x+largura_peca(atual)<10 and not colisao(tab,atual,x+1,y): x+=1
        elif key=='s' and not colisao(tab,atual,x,y): y+=1
        elif key=='w':
            if time.time()-last_rot>0.15:
                nv=rotacionar(atual)
                if rotacao_valida(tab,nv,x,y): atual=nv; curses.flushinp(); last_rot=time.time()
        elif key=='q': return

        time.sleep(sleep_t); tick+=1
        drop_mod = 4
        if tick%drop_mod==0:
            if colisao(tab,atual,x,y):
                desenhar_peca(tab,atual,x,y)
                score += limpar_linhas(tab)
                atual,proxima=proxima,random.choice(TODAS)
                x,y=3,PREVIEW_ROWS
                if colisao_topo(tab,atual,x,y):
                    # Exibe tela de Game Over visual
                    base = PREVIEW_ROWS + 5
                    for i, msg in enumerate([
                        "<! ################### !>",
                        "<! ###  GAME OVER  ### !>",
                        "<! ################### !>",
                        LINHA_VAZIA,
                        "<! 'n' novo jogo  . . !>",
                        LINHA_VAZIA,
                        "<! 'p' sair . . . . . !>",
                        LINHA_VAZIA,
                    ]):
                        tab[base + i][0] = msg
                    render_single(stdscr, tab, score, level)
                    stdscr.nodelay(False)
                    while True:
                        g = stdscr.getkey()
                        if g == 'n':
                            stdscr.nodelay(True)
                            return partida_single(stdscr)
                        if g == 'p':
                            stdscr.addstr(linha_texto("Encerrando...") + '\n')
                            stdscr.refresh()
                            time.sleep(1.5)
                            return


            else: y+=1

# ─────────────────────────────────────────────
# PARTIDA 2P
# ─────────────────────────────────────────────
def partida_duo(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    start_time = time.time()
    level = 1

    players = []
    # P1
    players.append({
        "tab": criar_tabuleiro(),
        "atual": random.choice(TODAS),
        "proxima": random.choice(TODAS),
        "x":3,"y":PREVIEW_ROWS,
        "last_rot":0,
        "alive":True,
        "score":0,
        "keys":{'L':'a','R':'d','D':'s','T':'w'}
    })
    # P2
    players.append({
        "tab": criar_tabuleiro(),
        "atual": random.choice(TODAS),
        "proxima": random.choice(TODAS),
        "x":3,"y":PREVIEW_ROWS,
        "last_rot":0,
        "alive":True,
        "score":0,
        "keys":{'L':'KEY_LEFT','R':'KEY_RIGHT','D':'KEY_DOWN','T':'KEY_UP'}
    })

    tick=0; paused=False
    while True:
        elapsed = time.time() - start_time
        level   = 1 + int(elapsed // LEVEL_STEP)
        sleep_t = max(MIN_SLEEP, BASE_SLEEP - (level-1)*SPEED_STEP)

        t1,t2=[l[:] for l in players[0]["tab"]],[l[:] for l in players[1]["tab"]]
        for idx,tmp in enumerate([t1,t2]):
            pl=players[idx]
            if pl["alive"]:
                desenhar_peca(tmp,pl["atual"],pl["x"],pl["y"])
            aplicar_preview(tmp,pl["proxima"])
        render_duo(stdscr,t1,t2,players[0]["score"],players[1]["score"],level,"PAUSE" if paused else None)

        try:key=stdscr.getkey()
        except curses.error:key=None

        if key=='p': paused=not paused
        if paused: time.sleep(sleep_t); continue

        for pl in players:
            if not pl["alive"]: continue
            km=pl["keys"]
            if   key==km['L'] and pl["x"]>0 and not colisao(pl["tab"],pl["atual"],pl["x"]-1,pl["y"]): pl["x"]-=1
            elif key==km['R'] and pl["x"]+largura_peca(pl["atual"])<10 and not colisao(pl["tab"],pl["atual"],pl["x"]+1,pl["y"]): pl["x"]+=1
            elif key==km['D'] and not colisao(pl["tab"],pl["atual"],pl["x"],pl["y"]): pl["y"]+=1
            elif key==km['T']:
                if time.time()-pl["last_rot"]>0.15:
                    nv=rotacionar(pl["atual"])
                    if rotacao_valida(pl["tab"],nv,pl["x"],pl["y"]):
                        pl["atual"]=nv; curses.flushinp(); pl["last_rot"]=time.time()
        if key=='q': return

        time.sleep(sleep_t); tick+=1
        drop_mod=4
        if tick%drop_mod==0:
            for pl in players:
                if not pl["alive"]: continue
                if colisao(pl["tab"],pl["atual"],pl["x"],pl["y"]):
                    desenhar_peca(pl["tab"],pl["atual"],pl["x"],pl["y"])
                    pl["score"]+=limpar_linhas(pl["tab"])
                    pl["atual"],pl["proxima"]=pl["proxima"],random.choice(TODAS)
                    pl["x"],pl["y"]=3,PREVIEW_ROWS
                    if colisao_topo(pl["tab"],pl["atual"],pl["x"],pl["y"]):
                        pl["alive"]=False
                        base=PREVIEW_ROWS+4
                        for i,m in enumerate([
                            "<! ################### !>",
                            "<! ###    OUT!    ### !>",
                            "<! ################### !>"]):
                            pl["tab"][base+i][0]=m
                else:
                    pl["y"]+=1

            if not any(p["alive"] for p in players):
                base=PREVIEW_ROWS+4
                final=[
                    "<! ################### !>",
                    "<! ###  GAME OVER  ### !>",
                    "<! ################### !>",
                    LINHA_VAZIA,
                    "<! 'n' novo jogo  . . !>",
                    LINHA_VAZIA,
                    "<! 'p' sair . . . . . !>",
                    LINHA_VAZIA]
                for pl in players:
                    for i,m in enumerate(final):
                        pl["tab"][base+i][0]=m
                render_duo(stdscr,players[0]["tab"],players[1]["tab"],players[0]["score"],players[1]["score"],level)
                stdscr.nodelay(False)
                while True:
                    kg=stdscr.getkey()
                    if kg=='n':
                        stdscr.nodelay(True); return partida_duo(stdscr)
                    if kg=='p':
                        return

# ─────────────────────────────────────────────
def main(stdscr):
    while True:
        acao=menu(stdscr)
        if acao=='1P': partida_single(stdscr)
        elif acao=='2P': partida_duo(stdscr)
        elif acao=='CMD': tela_comandos(stdscr)
        else: break

if __name__=='__main__':
    curses.wrapper(main)
