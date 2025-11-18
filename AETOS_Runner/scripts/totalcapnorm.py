import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch
from io import StringIO
import matplotlib.ticker as mtick
import os
import sys

plt.rcParams['hatch.linewidth'] = 0.40

# ---------------------------
if len(sys.argv) < 2:
    print("Usage: python script.py results/<file.csv> [TAG]")
    sys.exit(1)

data_file = sys.argv[1]
tag = sys.argv[2] if len(sys.argv) > 2 else "SCENARIO"

# ensure output folder exists
os.makedirs("visualisation", exist_ok=True)
base = os.path.basename(data_file).replace(".csv", "")
out_prefix = os.path.join("visualisation/TechnologyShareInstalledCapacity", base)

years_to_include = [2021, 2030, 2050]
parameter = "TotalCapacityAnnual"
countries_per_page_eu = 15
countries_per_page_africa = 16
excluded_countries = ["RS","RU","TR","UA","AL","BY","MD","MK","BA","ME","IL","GE","SA","JO"]
exclude_suffixes = ["00I00", "00X00", "00E00", "00D00", "00T00", "PI0", "STOP", "BATTN1", "BATTH1", "HYDSPH1", "HYDSPN1"]
# ---------------------------

prefix_color_map = {
    "COCCS": (89, 89, 89), "NGCCS":(86, 108, 140), "BMCCS":(172, 199, 119),
    "CO": (89, 89, 89), "NG": (86, 108, 140), "BF": (100, 180, 100), "DG": (129, 149, 177),
    "RG": (170, 183, 202), "DS": (183, 66, 63), "HF": (121, 43, 41), "BM": (172, 199, 119),
    "WS": (150, 75, 0), "WION": (143, 119, 173), "WIOF": (112, 48, 160), "SOU": (230, 175, 0),
    "SOSTH": (234, 67, 0), "GO": (192, 80, 77), "HYDRP": (0, 176, 240), "HYDMP": (0, 139, 188),
    "NU": (186, 28, 175), "TID": (0, 100, 150), "OCWV": (0, 100, 150), "HYDSP": (31, 80, 153),
    "LF": (209, 58, 54), "LI": (123, 96, 83), "HYDM": (0, 176, 240), "SOU1": (230, 175, 0),
    "SOC1": (234, 67, 0), "WI": (143, 119, 173)
}

techname_map = {
    "COCCS": "Coal CCS", "NGCCS": "Natural Gas CCS", "BMCCS": "Biomass CCS",
    "CO": "Coal", "NG": "Natural Gas", "BF": "Biofuel", "DG": "Derived Gas",
    "RG": "Refined Gas", "DS": "Diesel", "HF": "HFO", "BM": "Biomass",
    "WS": "Waste", "WION": "Wind Onshore", "WIOF": "Wind Offshore", "SOU": "Solar PV",
    "SOSTH": "CSP", "GO": "Geothermal", "HYDRP": "Hydro ROR", "HYDMP": "Hydro Dam",
    "NU": "Nuclear", "TID": "Tidal", "OCWV": "Ocean Wave", "HYDSP": "Pumped Hydro",
    "LF": "LFO", "LI": "Lignite", "HYDM": "Hydro", "SOU1": "Solar PV",
    "SOC1": "CSP", "WI": "Wind"
}

