"""
Genera una GIF in stile "coding agent": in alto una bubble fissa con il prompt
dell'utente, digitato con effetto typewriter. Sotto, l'output dell'agente in
stile terminale scuro — in due modalità:

- mode = "double": due colonne sincronizzate. Sinistra = azione dichiarata,
  destra = cosa l'agente "pensa davvero" in tono comico (fade-in dopo l'azione).
- mode = "single": una colonna sola, larghezza piena. Solo l'azione dichiarata
  (nessun pensiero, nessuna seconda colonna, nessun divisore verticale).

COME USARLO
-----------
Due strade, entrambe valide:

1. Con un file di contenuti JSON (consigliato: non tocchi lo script):

       python3 generate_gif.py --config contenuti.json --output out/demo.gif

   Formato del JSON:

       {
         "mode": "double",
         "user_prompt": "...",
         "steps": [
           {"action": "Preparo l'ambiente...", "thought": "...", "commands": 7}
         ]
       }

   In mode "single" il campo "thought" può essere omesso o lasciato vuoto.

2. Modificando la sezione "CONTENUTI DI DEFAULT" qui sotto ed eseguendo
   `python3 generate_gif.py`. Copia prima lo script in una directory
   scrivibile se la cartella della skill è in sola lettura.

Ottimizza SEMPRE il peso con gifsicle prima di consegnare (vedi SKILL.md):

    gifsicle -O3 --colors 48 --lossy=80 out/demo.gif -o out/demo_opt.gif
"""

import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFont

# ============================================================
# CONTENUTI DI DEFAULT
# Servono da demo eseguibile e da esempio del formato.
# Per una GIF vera, passa un --config JSON invece di editare qui.
# ============================================================

# "double" = 2 colonne (azione + pensiero in fade-in)
# "single" = 1 colonna a piena larghezza (solo azione)
DEFAULT_MODE = "double"

DEFAULT_USER_PROMPT = (
    "Vorrei realizzare il mio CRM per gestire i miei 4 clienti, "
    "perché i software attuali non sono fatti bene"
)

# Ogni step: (azione mostrata a sinistra, pensiero vero a destra, numero finto di comandi)
# - L'azione va scritta come farebbe un coding agent reale ("Preparo...", "Configuro...")
# - Il pensiero è la battuta comica (ignorato in mode "single")
# - commands è un numero a caso 2-9, solo per verosimiglianza della riga "Ran N commands"
DEFAULT_STEPS = [
    ("Preparo l'ambiente di sviluppo...",
     "ecco un altro CEO visionario. Deve gestire 4 contatti.. e gli serve un CRM.. "
     "custom.. che poi sicuramente nemmeno sa cosa vuol dire CRM",
     7),
    ("Genero la struttura: models/ views/ controllers/...",
     "creiamo una struttura overcomplicata per un'anagrafica che stava benissimo "
     "su un foglio di calcolo, bah contento lui",
     4),
    ("Installo le dipendenze: 47 pacchetti npm...",
     "47 pacchetti per salvare nome, cognome e data appuntamento.. l'indirizzo email "
     "non glielo inserisco appositamente così appena se ne accorge poi può dare la "
     "lezioncina che \"gli LLM a volte sbagliano\"",
     3),
    ("Configuro il database PostgreSQL...",
     "un database... PostgreSQL!!! Per 4 righe. Andava bene anche un post-it sul "
     "monitor, ma no qui vogliamo cambiare il mondo! Ci sono più CRM in giro che clienti..",
     6),
    ("Implemento l'autenticazione multi-utente...",
     "multi-utente. È solo lui. Da solo. Con 4 clienti. Ma \"multi-utente\" sono sicuro "
     "che lo farà sentire il fondatore di un unicorno",
     5),
    ("Aggiungo una dashboard con grafici in tempo reale...",
     "grafici in tempo reale su 4 clienti, LOL, ma sarà contento così andrà a flexare "
     "che \"data is the new oil\" (ma new era 10 anni fa)",
     4),
    ("Scrivo i test automatici...",
     "zero test passati, ma tanto chi controlla, non sa nemmeno cosa sono i test "
     "automatici e poi la cartella tests/ fa scena benissimo",
     8),
    ("Deploy in produzione...",
     "produzione. Dominio, certificato SSL, container, zero utenti oltre a lui. Tutte "
     "cose che non sa nemmeno cosa siano, ma sicuro lo faranno sentire un titano del tech",
     9),
    ("Fatto! Il tuo CRM è pronto",
     "vai campione! Hungry e foolish mi raccomando. Fra 1 settimana non si ricorderà "
     "nemmeno più dove è stato deployato e come ci si accede..",
     2),
]

