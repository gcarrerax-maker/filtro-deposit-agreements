import io
import re
import unicodedata

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Filtro Deposit Agreements", page_icon="🏨", layout="wide")

DATA_DIR = "data"


def normalize(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@st.cache_data
def load_reference_lists():
    ygg = pd.read_csv(f"{DATA_DIR}/hotel_list_ygg.csv")
    omn = pd.read_csv(f"{DATA_DIR}/hotel_list_omn.csv")
    ygg_names = {normalize(n) for n in ygg["Hotel"]}
    omn_names = {normalize(n) for n in omn["Hotel"]}
    omn_cnpjs = {re.sub(r"\D", "", str(c)) for c in omn["CNPJ"].dropna()}
    return ygg_names, omn_names, omn_cnpjs


YGG_NAMES, OMN_NAMES, OMN_CNPJS = load_reference_lists()

CREATION_SIGNATURE = {"Item", "Hotel Name"}
CHECKIN_SIGNATURE = {"Localizador", "Hotel"}


def detect_base(df: pd.DataFrame) -> str:
    cols = set(df.columns)
    if CREATION_SIGNATURE.issubset(cols):
        return "creation"
    if CHECKIN_SIGNATURE.issubset(cols):
        return "checkin"
    return "unknown"


def filter_creation(df: pd.DataFrame) -> pd.DataFrame:
    mask = df["Hotel Name"].apply(lambda v: normalize(v) in YGG_NAMES)
    return df[mask]


def filter_checkin(df: pd.DataFrame) -> pd.DataFrame:
    name_mask = df["Hotel"].apply(lambda v: normalize(v) in OMN_NAMES)
    cnpj_mask = df["CNPJ"].apply(lambda v: re.sub(r"\D", "", str(v)) in OMN_CNPJS if pd.notna(v) else False)
    return df[name_mask | cnpj_mask]


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtrado")
    return buffer.getvalue()


st.title("🏨 Filtro Deposit Agreements")
st.write(
    "Suba o extrato de **CREATION** (Booking Report) ou **CHECK IN** (Export) e "
    "receba de volta só as reservas cujo hotel está na lista de referência "
    "(YGG para CREATION, OMN para CHECK IN)."
)

uploaded_file = st.file_uploader("Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as exc:
        st.error(f"Não consegui ler o arquivo: {exc}")
        st.stop()

    base = detect_base(df)

    if base == "unknown":
        st.error(
            "Não reconheci o formato do arquivo. Esperava as colunas de CREATION "
            "('Item', 'Hotel Name', ...) ou de CHECK IN ('Localizador', 'Hotel', ...)."
        )
        st.stop()

    if base == "creation":
        st.success(f"Detectado: base **CREATION** · {len(df)} linhas · filtrando pela lista YGG.")
        filtered = filter_creation(df)
    else:
        st.success(f"Detectado: base **CHECK IN** · {len(df)} linhas · filtrando pela lista OMN.")
        filtered = filter_checkin(df)

    st.metric("Reservas elegíveis para prebuy", f"{len(filtered)} de {len(df)}")
    st.dataframe(filtered, use_container_width=True)

    file_label = "creation" if base == "creation" else "checkin"
    st.download_button(
        "⬇️ Baixar Excel filtrado",
        data=to_excel_bytes(filtered),
        file_name=f"filtro_prebuy_{file_label}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.subheader("📋 Copiar dados (sem baixar)")
    st.caption("Passe o mouse no canto superior direito do quadro abaixo e clique no ícone de copiar.")
    st.code(filtered.to_csv(sep="\t", index=False), language=None)
