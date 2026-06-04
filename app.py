
import streamlit as st
import pandas as pd

st.set_page_config(page_title="EEG-ECG Drowsiness Risk App", layout="wide")

HR_THR = -10
ALPHA_THR = 50
BETA_THR = -30

st.title("EEG-ECG Drowsiness Risk Assessment App")

st.warning(
    "Educational and research prototype only. Not clinically approved and not a replacement for professional medical judgment."
)

tab1, tab2 = st.tabs(["Manual Risk Calculator", "47 Subjects Dashboard"])

with tab1:
    st.header("Manual Drowsiness Risk Calculator")
    st.write("Enter baseline and current physiological values to estimate drowsiness risk.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("Heart Rate")
        baseline_hr = st.number_input("Baseline HR (bpm)", min_value=20.0, max_value=200.0, value=72.0)
        current_hr = st.number_input("Current HR (bpm)", min_value=20.0, max_value=200.0, value=65.0)

    with c2:
        st.subheader("Alpha Power")
        baseline_alpha = st.number_input("Baseline Alpha Power", min_value=0.000001, value=1.0, format="%.6f")
        current_alpha = st.number_input("Current Alpha Power", min_value=0.000001, value=1.7, format="%.6f")

    with c3:
        st.subheader("Beta Power")
        baseline_beta = st.number_input("Baseline Beta Power", min_value=0.000001, value=1.0, format="%.6f")
        current_beta = st.number_input("Current Beta Power", min_value=0.000001, value=0.6, format="%.6f")

    if st.button("Check Drowsiness Risk", type="primary"):
        delta_hr = ((current_hr - baseline_hr) / baseline_hr) * 100
        delta_alpha = ((current_alpha - baseline_alpha) / baseline_alpha) * 100
        delta_beta = ((current_beta - baseline_beta) / baseline_beta) * 100

        hr_condition = delta_hr < HR_THR
        alpha_condition = delta_alpha > ALPHA_THR
        beta_condition = delta_beta < BETA_THR
        score = int(hr_condition) + int(alpha_condition) + int(beta_condition)

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("HR Change", f"{delta_hr:.2f}%")
        r2.metric("Alpha Change", f"{delta_alpha:.2f}%")
        r3.metric("Beta Change", f"{delta_beta:.2f}%")
        r4.metric("Drowsiness Score", f"{score}/3")

        if score == 3:
            st.error("High Risk | Alarm ACTIVE")
            st.write("All three biomarkers satisfy the alarm criteria.")
        elif score == 2:
            st.warning("Moderate Risk | Caution")
            st.write("Two biomarkers indicate possible fatigue. Continue monitoring.")
        else:
            st.success("Low Risk / Normal | Alarm NOT ACTIVE")
            st.write("The drowsiness alarm criteria are not fully satisfied.")

        table = pd.DataFrame({
            "Biomarker": ["Heart Rate", "Alpha Power", "Beta Power"],
            "Baseline": [baseline_hr, baseline_alpha, baseline_beta],
            "Current": [current_hr, current_alpha, current_beta],
            "Change (%)": [delta_hr, delta_alpha, delta_beta],
            "Rule": ["Delta HR < -10%", "Delta Alpha > +50%", "Delta Beta < -30%"],
            "Condition Met": [hr_condition, alpha_condition, beta_condition]
        })
        st.dataframe(table, use_container_width=True)
        st.bar_chart(pd.DataFrame({
            "Change (%)": [delta_hr, delta_alpha, delta_beta]
        }, index=["HR Change", "Alpha Change", "Beta Change"]))

with tab2:
    st.header("47 Subjects Dashboard")
    st.write("Optional dashboard using the Excel results file from MATLAB.")

    uploaded = st.file_uploader("Upload 47.xlsx", type=["xlsx"])

    try:
        if uploaded is not None:
            df = pd.read_excel(uploaded)
        else:
            df = pd.read_excel("47.xlsx")

        df.columns = df.columns.str.strip()

        required = [
            "ID", "Sex", "Age", "Height(cm)", "Weight(kg)", "BMI",
            "Baseline_HR", "Mean_HR", "Mean_HR_Change",
            "Mean_Alpha_Change", "Mean_Beta_Change", "Num_Alarms"
        ]

        missing = [c for c in required if c not in df.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
            st.stop()

        if "Alarm_Percentage" not in df.columns:
            max_alarm = max(df["Num_Alarms"].max(), 1)
            df["Alarm_Percentage"] = (df["Num_Alarms"] / max_alarm) * 100

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Subjects", len(df))
        s2.metric("Mean Baseline HR", f"{df['Baseline_HR'].mean():.2f} bpm")
        s3.metric("Mean HR Change", f"{df['Mean_HR_Change'].mean():.2f}%")
        s4.metric("Mean Alarms", f"{df['Num_Alarms'].mean():.2f}")

        selected = st.selectbox("Select Subject", df["ID"].tolist())
        subject = df[df["ID"] == selected].iloc[0]

        st.subheader(f"Subject {selected}")
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Baseline HR", f"{subject['Baseline_HR']:.2f}")
        a2.metric("Mean HR", f"{subject['Mean_HR']:.2f}")
        a3.metric("HR Change", f"{subject['Mean_HR_Change']:.2f}%")
        a4.metric("Num Alarms", int(subject["Num_Alarms"]))

        b1, b2, b3 = st.columns(3)
        b1.metric("Alpha Change", f"{subject['Mean_Alpha_Change']:.2f}%")
        b2.metric("Beta Change", f"{subject['Mean_Beta_Change']:.2f}%")
        b3.metric("Alarm Percentage", f"{subject['Alarm_Percentage']:.2f}%")

        t1, t2, t3, t4 = st.tabs(["Alarm Count", "Alarm Percentage", "Alpha/Beta", "Full Table"])
        with t1:
            st.bar_chart(df[["ID", "Num_Alarms"]].set_index("ID"))
        with t2:
            st.bar_chart(df[["ID", "Alarm_Percentage"]].set_index("ID"))
        with t3:
            st.bar_chart(df[["ID", "Mean_Alpha_Change", "Mean_Beta_Change"]].set_index("ID"))
        with t4:
            st.dataframe(df, use_container_width=True)

    except FileNotFoundError:
        st.error("47.xlsx not found. Please upload the Excel file.")
