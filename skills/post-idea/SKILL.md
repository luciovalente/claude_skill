---
name: post-idea
description: Genera idee di contenuti LinkedIn partendo dalle fonti (feed RSS + newsletter) raccolte dal server MCP feedandpost.it, e su richiesta scrive il post finale. Usa questa skill ogni volta che l'utente chiede "idee per un post", "cosa posto oggi", "post-idea", "spunti dalle mie fonti", "analizza i feed e proponi contenuti", "rassegna di oggi", "dammi 3-4 idee da postare", o in qualsiasi forma vuole trasformare le notizie/newsletter recenti in idee di post da pubblicare. Attivala anche quando parla di "contenuti dalla rassegna", "cosa scrivo su LinkedIn oggi", o vuole scegliere tra più spunti giornalieri.
---

# post-idea

Trasforma la rassegna quotidiana raccolta da **feedandpost.it** in **3-4 idee di post LinkedIn**
pronte da scegliere e, una volta scelta un'idea, nel **post finale**.

Questa skill fa **selezione editoriale + confezionamento delle idee**. La scrittura vera e
propria è delegata a una skill di tone of voice separata (vedi *Dipendenza opzionale*): la
divisione del lavoro è voluta, perché il criterio con cui si sceglie *cosa* dire cambia molto
meno spesso di *come* lo si dice.

## Prerequisiti

### 1. Il connettore MCP feedandpost.it (obbligatorio)

Servono i tool MCP esposti da [feedandpost.it](https://feedandpost.it):
`list_sources`, `list_new_items(since, source_type)`, `get_item_content(item_id)`,
`search_items(query, days)`.

Il servizio aggrega feed RSS e newsletter via email in una rassegna già normalizzata e
isolata per utente. Va aggiunto in Claude come connettore remoto, endpoint
`https://feedandpost.it/mcp`.

Se questi tool non sono disponibili nella sessione, **dillo subito all'utente** e fermati:
il connettore non è collegato. Non inventare contenuti — senza fonti reali questa skill non
ha materia prima, e delle idee di post basate su notizie immaginarie sono peggio di nessuna
idea.

### 2. Il profilo editoriale (consigliato)

La qualità del triage dipende da quanto la skill sa dell'utente. Se non hai già questo
contesto in sessione, chiedilo una volta e riusalo:

- **Temi** su cui l'utente ha qualcosa da dire (es. leadership, digitalizzazione, AI applicata,
  gestione delle persone, ERP).
- **Audience** a cui parla (es. imprenditori e manager di PMI).
- **Esperienza** da cui trae credibilità (settore, ruolo, aziende, anni sul campo).

Senza questi tre elementi le idee escono generiche: sono il filtro che distingue "notizia
interessante" da "notizia su cui *questa persona* può dire qualcosa che gli altri non direbbero".

### Dipendenza opzionale: una skill di tone of voice

Se nella sessione esiste una skill che descrive il tono di voce dell'utente, questa skill la
richiama allo Step 4 e **non** duplica le regole di stile: quella skill resta l'unica fonte di
verità sul come si scrive.

Se non esiste, scrivi comunque il post, ma prima chiedi all'utente due o tre riferimenti
concreti (un paio di suoi post precedenti, oppure: prima o terza persona, lunghezza tipica,
quanto è diretto o ironico). Un post nel tono sbagliato è inutilizzabile anche quando la tesi
è giusta.

## Flusso di lavoro

### 1. Raccogli la rassegna recente

- Calcola un timestamp ISO 8601 per le **ultime 48 ore** (o dall'ultima volta che l'utente ha
  postato, se lo indica) e chiama `list_new_items(since=<ISO>)`.
- Se l'utente chiede un taglio tematico specifico ("qualcosa sull'AI", "sul management"), usa
  anche `search_items(query, days)`.
- Se utile per contesto, `list_sources` dice quali fonti sono attive e quanto sono fresche.

Le anteprime bastano per il triage; il testo completo si recupera solo per i candidati forti.

### 2. Triage: dai molti item a pochi candidati forti

