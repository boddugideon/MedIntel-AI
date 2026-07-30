import streamlit as st


def patient_information():

    st.subheader("👤 Patient Information")

    col1, col2 = st.columns(2)

    with col1:
        patient_name = st.text_input("Patient Name")

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=25
        )

        gender = st.selectbox(
            "Gender",
            [
                "Male",
                "Female",
                "Other"
            ]
        )

    with col2:

        phone = st.text_input("Phone Number")

        report_type = st.selectbox(
            "Report Type",
            [
                "Blood Test",
                "MRI",
                "Prescription",
                "X-Ray Report"
            ]
        )

        report_date = st.date_input("Report Date")

    return {
        "Patient Name": patient_name,
        "Age": age,
        "Gender": gender,
        "Phone": phone,
        "Report Type": report_type,
        "Report Date": report_date
    }