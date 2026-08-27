---
name: llm-conversation-gif
description: "Crea una GIF animata che simula un coding agent al lavoro, per post sui social: in alto la bubble del prompt utente digitata a macchina, sotto l'output in stile terminale scuro che scorre. Due modalità — double (2 colonne sincronizzate: a sinistra l'azione dichiarata, a destra cosa l'agente pensa davvero, in fade-in comico) e single (1 colonna a piena larghezza, solo l'azione, senza battuta). Usa questa skill quando l'utente chiede 'fai una GIF stile Claude Code', 'GIF pensieri veri', 'GIF doppia colonna', 'GIF a una colonna', 'una GIF come quella del CRM', o vuole riusare questo formato con un prompt e degli step diversi. Se l'utente non specifica la modalità, chiedila prima di generare."
---

# LLM Conversation GIF

Genera una GIF animata che imita l'output di un coding agent che lavora in locale.
In alto una bubble fissa mostra il prompt dell'utente, digitato carattere per
carattere. Sotto, l'output scorre in una delle due modalità.

Il deliverable è un singolo file `.gif` ottimizzato, sotto 1.5MB, pronto da
allegare a un post.

## Le due modalità

**`double`** — due colonne sincronizzate, separate da un divisore verticale.

- Sinistra (bianco, grassetto): l'azione dichiarata dall'agente, con una riga
  secondaria grigia `Ran 7 commands  ›` per verosimiglianza.
- Destra (arancione): cosa l'agente "pensa davvero" — la battuta comica — che
  compare in fade-in dopo che l'azione è stata scritta.
- Il contrasto comico sta fra l'entusiasmo posticcio del tono professionale a
  sinistra e il pensiero cinico a destra.

**`single`** — una colonna sola a piena larghezza.

- Solo l'azione e la riga `Ran N commands`. Nessun pensiero, nessun divisore.
- Serve quando l'utente vuole un formato più sobrio, senza il layer satirico:
  mostra "il lavoro che fa l'agente" e basta.

## Quando NON usare questa skill

- Per una GIF qualsiasi (screen recording, animazione di prodotto, meme): questa
  skill produce **solo** questo formato specifico.
- Per un mockup statico o uno screenshot di conversazione: qui il valore è
  l'animazione, se serve un'immagine ferma non usare questa skill.
- Per un cambio strutturale del formato ("tre colonne", "verticale per Instagram",
  "tema chiaro"): trattalo come una richiesta nuova, conferma con l'utente prima
  di riscrivere il motore di rendering.

## Prerequisiti

- **Python 3** con **Pillow** (`pip install Pillow`). Senza Pillow lo script non
  parte: installala, non aggirare il problema generando la GIF in altro modo.
- **Un font TrueType di sistema.** Lo script prova DejaVu, Liberation, Arial
  (macOS e Windows) in quest'ordine. Se non ne trova nessuno si ferma con un
  errore esplicito invece di ripiegare sul font di default di Pillow, che a
  queste dimensioni è illeggibile. Su Debian/Ubuntu:
  `apt-get install -y fonts-dejavu-core`.
  Se il corsivo della famiglia scelta non è installato, il pensiero viene reso in
  tondo: è una degradazione accettabile, non un errore.
- **`gifsicle`** per l'ottimizzazione finale (`apt-get install -y gifsicle`).
  Se manca, **dillo all'utente** e consegna comunque la GIF non ottimizzata
  segnalando il peso reale — non spacciare per pronto un file da 7MB che i social
  rifiutano.

## Workflow

### 1. Determina la modalità

Se l'utente non la specifica ("a due colonne"/"con i pensieri" → `double`; "una
colonna sola"/"solo l'azione" → `single`), chiedila con una domanda diretta prima
di procedere: *"Doppia colonna (con il pensiero comico) o una colonna sola (solo
l'azione)?"*.

### 2. Raccogli i contenuti

Servono:

- **Il prompt utente iniziale**, una frase sola, in prima persona, del tipo che
  scriverebbe qualcuno di poco tecnico.
- **Una lista di step**, ciascuno con l'azione dichiarata (breve, come la
  scriverebbe un coding agent reale: "Preparo...", "Configuro...", "Genero...")
  e un numero 2-9 per `Ran N commands`. In modalità `double` serve anche il
  pensiero per ogni step.

Se l'utente fornisce già un post o un testo pronto, **estrai da lì** prompt e
step invece di chiedere da capo. Se manca solo un pezzo, chiedi solo quello: non
ridiscutere il formato ogni volta.

### 3. Scrivi il file di contenuti

Copia `assets/example-config.json` e riempilo. È la strada preferita: non tocchi
lo script e puoi rigenerare varianti cambiando solo il JSON.

```json
{
  "mode": "double",
  "user_prompt": "...",
  "steps": [
    {"action": "Preparo l'ambiente...", "thought": "...", "commands": 7}
  ]
}
```

In modalità `single` il campo `thought` si può omettere. In modalità `double` è
obbligatorio su ogni step: lo script si ferma con un errore se ne manca uno.

### 4. Genera

```bash
python3 scripts/generate_gif.py --config contenuti.json --output out/agent.gif
```