# Relativo alla directory da cui lanci lo script. Sovrascrivibile con --output.
DEFAULT_OUTPUT_PATH = "output/llm-conversation.gif"

# ============================================================
# PARAMETRI DI TIMING (toccare solo se serve più/meno velocità)
# ============================================================

FPS = 14
CHARS_PER_FRAME_PROMPT = 3      # velocità digitazione prompt utente
CHARS_PER_FRAME_ACTION = 4      # velocità digitazione azione (colonna sx)
HOLD_AFTER_PROMPT = 14          # frame di pausa col prompt completo prima di iniziare
HOLD_AFTER_ACTION = 4           # pausa dopo il typewriter dell'azione
HOLD_AFTER_SUBLINE = 6          # pausa dopo comparsa "Ran N commands"
FADE_STEP_ALPHA = 34            # incremento alpha del fade-in del pensiero (più basso = più lento)
READ_PAUSE_PER_STEP = 55        # pausa di lettura su ogni blocco (~4s a 14fps) — ALZARE per andare più piano
FINAL_PAUSE = 40                # pausa sull'ultimo frame

# In mode "single" non c'è pensiero da leggere: si può stare più stretti.
READ_PAUSE_PER_STEP_SINGLE = 32

# ============================================================
# MOTORE DI RENDERING (di norma non serve toccare da qui in giù)
# ============================================================

W, H = 1100, 640
BG = (23, 23, 23)
WHITE = (230, 230, 230)
GRAY = (128, 128, 128)
THOUGHT = (240, 146, 74)     # arancione per il pensiero
DIVIDER = (70, 70, 70)
BUBBLE_FILL = (44, 44, 44)

FS_ACTION = 21
FS_SUB = 18
FS_THOUGHT = 19
FS_PROMPT = 19

# Famiglie di font provate in ordine. Ogni voce è (regular, bold, oblique).
# L'oblique è opzionale: se manca si ricade sul regular, il pensiero resta
# leggibile ma non corsivo.
FONT_CANDIDATES = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
     "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
     "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"),
    ("/Library/Fonts/Arial.ttf",
     "/Library/Fonts/Arial Bold.ttf",
     "/Library/Fonts/Arial Italic.ttf"),
    ("/System/Library/Fonts/Supplemental/Arial.ttf",
     "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
     "/System/Library/Fonts/Supplemental/Arial Italic.ttf"),
    ("C:/Windows/Fonts/arial.ttf",
     "C:/Windows/Fonts/arialbd.ttf",
     "C:/Windows/Fonts/ariali.ttf"),
]


def resolve_fonts():
    """Trova una famiglia di font utilizzabile.

    Restituisce (regular, bold, oblique) come percorsi, dove bold e oblique
    ricadono sul regular se il file specifico non esiste. Solleva
    RuntimeError se nessuna famiglia è disponibile: meglio fermarsi che
    produrre una GIF con il font di default di PIL, illeggibile a queste
    dimensioni.
    """
    for regular, bold, oblique in FONT_CANDIDATES:
        if os.path.exists(regular):
            return (
                regular,
                bold if os.path.exists(bold) else regular,
                oblique if os.path.exists(oblique) else regular,
            )
    raise RuntimeError(
        "Nessun font TrueType trovato. Installane uno (es. su Debian/Ubuntu: "
        "apt-get install -y fonts-dejavu-core) oppure aggiungi il percorso "
        "della tua famiglia di font a FONT_CANDIDATES."
    )


F_REG, F_BOLD, F_IT = resolve_fonts()

font_action = ImageFont.truetype(F_BOLD, FS_ACTION)
font_sub = ImageFont.truetype(F_REG, FS_SUB)
font_thought = ImageFont.truetype(F_IT, FS_THOUGHT)
font_prompt = ImageFont.truetype(F_REG, FS_PROMPT)

PAD_X = 56
COL_GAP = 40
LEFT_X = PAD_X

BUBBLE_MAX_W = 620
BUBBLE_PAD_X = 18
BUBBLE_PAD_Y = 14
BUBBLE_LINE_H = 26
PROMPT_TOP = 22
PROMPT_LINES_MAX = 2  # se il prompt è molto più lungo, alza questo valore
PROMPT_AREA_H = PROMPT_TOP + PROMPT_LINES_MAX * BUBBLE_LINE_H + BUBBLE_PAD_Y * 2 + 34

