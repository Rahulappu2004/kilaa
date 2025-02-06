import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Multi-File Data Analysis App")

uploaded_files = st.file_uploader("Choose one or more files", type=["xlsx", "csv"], accept_multiple_files=True)

if uploaded_files:
    @st.cache_data
    def process_data(files):
        all_data = []

        for file in files:
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file, engine='openpyxl')
            else:
                df = pd.read_csv(file)

            required_columns = {'Code', 'LBType', 'Tot', 'TotExp', 'Sector', 'District'}
            if not required_columns.issubset(df.columns):
                st.error(f"Invalid format in {file.name}. Missing: {required_columns - set(df.columns)}")
                return None
            
            # Remove rows with null values in 'Code'
            df = df.dropna(subset=['Code'])
            
            # Add 'Difference' column
            df['Difference'] = df['Tot'] - df['TotExp']
            
            all_data.append(df)

        return pd.concat(all_data, ignore_index=True)

    data = process_data(uploaded_files)

    if data is not None:
        st.sidebar.header("Choose Analysis Options")
        analysis_options = st.sidebar.multiselect(
            "Select the analyses you want to perform:",
            [
                "Filter Data by LBType",
                "Find Funded & Non-Funded Projects",
                "Compare Total Expense & Total Income",
                "District-wise Expense vs Income",
                "Find Projects Where Funds Were Not Used"
            ]
        )

        # 1️⃣ Filter Data by LBType
        if "Filter Data by LBType" in analysis_options:
            st.subheader("Filter Data by LBType")
            lb_types = data['LBType'].unique()
            selected_lbtype = st.multiselect("Select LBType(s)", list(lb_types), default=[])
            
            if selected_lbtype:
                filtered_data = data[data['LBType'].isin(selected_lbtype)]
                st.dataframe(filtered_data)
            else:
                st.dataframe(data)

        # 2️⃣ Find Funded & Non-Funded Projects
        if "Find Funded & Non-Funded Projects" in analysis_options:
            st.subheader("Funded vs Non-Funded Projects")
            data['Funding Status'] = np.where(data['Tot'] == 0, 'Not Funded', 'Funded')
            
            funded_counts = data['Funding Status'].value_counts()
            st.bar_chart(funded_counts)
            st.dataframe(data[['Code', 'LBType', 'Sector', 'District', 'Tot', 'Funding Status']])

        # 3️⃣ Compare Total Expense & Total Income
        if "Compare Total Expense & Total Income" in analysis_options:
            st.subheader("Total Expense vs Total Income")
            total_expense = data['TotExp'].sum()
            total_income = data['Tot'].sum()

            fig, ax = plt.subplots()
            labels = ['Total Expense', 'Total Income']
            values = [total_expense, total_income]
            ax.bar(labels, values, color=['#ff9999', '#66b3ff'])
            ax.set_ylabel('Amount')

            for i, v in enumerate(values):
                ax.text(i, v + 0.02 * max(values), f'{v:,.0f}', ha='center', fontsize=10, fontweight='bold')

            st.pyplot(fig)

        # 4️⃣ District-wise Expense vs Income
        if "District-wise Expense vs Income" in analysis_options:
            st.subheader("District-wise Comparison of Expense & Income")
            district_data = data.groupby('District')[['TotExp', 'Tot']].sum().reset_index()

            fig, ax = plt.subplots(figsize=(10, 5))
            x = np.arange(len(district_data['District']))
            width = 0.35

            ax.bar(x - width/2, district_data['TotExp'], width, label='Total Expense', color='#c94c4c')
            ax.bar(x + width/2, district_data['Tot'], width, label='Total Income', color='#66b3ff')

            ax.set_xlabel('District')
            ax.set_ylabel('Amount')
            ax.set_title('District-wise Expense vs Income')
            ax.set_xticks(x)
            ax.set_xticklabels(district_data['District'], rotation=45, ha='right')
            ax.legend()

            st.pyplot(fig)

        # 5️⃣ Find Projects Where Funds Were Not Used
        if "Find Projects Where Funds Were Not Used" in analysis_options:
            st.subheader("Projects Where Funds Were Not Used")
            unused_funds = data[(data['TotExp'] == 0) & (data['Tot'] > 0)]
            st.dataframe(unused_funds)
