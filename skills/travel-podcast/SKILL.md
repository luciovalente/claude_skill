---
name: travel-podcast
description: "Genera un mini-podcast HTML narrato (via Web Speech API del browser, voce italiana) su un luogo specifico che l'utente sta visitando o vuole conoscere — monumento, città, museo, sito naturalistico, ecc. Produce un UNICO file HTML con tre modalità di narrazione selezionabili a runtime (Avventuroso/ragazzi, Bambini, Adulti), capitoli navigabili, evidenziazione del testo durante la lettura, e controlli play/pausa/stop. Usa questa skill ogni volta che l'utente chiede un 'podcast' o una 'audioguida' su un luogo, dice 'spiegami dove siamo/cosa stiamo vedendo', 'crea un audio su [luogo]', 'guida vocale per [posto]', o chiede di raccontare un sito con toni diversi per età diverse. Non richiede file audio pre-registrati, la voce viene generata dal browser al volo."
---

# Travel Podcast

Skill per generare audioguide HTML autonome (nessun hosting, nessun file audio esterno) su un luogo, con tre stili di narrazione selezionabili dall'utente nello stesso file.

## Prerequisiti

- Nessuna dipendenza, nessuna API key, nessun file audio: la voce è sintetizzata dal browser.
- Il file `assets/template.html` deve trovarsi accanto a questo `SKILL.md`.
- Per l'ascolto serve un browser con supporto alla **Web Speech API** e almeno una voce
  italiana installata nel sistema (Chrome, Edge e Safari la supportano; Firefox richiede
  che le voci siano abilitate a livello di sistema operativo). Il player degrada in modo
  visibile: se non trova una voce italiana lo segnala invece di leggere con un accento sbagliato.

## Come funziona

1. Copia `assets/template.html` come base.
2. Genera **tre script separati** per lo stesso luogo — uno per modalità (vedi sotto "Tre modalità").
3. Sostituisci nel template:
   - `{{LUOGO}}` → nome del luogo (es. "Abbazia di San Galgano")
   - `{{ICON}}` → un'emoji pertinente al luogo (🏛️ per rovine/chiese, 🏰 per castelli, ⛰️ per natura, 🏙️ per città, ecc.)
   - `{{SOTTOTITOLO}}` → una riga breve descrittiva (es. "La chiesa senza tetto e il colle della spada")
   - `{{SCRIPT_AVVENTUROSO_JSON}}`, `{{SCRIPT_BAMBINI_JSON}}`, `{{SCRIPT_ADULTI_JSON}}` → array JSON di capitoli, formato descritto sotto
   - `{{HUNT_ITEMS_JSON}}` → array JSON di stringhe per la caccia al tesoro (vedi sotto "Caccia al tesoro")
4. Salva il file risultante con un nome slug del luogo (es. `abbazia-san-galgano-podcast.html`) nella directory di output dell'ambiente in cui stai girando, e comunica all'utente il percorso completo del file. Il file è autonomo: si apre con un doppio click nel browser, non serve un server.

## Input dall'utente

Prima di generare, assicurati di avere:
- **Il luogo** (obbligatorio). Se ambiguo o generico, chiedi di specificare (es. "Duomo di Siena" vs "Siena" — meglio un punto preciso che una città intera).
- **Fatti specifici da includere**, se il luogo è poco noto o l'utente ne ha già di propri (facoltativo — altrimenti scrivi dalla tua conoscenza generale, e se hai dubbi su dettagli fattuali specifici e verificabili, fai una ricerca web prima di scrivere lo script).

Non serve altro: le tre modalità si generano sempre tutte e tre, l'utente sceglie quale ascoltare nel player.

## Formato di ogni script (JSON per capitoli)

Ogni modalità è un array di capitoli, ognuno con `titolo` e `paragrafi` (array di stringhe, ognuna diventa un'unità di lettura/evidenziazione):

```json
[
  {
    "titolo": "Dove siete",
    "paragrafi": [
      "Primo paragrafo...",
      "Secondo paragrafo..."
    ]
  },
  {
    "titolo": "Un altro capitolo",
    "paragrafi": ["..."]
  }
]
```

Regole:
- 4-6 capitoli per modalità, per un totale di 800-1400 parole per script (equivalgono a circa 6-10 minuti di ascolto).
- Ogni paragrafo va scritto per essere **letto ad alta voce**: frasi non troppo lunghe, niente di illeggibile per un sintetizzatore vocale (evita sigle non pronunciabili, abbreviazioni ambigue, notazioni tipo "XII sec." — scrivi per esteso "dodicesimo secolo").
- Il JSON va inserito **letteralmente** al posto del placeholder nel template (sostituisci l'intera stringa `{{SCRIPT_X_JSON}}` con l'array, senza virgolette attorno).
- Occhio agli apici: se il testo contiene virgolette doppie, usa l'apostrofo tipografico (') o riformula, per non rompere il JSON.