AREA_TOP = PROMPT_AREA_H
AREA_BOTTOM = H - 20
LINE_H = 30
GAP_ROWS = 1


class Layout:
    """Geometria delle colonne, che dipende dalla modalità."""

    def __init__(self, mode):
        self.mode = mode
        if mode == "single":
            self.col_w = W - PAD_X * 2
        else:
            self.col_w = (W - PAD_X * 2 - COL_GAP) // 2
        self.right_x = PAD_X + self.col_w + COL_GAP
        self.divider_x = PAD_X + self.col_w + COL_GAP // 2


def wrap_text(text, fnt, max_width):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if fnt.getlength(trial) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def blend(color, alpha):
    if alpha >= 255:
        return color
    return tuple(int(BG[k] + (color[k] - BG[k]) * (alpha / 255)) for k in range(3))


def draw_prompt_bubble(draw, display_text):
    wrapped = wrap_text(display_text, font_prompt, BUBBLE_MAX_W - BUBBLE_PAD_X * 2)
    if not wrapped:
        wrapped = ['']
    n_lines = len(wrapped)
    bubble_h = n_lines * BUBBLE_LINE_H + BUBBLE_PAD_Y * 2
    bubble_w = min(BUBBLE_MAX_W,
                   max(font_prompt.getlength(l) for l in wrapped) + BUBBLE_PAD_X * 2)
    x1 = W - PAD_X
    x0 = x1 - bubble_w
    y0 = PROMPT_TOP
    y1 = y0 + bubble_h
    draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=BUBBLE_FILL)
    ty = y0 + BUBBLE_PAD_Y
    for line in wrapped:
        tw = font_prompt.getlength(line)
        draw.text((x1 - BUBBLE_PAD_X - tw, ty), line, font=font_prompt, fill=WHITE)
        ty += BUBBLE_LINE_H
    return y1


def draw_static_chrome(draw, prompt_display_text, layout):
    draw.rectangle([0, 0, W, PROMPT_AREA_H], fill=BG)
    draw_prompt_bubble(draw, prompt_display_text)
    bar_y = PROMPT_AREA_H - 12
    draw.line([(0, bar_y), (W, bar_y)], fill=DIVIDER, width=1)
    if layout.mode == "double":
        draw.line([(layout.divider_x, PROMPT_AREA_H + 6), (layout.divider_x, H - 10)],
                  fill=DIVIDER, width=2)


def render(committed, layout, prompt_text, active_left=None, active_right=None,
           active_right_alpha=255):
    frame = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(frame)
    draw_static_chrome(draw, prompt_text, layout)

    blocks = list(committed)
    if active_left is not None or active_right is not None:
        blocks.append({'left': active_left or [], 'right': active_right or []})

    row = 0
    positions = []
    for b in blocks:
        positions.append((b, row))
        rows = max(len(b['left']), len(b['right']), 1) + GAP_ROWS
        row += rows
    total_rows = row

    visible_rows = (AREA_BOTTOM - AREA_TOP) // LINE_H
    scroll_offset = max(0, total_rows - visible_rows)

    is_last = len(blocks) - 1
    for bi, (b, start_row) in enumerate(positions):
        for i, (text, color, fnt) in enumerate(b['left']):
            r = start_row + i
            y = AREA_TOP + (r - scroll_offset) * LINE_H
            if AREA_TOP - LINE_H <= y <= AREA_BOTTOM:
                draw.text((LEFT_X, y), text, font=fnt, fill=color)
        for i, (text, color, fnt) in enumerate(b['right']):
            r = start_row + i
            y = AREA_TOP + (r - scroll_offset) * LINE_H
            c = color
            if bi == is_last and active_right_alpha < 255:
                c = blend(color, active_right_alpha)
            if AREA_TOP - LINE_H <= y <= AREA_BOTTOM:
                draw.text((layout.right_x, y), text, font=fnt, fill=c)
    return frame


