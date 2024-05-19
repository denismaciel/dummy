import streamlit as st
import pandas as pd
import altair as alt
from dataclasses import dataclass


X_SCALES = {
    "year": alt.Scale(domain=[1990, 2030], type='linear'),
    "horsepower": alt.Scale(domain=[50, 1000], type='linear'),
    "kilometerstand_float": alt.Scale(domain=[0, 300000], type='linear'),
}


@dataclass
class InputData:
    df: pd.DataFrame
    marke_modell_options: dict[str, tuple[str, str, int]]


@st.cache_data
def load_data():
    df = pd.read_parquet("./data/output_transformed.parquet")
    return df


@st.cache_data
def load_opts(df):
    xs = (
        df.groupby(['marke', 'modell'])
        .size()
        .reset_index(name='count')
        .itertuples(index=False)
    )
    opts = {f'{x[0]} - {x[1]} ({x[2]})': tuple(x) for x in xs}
    return opts


df = load_data()
opts = load_opts(df)

st.sidebar.header("Filter options")

selected = st.sidebar.multiselect(
    "Select Marke and Modell",
    opts,
    default=list(opts)[0],
)

print(selected)

if selected:
    filtered_data = df[
        df[['marke', 'modell']]
        .apply(tuple, axis=1)
        .isin([(opts[s][0], opts[s][1]) for s in selected])
    ]
else:
    filtered_data = None


x_axis = st.sidebar.selectbox(
    "Select X axis", ["year", "horsepower", "kilometerstand_float"]
)


st.title("Car Scatter Plot")
st.write(f"Visualizing {x_axis} against Price with Color Coded by (Marke, Modell)")


scatter_plot = (
    alt.Chart(filtered_data)
    .mark_circle(size=60)
    .encode(
        x=alt.X(x_axis, scale=X_SCALES[x_axis]),
        y='price_float',
        color='marke:N',
        tooltip=["marke", "modell", "year", "horsepower", "price_float"],
    )
    .interactive()
)

st.altair_chart(scatter_plot, use_container_width=True)