Senza `--config` lo script usa i contenuti di default che porta dentro: comodo
per una prova, non per una consegna.

### 5. Ottimizza SEMPRE il peso

La `double` non ottimizzata pesa 7-10MB, troppo per un post. La `single` è più
leggera (~2-3MB) ma va passata da gifsicle lo stesso.

```bash
gifsicle -O3 --colors 48 --lossy=80 out/agent.gif -o out/agent_opt.gif
```

Target: **sotto 1.5MB**. Se è ancora troppo pesante, scendi a `--colors 32`,
oppure riduci `W, H` nello script (1100x640 → 950x560).

### 6. Verifica visivamente prima di consegnare

Estrai 2-3 frame chiave e guardali davvero:

```python
from PIL import Image
im = Image.open("out/agent_opt.gif")
for n in (12, 60, 200):
    im.seek(n); im.convert("RGB").save(f"check_{n}.png")
```

Controlla almeno un frame durante la digitazione del prompt, uno a metà scroll e
uno sull'ultimo step. Cerca in particolare:

- sovrapposizioni fra la bubble del prompt e la prima riga di contenuto — se
  capita, alza `PROMPT_AREA_H` o `PROMPT_LINES_MAX`;
- in modalità `single`, un divisore verticale residuo (non deve esserci).

## Timing

I default sono calibrati e raramente vanno toccati:

| Parametro | Default | Nota |
|---|---|---|
| `FPS` | 14 | |
| `READ_PAUSE_PER_STEP` | 55 | ~4s di pausa per leggere ogni blocco in `double`. Alzalo se serve più lento; non scendere sotto 30. |
| `READ_PAUSE_PER_STEP_SINGLE` | 32 | in `single` non c'è pensiero da leggere, si può stare più stretti |
| `CHARS_PER_FRAME_ACTION` | 4 | velocità digitazione azione |
| `CHARS_PER_FRAME_PROMPT` | 3 | velocità digitazione prompt |

## Note di stile per i pensieri (modalità `double`)

- I pensieri funzionano meglio in **terza persona** ("non sa nemmeno cosa sia...",
  "sarà contento così...") che in prima persona diretta.
- L'iperbole per confronto — paragonare l'utente a una figura fuori scala rispetto
  a quello che sta facendo — è il meccanismo comico principale. Uno per step, mai
  ripetuto.
- Le osservazioni meta sull'AI stessa (che gli LLM sbagliano, i dataset di
  addestramento) funzionano, ma **massimo 1-2 per GIF**.
- L'ultimo step (deploy, fine lavoro) è il punto della battuta finale, la più
  lunga e a effetto.
- **Non spiegare il gioco.** Niente meta-commento tipo "ecco cosa pensa davvero
  l'AI" dentro la GIF: la si lascia parlare da sola.

## Cosa non cambiare senza chiederlo

Layout, palette, font, dimensioni del canvas (1100x640) e la meccanica del prompt
digitato in alto sono stati validati su più iterazioni in entrambe le modalità.
Se l'utente chiede contenuti diversi, cambia solo il JSON dei contenuti.

## Esempio d'uso

**Utente:** *"Fammi una GIF stile Claude Code su uno che si vuole fare il sito
della pasticceria da solo."*

Claude non trova la modalità nel messaggio, quindi chiede: *"Doppia colonna (con
il pensiero comico) o una colonna sola (solo l'azione)?"* — l'utente risponde
"doppia".

Claude scrive `pasticceria.json`:

```json
{
  "mode": "double",
  "user_prompt": "Mi serve un sito per la mia pasticceria, ma semplice, tipo due pagine",
  "steps": [
    {"action": "Preparo l'ambiente di sviluppo...",
     "thought": "due pagine. Sta per ricevere un progetto con 340 file di configurazione",
     "commands": 6},
    {"action": "Configuro il build system e la pipeline di deploy...",
     "thought": "una pipeline di deploy. Per le paste. Che cambiano listino due volte l'anno",
     "commands": 4},
    {"action": "Fatto! Il tuo sito è online",
     "thought": "online sì. Poi però le foto dei cannoli le manda su WhatsApp come sempre",
     "commands": 2}
  ]
}
```

Poi genera e ottimizza:

```bash
$ python3 scripts/generate_gif.py --config pasticceria.json --output out/pasticceria.gif
mode: double — frame totali generati: 312
scritto out/pasticceria.gif — 2481.3 KB
n_frames riletti: 78
ATTENZIONE: sopra 1.5MB. Passa da gifsicle prima di consegnare.

$ gifsicle -O3 --colors 48 --lossy=80 out/pasticceria.gif -o out/pasticceria_opt.gif
$ du -h out/pasticceria_opt.gif
712K	out/pasticceria_opt.gif
```

Estrae due frame, controlla che la bubble non si sovrapponga al testo, e consegna
`pasticceria_opt.gif`.

> Nota sui frame: lo script genera più frame di quanti la GIF ne riporti. Pillow
> accorpa i frame identici consecutivi sommandone le durate, quindi il numero
> scende ma la durata dell'animazione resta quella prevista
> (`frame generati / FPS` secondi). Non è un bug e non serve correggerlo.