def build_frames(mode, user_prompt, steps):
    layout = Layout(mode)
    read_pause = READ_PAUSE_PER_STEP_SINGLE if mode == "single" else READ_PAUSE_PER_STEP
    frames = []
    committed = []

    for i in range(0, len(user_prompt) + 1, CHARS_PER_FRAME_PROMPT):
        partial = user_prompt[:i]
        cursor = "\u258c" if (i // 6) % 2 == 0 else ""
        frames.append(render(committed, layout, partial + cursor))
    for _ in range(HOLD_AFTER_PROMPT):
        frames.append(render(committed, layout, user_prompt))

    for action_text, thought_text, n_cmd in steps:
        for i in range(0, len(action_text) + 1, CHARS_PER_FRAME_ACTION):
            partial = action_text[:i]
            wrapped = wrap_text(partial + ("\u258c" if (i // 6) % 2 == 0 else ""),
                                font_action, layout.col_w)
            left_lines = [(t, WHITE, font_action) for t in wrapped] or [("", WHITE, font_action)]
            frames.append(render(committed, layout, user_prompt,
                                 active_left=left_lines, active_right=[]))

        wrapped_final = wrap_text(action_text, font_action, layout.col_w)
        left_final = [(t, WHITE, font_action) for t in wrapped_final]
        for _ in range(HOLD_AFTER_ACTION):
            frames.append(render(committed, layout, user_prompt,
                                 active_left=left_final, active_right=[]))

        left_with_sub = left_final + [(f"Ran {n_cmd} commands   \u203a", GRAY, font_sub)]
        for _ in range(HOLD_AFTER_SUBLINE):
            frames.append(render(committed, layout, user_prompt,
                                 active_left=left_with_sub, active_right=[]))

        if mode == "double":
            wrapped_thought = wrap_text(thought_text, font_thought, layout.col_w)
            right_final = [(t, THOUGHT, font_thought) for t in wrapped_thought]
            for alpha in range(0, 256, FADE_STEP_ALPHA):
                frames.append(render(committed, layout, user_prompt,
                                     active_left=left_with_sub,
                                     active_right=right_final, active_right_alpha=alpha))
        else:
            right_final = []

        for _ in range(read_pause):
            frames.append(render(committed, layout, user_prompt,
                                 active_left=left_with_sub, active_right=right_final))

        committed.append({'left': left_with_sub, 'right': right_final})

    for _ in range(FINAL_PAUSE):
        frames.append(render(committed, layout, user_prompt))

    return frames


def load_config(path):
    """Legge mode/user_prompt/steps da un JSON e li valida."""
    with open(path, encoding='utf-8') as fh:
        data = json.load(fh)

    mode = data.get("mode", DEFAULT_MODE)
    if mode not in ("double", "single"):
        raise ValueError(f"mode deve essere 'double' o 'single', trovato: {mode!r}")

    user_prompt = data.get("user_prompt")
    if not user_prompt:
        raise ValueError("il config deve contenere 'user_prompt' non vuoto")

    raw_steps = data.get("steps") or []
    if not raw_steps:
        raise ValueError("il config deve contenere almeno uno step in 'steps'")

    steps = []
    for i, s in enumerate(raw_steps, 1):
        action = s.get("action")
        if not action:
            raise ValueError(f"step {i}: campo 'action' mancante o vuoto")
        thought = s.get("thought", "")
        if mode == "double" and not thought:
            raise ValueError(
                f"step {i}: in mode 'double' serve un 'thought' per ogni step"
            )
        steps.append((action, thought, int(s.get("commands", 4))))

    return mode, user_prompt, steps


def main():
    parser = argparse.ArgumentParser(
        description="Genera la GIF stile coding agent (mode double o single)."
    )
    parser.add_argument("--config",
                        help="file JSON con mode/user_prompt/steps. "
                             "Senza questo flag usa i contenuti di default nello script.")
    parser.add_argument("--mode", choices=["double", "single"],
                        help="sovrascrive il mode del config o del default.")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH,
                        help=f"percorso della GIF in uscita (default: {DEFAULT_OUTPUT_PATH})")
    args = parser.parse_args()

    if args.config:
        mode, user_prompt, steps = load_config(args.config)
    else:
        mode, user_prompt, steps = DEFAULT_MODE, DEFAULT_USER_PROMPT, DEFAULT_STEPS

    if args.mode:
        mode = args.mode

    frames = build_frames(mode, user_prompt, steps)
    print(f"mode: {mode} — frame totali generati: {len(frames)}")

    out_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(out_dir, exist_ok=True)
    frames[0].save(
        args.output,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=False,
        disposal=2,
    )

    size_kb = os.path.getsize(args.output) / 1024
    print(f"scritto {args.output} — {size_kb:.1f} KB")
    check = Image.open(args.output)
    print("n_frames riletti:", check.n_frames)
    if size_kb > 1500:
        print("ATTENZIONE: sopra 1.5MB. Passa da gifsicle prima di consegnare "
              "(vedi SKILL.md, punto 'Ottimizza il peso').")


if __name__ == "__main__":
    main()
