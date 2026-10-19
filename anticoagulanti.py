import streamlit as st

st.set_page_config(
    page_title="Calcolatore Sospensione Farmaci",
    layout="centered",
)

st.title("💊 Calcolatore Tempi di Sospensione Farmaci")
st.write(
    "Seleziona la categoria di farmaco e inserisci i dati per determinare l'intervallo"
    " di sospensione raccomandato prima di una procedura o intervento."
)

# 1. Selezione della Categoria di Farmaci
st.header("1. Categoria e Farmaco")

categoria = st.selectbox(
    "Seleziona Categoria Farmaco", ["Anticoagulanti", "Antiaggreganti"]
)

col1, col2 = st.columns(2)

if categoria == "Anticoagulanti":
  with col1:
    farmaco = st.selectbox(
        "Seleziona il Farmaco / Classe",
        [
            "Dabigatran (Pradaxa)",
            "Apixaban (Eliquis) / Rivaroxaban (Xarelto) / Edoxaban (Lixiana)",
            "Eparina a Basso Peso Molecolare (EBPM / Enoxaparina)",
            "Warfarin / Acenocumarol (Sintrom)",
        ],
    )
    eta = st.number_input("Età (anni)", min_value=18, max_value=120, value=65)
    peso = st.number_input(
        "Peso (kg)", min_value=30.0, max_value=200.0, value=70.0
    )

  with col2:
    sesso = st.radio("Sesso", ["Maschio", "Femmina"])
    creatinina = st.number_input(
        "Creatininemia sierica (mg/dL)",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1,
    )

    if "Eparina" in farmaco:
      dosaggio_ebpm = st.selectbox(
          "Dosaggio EBPM",
          ["Basso dosaggio (50UI/kg/die)", "Alto dosaggio (100UI/kg/die)"],
      )

  # Calcolo Clearance Creatinina (Cockcroft-Gault)
  def calcola_crcl(eta, peso, creatinina, sesso):
    if creatinina == 0:
      return 0.0
    crcl = ((140 - eta) * peso) / (72 * creatinina)
    if sesso == "Femmina":
      crcl *= 0.85
    return round(crcl, 1)

  crcl_stimata = calcola_crcl(eta, peso, creatinina, sesso)

else:
  # Categoria Antiaggreganti
  with col1:
    farmaco = st.selectbox(
        "Seleziona Antiaggregante",
        [
            "Aspirina / Cardioaspirina (ASA)",
            "Clopidogrel (Plavix)",
            "Prasugrel (Efient)",
            "Ticagrelor (Brilique)",
            "Ticlopidina",
        ],
    )

  with col2:
    if "Aspirina" in farmaco:
      dosaggio_asa = st.selectbox(
          "Seleziona Dosaggio Aspirina",
          ["100 mg (Basso dosaggio)", "300 mg (Alto dosaggio)"],
      )


# 2. Logica di Sospensione
def determina_sospensione(categoria, farmaco, **kwargs):
  if categoria == "Anticoagulanti":
    crcl = kwargs.get("crcl")

    # Warfarin / Sintrom
    if "Warfarin" in farmaco:
      return (
          "Sospendere 3-5 giorni prima (verificando che l'INR sia < 1.5 prima"
          " dell'intervento/blocco)."
      )

    # EBPM
    if "Eparina" in farmaco:
      dosaggio = kwargs.get("dosaggio_ebpm")
      if crcl >= 30:
        return (
            "12 ore prima"
            if dosaggio == "Basso dosaggio (50UI/kg/die)"
            else "24 ore prima"
        )
      else:
        return (
            "24 ore prima"
            if dosaggio == "Basso dosaggio (50UI/kg/die)"
            else "48 ore prima"
        )

    # Dabigatran
    if "Dabigatran" in farmaco:
      if crcl >= 80:
        return "48 ore prima"
      elif 50 <= crcl < 79:
        return "72 ore prima"
      elif 30 <= crcl < 49:
        return "96 ore prima"
      else:
        return (
            "Controindicato eseguire procedure invasive per filtrato"
            " glomerulare troppo basso"
        )

    # Apixaban / Rivaroxaban / Edoxaban
    if (
        "Apixaban" in farmaco
        or "Rivaroxaban" in farmaco
        or "Edoxaban" in farmaco
    ):
      if crcl >= 15:
        return "48 ore prima"
      else:
        return (
            "Controindicato eseguire procedure invasive per filtrato"
            " glomerulare troppo basso"
        )

  else:
    # Logica Antiaggreganti
    if "Aspirina" in farmaco:
      dosaggio_asa = kwargs.get("dosaggio_asa")
      if dosaggio_asa == "100 mg (Basso dosaggio)":
        return (
            "**Non va sospesa** (da proseguire, eccetto in caso di specifiche"
            " eccezioni chirurgiche/anestesiologiche o procedure ad altissimo"
            " rischio emorragico neuroassiale)."
        )
      else:
        return "**Sospendere 7 giorni prima** dell'intervento o procedura."

    elif "Clopidogrel" in farmaco:
      return "Sospendere 5 giorni prima dell'intervento o procedura."
    elif "Prasugrel" in farmaco:
      return "Sospendere 7 giorni prima dell'intervento o procedura."
    elif "Ticagrelor" in farmaco:
      return "Sospendere 3-5 giorni prima dell'intervento o procedura."
    elif "Ticlopidina" in farmaco:
      return "Sospendere 10-14 giorni prima dell'intervento o procedura."

  return "Valutare secondo linee guida specifiche."


# 3. Sezione Risultati
st.markdown("---")
st.header("2. Risultati dell'Analisi")

if st.button("Calcola Tempi di Sospensione", type="primary"):
  if categoria == "Anticoagulanti":
    st.info(
        f"📊 **Clearance della Creatinina stimata (Cockcroft-Gault):**"
        f" **{crcl_stimata} mL/min**"
    )
    kwargs_pass = {"crcl": crcl_stimata}
    if "Eparina" in farmaco:
      kwargs_pass["dosaggio_ebpm"] = dosaggio_ebpm
  else:
    kwargs_pass = {}
    if "Aspirina" in farmaco:
      kwargs_pass["dosaggio_asa"] = dosaggio_asa

  risultato_sospensione = determina_sospensione(
      categoria, farmaco, **kwargs_pass
  )

  st.success(
      f"⏱️ **Intervallo di sospensione raccomandato prima della procedura /"
      f" blocco:**\n\n {risultato_sospensione}"
  )

  st.warning(
      "⚠️ **Nota di responsabilità:** Questo strumento integra criteri"
      " avanzati, ma non sostituisce il giudizio clinico specialistico e le"
      " linee guida ufficiali vigenti."
  )