Scorri gli item e tieni i **6-10 più promettenti**. Poi, sui migliori, chiama
`get_item_content(item_id)` per leggere il full-text prima di proporli — un'idea si costruisce
sul contenuto vero, non sul titolo.

**Cosa rende un item interessante:**

- Tocca i temi del profilo editoriale.
- Offre un **angolo di opinione** o controcorrente, non solo cronaca. L'utente non "riporta le
  notizie": le usa come pretesto per una tesi, una lezione, una provocazione.
- Ha un **aggancio con la sua esperienza** che gli permette di dire qualcosa che solo lui direbbe.
- Genera **dibattito** o fa cambiare prospettiva. Meglio un contenuto divisivo e ragionato che
  un'ovvietà.

**Cosa scartare:** cronaca pura senza spunto, argomenti saturi già detti da tutti, pezzi troppo
di nicchia tecnica senza lezione trasferibile, e item da cui non emerge una tesi difendibile.

### 3. Proponi 3-4 idee (questo è l'output principale)

Presenta **almeno 3-4 idee**, ognuna con questo formato compatto e scansionabile:

```
## Idea N — <angolo/tesi in una riga>
**Hook:** <la prima riga del post, quella che ferma lo scroll>
**Tesi:** <cosa sostiene l'utente, in 1-2 frasi>
**Perché ora / perché lui:** <cosa la rende attuale e perché è credibile detta da lui>
**Fonte:** <nome fonte> — <titolo item> (item_id: <id>, <url se presente>)
```

Chiudi chiedendo **quale (o quali) svolgere**. Le idee devono essere diverse tra loro per
angolo e tono: non 4 varianti della stessa cosa.

### 4. Scrivi il post finale (solo l'idea scelta)

Quando l'utente sceglie, **richiama la skill di tone of voice** per scrivere il post. Passale
la tesi, l'hook e il materiale rilevante dell'item (che hai già letto con `get_item_content`).
Non riscrivere qui le regole di tono.

Se l'utente ne sceglie più di una, scrivi i post uno alla volta.

## Esempio d'uso

**Utente:** "Cosa posto oggi?"

1. `list_new_items(since="2026-08-25T09:00:00Z")` → 47 item nelle ultime 48 ore.
2. Triage → 8 candidati. `get_item_content` sui 4 migliori.
3. Output:

```
## Idea 1 — L'AI non sostituisce i junior, sostituisce il modo in cui li formavamo
**Hook:** Il primo lavoro che l'AI ha davvero preso non è quello del senior. È il tirocinio.
**Tesi:** I compiti ripetitivi che davamo ai junior erano il loro percorso di apprendimento.
         Automatizzarli senza sostituirli con altro produce una generazione senza palestra.
**Perché ora / perché lui:** Il report cita il calo di assunzioni entry-level nel tech; chi
         gestisce team lo sta vedendo adesso e nessuno collega le due cose.
**Fonte:** The Pragmatic Engineer — "Entry-level hiring in 2026" (item_id: itm_8812)
```

...più le idee 2, 3 e 4 con angoli diversi. Poi: *"Quale svolgo?"*

L'utente sceglie la 1 → la skill richiama il tone of voice e consegna il post finito.

## Note operative

- **Lingua:** italiano. **Piattaforma:** LinkedIn.
- **Cita la fonte** internamente (item_id/URL) così l'utente può verificare, ma il post finale
  è un contenuto originale suo, non un riassunto dell'articolo: la notizia è il trampolino,
  la tesi è sua.
- **Evita di riproporre** idee/item già trasformati in post nei giorni precedenti, se l'utente
  te lo segnala o se emerge dal contesto.
- **Paywall/troncati:** alcune newsletter a pagamento arrivano troncate. Se un item è
  chiaramente incompleto, usalo solo se il frammento basta a reggere una tesi, altrimenti
  scartalo.
- Se in 48 ore c'è poco materiale forte, dillo con onestà e proponi meno idee ma buone, oppure
  allarga la finestra temporale.
