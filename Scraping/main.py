import requests
from bs4 import BeautifulSoup
import pandas as pd
import calendar
import matplotlib.pyplot as plt

def fetch_only_funds_inflow_outflow(pmr_id, year, month):
    import requests
    from bs4 import BeautifulSoup

    url = "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doPmr=yes"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": url,
        "Origin": "https://www.sebi.gov.in"
    }
    payload = {
        "pmrId": pmr_id,
        "year": str(year),
        "month": str(month),
        "action": "search"
    }

    with requests.Session() as session:
        session.headers.update(headers)
        session.get(url)
        response = session.post(url, data=payload)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        all_elements = soup.find_all(['strong', 'b', 'table'])
        current_title = "Untitled Section"
        table_count = 0

        for el in all_elements:
            if el.name in ['strong', 'b']:
                title_text = el.get_text(strip=True)
                if title_text:
                    current_title = title_text
            elif el.name == 'table' and 'statistics-table' in el.get('class', []):
                table_count += 1
                full_title = f"{table_count:02d} - {current_title}"
                # print("full_title : ",full_title)
                if full_title.strip() == "07 - C.Funds Inflow/ Outflow":
                    rows = []
                    for row in el.find_all("tr"):
                        cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
                        if cols:
                            rows.append(cols)
                    return {full_title: rows}

    return {}  # If not found





def extract_funds_inflow_outflow_table(tables_dict):
    target_key = None
    for key in tables_dict.keys():
        if "07 - C.Funds Inflow/ Outflow" in key:
            target_key = key
            break
    if target_key is None:
        return None
    data = tables_dict[target_key]
    max_cols = max(len(row) for row in data)
    header_row_index = 0
    for i, row in enumerate(data):
        if len(row) == max_cols:
            header_row_index = i
            break
    columns = data[header_row_index]
    df = pd.DataFrame(data[header_row_index+1:], columns=columns)
    return df


def fetch_monthly_funds_data(pmr_id, months_list):
    all_data = {}
    for year, month in months_list:
        month_name = calendar.month_name[month]
        month_year = f"{month_name} {year}"
        print(f"Fetching data for {month_year}...")
        tables = fetch_only_funds_inflow_outflow(pmr_id, year, month)
        df = extract_funds_inflow_outflow_table(tables)
        if df is not None:
            all_data[month_year] = df
        else:
            print(f"Warning: '07 - C.Funds Inflow/ Outflow' table not found for {month_year}")
    print("Fetching complete.")
    return all_data


def prepare_performance_data(monthly_funds_data):
    months = []
    monthly_net_flow = []
    cumulative_net_flow = []

    for month_year in sorted(monthly_funds_data.keys(), key=lambda x: pd.to_datetime(x, format='%B %Y')):
        df = monthly_funds_data[month_year]
        df.columns = [col.strip() for col in df.columns]
        print(f"Processing {month_year}...")
        print("Columns:", df.columns.tolist())
        
        total_row = df[df[''].str.lower() == 'total']
        if total_row.empty:
            print(f"Warning: Total row not found for {month_year}, skipping.")
            continue

        # Look for columns containing the needed text ignoring FY end date variance
        monthly_col = None
        cumulative_col = None
        for col in df.columns:
            if "Net Inflow (+ve)/ Outflow (-ve) during the month" in col:
                monthly_col = col
            if "Net Inflow (+ve)/ Outflow (-ve) during the FY since April 01 to" in col:
                cumulative_col = col

        if not monthly_col or not cumulative_col:
            print(f"Warning: Required columns not found for {month_year}, skipping.")
            continue

        try:
            monthly_net = float(total_row.iloc[0][monthly_col].replace(',', ''))
            cumulative_net = float(total_row.iloc[0][cumulative_col].replace(',', ''))
        except Exception as e:
            print(f"Error parsing numbers for {month_year}: {e}, skipping.")
            continue
        
        print(f"Extracted values - Monthly: {monthly_net}, Cumulative: {cumulative_net}")

        months.append(month_year)
        monthly_net_flow.append(monthly_net)
        cumulative_net_flow.append(cumulative_net)

    print("Final extracted months:", months)
    return months, monthly_net_flow, cumulative_net_flow



def plot_performance_chart(months, monthly_net_flow, cumulative_net_flow):
    plt.figure(figsize=(12,6))
    plt.plot(months, monthly_net_flow, marker='o', label='Monthly Net Inflow/Outflow')
    plt.plot(months, cumulative_net_flow, marker='s', label='Cumulative Net Inflow/Outflow FY')
    plt.xticks(rotation=45)
    plt.title("Funds Inflow/Outflow Performance (Apr 2024 - Mar 2025)")
    plt.xlabel("Month")
    plt.ylabel("Amount (INR crores)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    pmr_id = "INP000008464@@INP000008464@@1729 ADVISORS LLP"
    all_months = [(2024, m) for m in range(4, 13)] + [(2025, m) for m in range(1, 4)]
    monthly_funds_data = fetch_monthly_funds_data(pmr_id, all_months)
    # print("monthly_funds_data : ",monthly_funds_data)

    months, monthly_net_flow, cumulative_net_flow = prepare_performance_data(monthly_funds_data)
    print("months, monthly_net_flow, cumulative_net_flow : ",months, monthly_net_flow, cumulative_net_flow )
    plot_performance_chart(months, monthly_net_flow, cumulative_net_flow)