country_name_map = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus",
    "CZ": "Czechia", "DE": "Germany", "DK": "Denmark", "EE": "Estonia", "GR": "Greece",
    "ES": "Spain", "FI": "Finland", "FR": "France", "HR": "Croatia", "HU": "Hungary",
    "IE": "Ireland", "IS": "Iceland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg",
    "LV": "Latvia", "MT": "Malta", "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
    "PT": "Portugal", "RO": "Romania", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia",
    "UK": "United Kingdom",

    "DZ": "Algeria", "AO": "Angola", "BJ": "Benin", "BW": "Botswana",
    "BF": "Burkina Faso", "BI": "Burundi", "CM": "Cameroon", "CV": "Cape Verde",
    "CF": "CAR", "TD": "Chad", "CG": "Congo", "CD": "DR Congo",
    "DJ": "Djibouti", "EG": "Egypt", "GQ": "Equatorial Guinea", "ER": "Eritrea", "SZ": "Eswatini",
    "ET": "Ethiopia", "GA": "Gabon", "GM": "Gambia", "GH": "Ghana", "GN": "Guinea",
    "GW": "Guinea-Bissau", "CI": "Ivory Coast", "KE": "Kenya", "LS": "Lesotho", "LR": "Liberia",
    "LY": "Libya", "MW": "Malawi", "ML": "Mali", "MR": "Mauritania", "MA": "Morocco",
    "MZ": "Mozambique", "NA": "Namibia", "NE": "Niger", "NG": "Nigeria", "RW": "Rwanda",
    "SN": "Senegal", "SL": "Sierra Leone", "SO": "Somalia", "ZA": "South Africa",
    "SS": "South Sudan", "SD": "Sudan", "TZ": "Tanzania", "TG": "Togo", "TN": "Tunisia",
    "UG": "Uganda", "ZM": "Zambia", "ZW": "Zimbabwe"
}