## Caccia al tesoro (solo modalità bambini)

Sotto il toggle delle modalità, quando è selezionato "Bambini", appare una checklist interattiva: i bambini spuntano gli oggetti/dettagli mentre li trovano davanti a loro. Genera sempre questa lista insieme ai tre script.

Formato: array semplice di stringhe in `{{HUNT_ITEMS_JSON}}`, es.

```json
[
  "Una finestra rotonda",
  "Un punto dove cresce l'erba invece del pavimento"
]
```

Regole — questa è la parte più delicata della skill:
- **Ogni elemento deve essere reale e verificabile sul posto**, non inventato. Se non sei sicuro al 100% che un dettaglio esista fisicamente nel luogo (una statua precisa, un'iscrizione, un colore specifico), non includerlo: meglio un elemento generico ma sicuro ("una colonna alta", "un arco a punta") che uno specifico ma incerto.
- Se il luogo è poco noto o hai dubbi sui dettagli architettonici/decorativi, fai una ricerca web prima di scrivere la lista, o chiedi controllo/conferma dei dettagli fisici all'utente.
- 5-8 elementi, tutti trovabili senza spostarsi troppo o senza permessi speciali (niente "apri quella porta chiusa" o "chiedi al custode di mostrarti...").
- Linguaggio semplice, adatto a un bambino che legge o si fa leggere la lista (stesso registro della modalità bambini).
- Evita elementi pericolosi da raggiungere (bordi, altezze, aree transennate) o oggetti facilmente rimossi/stagionali (potrebbero non esserci più al momento della visita).
- Se il luogo è al chiuso in un museo con vetrine, va bene includere oggetti esposti, ma verifica che siano parte dell'allestimento permanente.



Non limitarti ad "abbassare il registro" dello stesso testo — sono tre narrazioni diverse per intento:

**Avventuroso (ragazzi/adolescenti)**
- Tono da racconto: mistero, sfida, dettagli epici o macabri quando pertinenti (leggende, battaglie, maledizioni, enigmi irrisolti).
- Seconda persona, ritmo incalzante, qualche domanda retorica ("Vi siete mai chiesti come...").
- Va bene includere teorie alternative, controversie storiche, dettagli "da brivido".

**Bambini**
- Vocabolario semplice, frasi brevi, niente date precise o cifre complesse (usa "tanto, tanto tempo fa" invece di "nel 1220").
- Paragoni con cose che un bambino conosce (animali, favole, dimensioni familiari).
- Tono caldo e curioso, mai spaventoso — le leggende vanno addolcite, non tolte.
- Evita crolli, morte, violenza esplicita anche se storicamente presenti: accennali con delicatezza o saltali.

**Adulti**
- Registro informativo-narrativo, quello già usato negli esempi precedenti di questa conversazione: contesto storico/architettonico preciso, aneddoti verificabili, qualche curiosità meno nota.
- Puoi includere numeri, date, nomi propri, riferimenti culturali (film, studi, connessioni con altri luoghi/leggende).

## Esempio d'uso

**Utente:** "Siamo davanti all'Abbazia di San Galgano, fammi un podcast per i bambini."

Claude:

1. Riconosce il luogo (specifico, non ambiguo) e non chiede altro.
2. Scrive i **tre** script — avventuroso, bambini, adulti — anche se l'utente ne ha
   chiesto uno solo: il player li contiene tutti e l'utente sceglie al volo.
   Per i bambini: "Tanto, tanto tempo fa un cavaliere infilò la sua spada in una roccia..."
   Per gli adulti: "L'abbazia cistercense fu completata nel 1288 e perse il tetto nel Cinquecento..."
3. Compone la caccia al tesoro con soli elementi che esistono davvero sul posto:
   `["Una finestra rotonda", "Il cielo al posto del soffitto", "Una colonna senza cima"]`
4. Sostituisce i placeholder in `assets/template.html` e salva
   `abbazia-san-galgano-podcast.html`.
5. Comunica il percorso del file: si apre col browser e parte.

Se l'utente dicesse solo "fammi un podcast sulla Toscana", Claude chiede prima di
restringere il campo: un punto preciso produce un'audioguida utile, una regione intera no.

## Nota sull'estensione della skill

Questa skill genera contenuto (script + HTML), non nuova infrastruttura. Se in futuro l'utente chiede di espandere la skill (es. aggiungere lingue, salvataggio audio, hosting condiviso), vale comunque la regola generale: chiedere prima se c'è già evidenza d'uso ricorrente prima di costruire.