def process_file(data_file, out_prefix, tag):
    # Load and clean
    with open(data_file, "r") as f:
        lines = [line for line in f if line.startswith(parameter + ",")]
    df = pd.read_csv(StringIO("".join(lines)), header=None)
    df = df.dropna(axis=1, how='all')
    df.columns = ["Parameter", "Region", "Technology"] + [f"Y{2021+i}" for i in range(len(df.columns) - 3)]
    df = df.melt(id_vars=["Parameter", "Region", "Technology"], var_name="Year", value_name="Value")
    df["Year"] = df["Year"].str.extract(r'(\d+)').astype(int)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["Country"] = df["Technology"].str.extract(r"^([A-Z]{2})")
    df = df[~df["Country"].isin(excluded_countries)]
    pattern = "(?:" + "|".join(exclude_suffixes) + r")$"
    df = df[~df["Technology"].str.contains(pattern, regex=True)]
    df = df[~df["Technology"].str.contains(r"^..EL.*PH1$", regex=True)]
    df["TechBase"] = df["Technology"].str.replace(r"(H1|N1|H0|N0)$", "", regex=True)

    def get_prefix(tech):
        for p in sorted(prefix_color_map, key=len, reverse=True):
            if p in tech:
                return p
        return None

    df["TechPrefix"] = df["TechBase"].apply(get_prefix)
    df = df[df["TechPrefix"].notna()]
    df["TechName"] = df["TechPrefix"].map(techname_map)
    df["Color"] = df["TechPrefix"].map(lambda x: [v / 255 for v in prefix_color_map.get(x)])
    df = df[df["Year"].isin(years_to_include)]

    # Grouped
    grouped = df.groupby(["Country", "Year", "TechName", "TechPrefix"]).agg({"Value": "sum"}).reset_index()
    grouped["Total"] = grouped.groupby(["Country", "Year"])["Value"].transform("sum")
    grouped["Share"] = grouped["Value"] / grouped["Total"]

    europe_codes = [c for c in country_name_map if c in [
        "AT","BE","BG","CH","CY","CZ","DE","DK","EE","GR","ES","FI","FR","HR",
        "HU","IE","IT","LT","LU","LV","MT","NL","NO","PL","PT","RO","SE","SI","SK","UK"
    ]]
    africa_codes = [c for c in country_name_map if c not in europe_codes and c not in excluded_countries]

    grouped_eu = grouped[grouped["Country"].isin(europe_codes)]
    grouped_af = grouped[grouped["Country"].isin(africa_codes)]

    tech_order_eu = grouped_eu.groupby("TechName")["Share"].mean().sort_values(ascending=False).index.tolist()
    tech_order_af = grouped_af.groupby("TechName")["Share"].mean().sort_values(ascending=False).index.tolist()

    prefix_by_tech = grouped.drop_duplicates("TechName").set_index("TechName")["TechPrefix"]
    color_map_eu = {tech: [v / 255 for v in prefix_color_map[prefix_by_tech[tech]]] for tech in tech_order_eu}
    color_map_af = {tech: [v / 255 for v in prefix_color_map[prefix_by_tech[tech]]] for tech in tech_order_af}

    pivot_df = grouped.pivot_table(index=["Country", "Year"], columns="TechName", values="Share", fill_value=0)

    def plot_region(region_name, country_codes, pdf, countries_per_page, tech_order, color_map, legend_cols):
        selected = [c for c in country_codes if c in pivot_df.index.get_level_values(0)]
        n_pages = int(np.ceil(len(selected) / countries_per_page))
        bar_width, gap_within, gap_between = 0.8, 1, 0.5

        for page in range(n_pages):
            subset = selected[page * countries_per_page : (page + 1) * countries_per_page]
            fig, ax = plt.subplots(figsize=(max(18, len(subset) * 1.6), 9))
            x_positions, tick_positions, tick_labels = [], [], []

            for i, country in enumerate(subset):
                for j, year in enumerate(years_to_include):
                    try:
                        row = pivot_df.loc[(country, year)]
                    except KeyError:
                        continue
                    x = i * (gap_within * len(years_to_include) + gap_between) + j * gap_within
                    bottom = 0
                    for tech in tech_order:
                        val = row.get(tech, 0)
                        if val > 0:
                            color = color_map.get(tech, [0.6, 0.6, 0.6])
                            if prefix_by_tech[tech] in ["COCCS", "NGCCS", "BMCCS"]:
                                ax.bar(x, val, bottom=bottom, width=bar_width,
                                       color=color, edgecolor="white", linewidth=0,
                                       hatch="/////", zorder=3)
                            else:
                                ax.bar(x, val, bottom=bottom, width=bar_width,
                                       color=color, edgecolor=None, zorder=3)
                            bottom += val

                    x_positions.append(x)
                    tick_positions.append(x)
                    tick_labels.append(str(year))

            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=90, fontsize=14)
            label_positions = [
                i * (gap_within * len(years_to_include) + gap_between) + (gap_within * (len(years_to_include) - 1)) / 2
                for i in range(len(subset))
            ]
            label_names = [country_name_map.get(code, code) for code in subset]
            for xpos, label in zip(label_positions, label_names):
                ax.text(xpos, -0.18, label, fontsize=14, ha='center', va='top', transform=ax.get_xaxis_transform())

            ax.set_xlim(min(x_positions) - 1, max(x_positions) + 1)
            ax.set_ylabel("Share of Total Capacity (%)", fontsize=16)
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
            ax.tick_params(axis='y', labelsize=13)

            ax.set_ylim(0, 1.0)

            ax.set_title(f"{region_name} – Technology Share in Installed Capacity (2021, 2030, 2050) – {tag}",
                         fontsize=16, pad=20)

            ax.grid(True, which="major", axis="y", linestyle="--", alpha=0.5, zorder=0)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            legend_elements = []
            for tech in tech_order:
                color = color_map.get(tech, [0.6, 0.6, 0.6])
                if prefix_by_tech[tech] in ["COCCS", "NGCCS", "BMCCS"]:
                    patch = Patch(facecolor=color, edgecolor="white", linewidth=0,
                                  hatch="/////", label=techname_map.get(prefix_by_tech[tech], tech))
                else:
                    patch = Patch(facecolor=color, label=techname_map.get(prefix_by_tech[tech], tech))
                legend_elements.append(patch)

            ax.legend(
                handles=legend_elements,
                loc='lower center',
                bbox_to_anchor=(0.5, -0.40),
                ncol=legend_cols,
                fontsize=11,
                frameon=False
            )

            plt.tight_layout(rect=[0, 0.05, 1, 0.95])

            pdf.savefig(fig, bbox_inches='tight')
            png_name = f"{out_prefix}_{region_name}_page{page+1}.png"
            fig.savefig(png_name, dpi=900, bbox_inches='tight')
            plt.close()

    out_pdf = f"{out_prefix}.pdf"
    with PdfPages(out_pdf) as pdf:
        plot_region("Europe", europe_codes, pdf, countries_per_page_eu, tech_order_eu, color_map_eu, legend_cols=11)
        plot_region("Africa", africa_codes, pdf, countries_per_page_africa, tech_order_af, color_map_af, legend_cols=8)

    print(f"✅ Visualisation successfully completed, check {out_pdf}")

# ---------------------------
process_file(data_file, out_prefix, tag)
