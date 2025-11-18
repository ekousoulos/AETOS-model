import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch
import matplotlib.ticker as mtick
import re
from io import StringIO
import sys, os

plt.rcParams['hatch.linewidth'] = 0.40

# ---------------------------------
if len(sys.argv) < 2:
    print("Usage: python script.py results/<file.csv> [TAG]")
    sys.exit(1)

data_file = sys.argv[1]
tag = sys.argv[2] if len(sys.argv) > 2 else "SCENARIO"

# make sure output folder exists
os.makedirs("visualisation/TechnologyShareTotalActivity", exist_ok=True)
base = os.path.basename(data_file).replace(".csv", "")
out_prefix = os.path.join("visualisation/TechnologyShareTotalActivity", base)

parameter = "TotalTechnologyAnnualActivity"
years_to_include = [2021, 2030, 2050]
countries_per_page_eu = 15
countries_per_page_africa = 16
excluded_countries = ["RS","RU","TR","UA","AL","BY","MD","MK","BA","ME","IL","GE","SA","JO"]
exclude_suffixes = ["00I00", "00X00", "00E00", "00D00", "00T00", "PI0", "STOP",
                    "BATTN1", "BATTH1", "HYDSPH1", "HYDSPN1"]
# ---------------------------------

prefix_color_map = {
    "COCCS": (89, 89, 89), "NGCCS": (86, 108, 140), "BMCCS": (172, 199, 119),
    "CO": (89, 89, 89), "NG": (86, 108, 140), "BF": (100, 180, 100), "DG": (129, 149, 177),
    "RG": (170, 183, 202), "DS": (183, 66, 63), "HF": (121, 43, 41), "BM": (172, 199, 119),
    "WS": (150, 75, 0), "WION": (143, 119, 173), "WIOF": (112, 48, 160), "SOU": (230, 175, 0),
    "SOSTH": (234, 67, 0), "GO": (192, 80, 77), "HYDRP": (0, 176, 240), "HYDMP": (0, 139, 188),
    "NU": (186, 28, 175), "TID": (0, 100, 150), "OCWV": (0, 100, 150), "HYDSP": (31, 80, 153),
    "LF": (209, 58, 54), "LI": (123, 96, 83), "HYDM": (0, 176, 240), "SOU1": (230, 175, 0),
    "SOC1": (234, 67, 0), "WI": (143, 119, 173),
    "NI": (255, 0, 127)  # Net Imports
}

techname_map = {
    "COCCS": "Coal CCS", "NGCCS": "Natural Gas CCS", "BMCCS": "Biomass CCS",
    "CO": "Coal", "NG": "Natural Gas", "BF": "Biofuel", "DG": "Derived Gas",
    "RG": "Refined Gas", "DS": "Diesel", "HF": "HFO", "BM": "Biomass",
    "WS": "Waste", "WION": "Wind Onshore", "WIOF": "Wind Offshore", "SOU": "Solar PV",
    "SOSTH": "CSP", "GO": "Geothermal", "HYDRP": "Hydro ROR", "HYDMP": "Hydro Dam",
    "NU": "Nuclear", "TID": "Tidal", "OCWV": "Ocean Wave", "HYDSP": "Pumped Hydro",
    "LF": "LFO", "LI": "Lignite", "HYDM": "Hydro", "SOU1": "Solar PV",
    "SOC1": "CSP", "WI": "Wind",
    "NI": "Net Imports"
}

country_name_map = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus",
    "CZ": "Czechia", "DE": "Germany", "DK": "Denmark", "EE": "Estonia", "GR": "Greece",
    "ES": "Spain", "FI": "Finland", "FR": "France", "HR": "Croatia", "HU": "Hungary",
    "IE": "Ireland", "IS": "Iceland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg",
    "LV": "Latvia", "MT": "Malta", "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
    "PT": "Portugal", "RO": "Romania", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia",
    "UK": "United Kingdom",
    "DZ": "Algeria", "AO": "Angola", "BJ": "Benin", "BW": "Botswana", "BF": "Burkina Faso",
    "BI": "Burundi", "CM": "Cameroon", "CV": "Cape Verde", "CF": "CAR", "TD": "Chad",
    "CG": "Congo", "CD": "DR Congo", "DJ": "Djibouti", "EG": "Egypt", "GQ": "Equatorial Guinea",
    "ER": "Eritrea", "SZ": "Eswatini", "ET": "Ethiopia", "GA": "Gabon", "GM": "Gambia",
    "GH": "Ghana", "GN": "Guinea", "GW": "Guinea-Bissau", "CI": "Ivory Coast", "KE": "Kenya",
    "LS": "Lesotho", "LR": "Liberia", "LY": "Libya", "MW": "Malawi", "ML": "Mali",
    "MR": "Mauritania", "MA": "Morocco", "MZ": "Mozambique", "NA": "Namibia", "NE": "Niger",
    "NG": "Nigeria", "RW": "Rwanda", "SN": "Senegal", "SL": "Sierra Leone", "SO": "Somalia",
    "ZA": "South Africa", "SS": "South Sudan", "SD": "Sudan", "TZ": "Tanzania", "TG": "Togo",
    "TN": "Tunisia", "UG": "Uganda", "ZM": "Zambia", "ZW": "Zimbabwe"
}

def process_file(data_file, out_prefix, tag):
    # Load and filter
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
    df = df[~df["Technology"].str.contains("(?:%s)$" % "|".join(exclude_suffixes), regex=True, na=False)]
    df = df[~df["Technology"].str.contains(r"^[A-Z]{2}EL.*PH1$", regex=True, na=False)]
    df["TechBase"] = df["Technology"].str.replace(r"(H1|N1|H0|N0)$", "", regex=True)

    def get_prefix(tech):
        for p in sorted(prefix_color_map, key=len, reverse=True):
            if p in tech:
                return p
        return None

    df["TechPrefix"] = df["TechBase"].apply(get_prefix)
    df = df[df["TechPrefix"].notna()]
    df["TechName"] = df["TechPrefix"].map(techname_map)
    df["Color"] = df["TechPrefix"].map(lambda x: [v/255 for v in prefix_color_map.get(x)])
    df = df[df["Year"].isin(years_to_include)]

    grouped = df.groupby(["Country","Year","TechName","TechPrefix"]).agg({"Value":"sum"}).reset_index()

    # === Net imports ===
    net_import_raw = []
    tech_pattern = re.compile(r'^[A-Z]{2}EL[A-Z]{2}PH1$')
    with open(data_file, "r") as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) < 5: continue
            param, region, tech, mode = parts[:4]
            if param == "TotalAnnualTechnologyActivityByMode" and tech_pattern.match(tech):
                net_import_raw.append(parts)

    if net_import_raw:
        years = list(range(2021, 2021 + len(net_import_raw[0]) - 4))
        df_net = pd.DataFrame(net_import_raw, columns=['Parameter','Region','Technology','Mode']+years)
        for y in years: df_net[y] = pd.to_numeric(df_net[y], errors='coerce')

        def extract_countries(code):
            m = re.match(r'^([A-Z]{2})EL([A-Z]{2})PH1$', code)
            return (m.group(1), m.group(2)) if m else (None, None)

        df_net[['Country_A','Country_B']] = df_net['Technology'].apply(lambda x: pd.Series(extract_countries(x)))
        net_import = {}
        for _,row in df_net.iterrows():
            ca,cb = row['Country_A'],row['Country_B']; mode=int(row['Mode']); vals=row[years].values.astype(float)
            for c in [ca,cb]:
                if c not in net_import: net_import[c] = np.zeros(len(years))
            if mode==1: net_import[cb]+=vals; net_import[ca]-=vals
            elif mode==2: net_import[ca]+=vals; net_import[cb]-=vals

        net_df = pd.DataFrame.from_dict(net_import,orient='index',columns=years).reset_index().rename(columns={'index':'Country'})
        net_df[years] = net_df[years]*0.27778
        melted = net_df.melt(id_vars="Country",var_name="Year",value_name="Value")
        melted["Year"]=melted["Year"].astype(int); melted["TechName"]="Net Imports"; melted["TechPrefix"]="NI"
        melted["Color"]=[tuple(c/255 for c in prefix_color_map["NI"])]*len(melted)
        grouped = pd.concat([grouped,melted],ignore_index=True)

    grouped["Total"] = grouped.groupby(["Country","Year"])["Value"].transform("sum")
    grouped["Share"] = grouped["Value"]/grouped["Total"]

    europe = ["AT","BE","BG","CH","CY","CZ","DE","DK","EE","GR","ES","FI","FR","HR","HU","IE","IT","LT","LU","LV","MT","NL","NO","PL","PT","RO","SE","SI","SK","UK"]
    africa = [c for c in country_name_map if c not in europe and c not in excluded_countries]

    grouped_eu,grouped_af = grouped[grouped["Country"].isin(europe)],grouped[grouped["Country"].isin(africa)]
    order_eu=grouped_eu.groupby("TechName")["Share"].mean().sort_values(ascending=False).index.tolist()
    order_af=grouped_af.groupby("TechName")["Share"].mean().sort_values(ascending=False).index.tolist()
    prefix_by_tech=grouped.drop_duplicates("TechName").set_index("TechName")["TechPrefix"]
    cmap_eu={t:[v/255 for v in prefix_color_map[prefix_by_tech[t]]] for t in order_eu}
    cmap_af={t:[v/255 for v in prefix_color_map[prefix_by_tech[t]]] for t in order_af}
    pivot=grouped.pivot_table(index=["Country","Year"],columns="TechName",values="Share",fill_value=0)

    def plot_region(name,codes,pdf,n,corder,cmap,ncol):
        sel=[c for c in codes if c in pivot.index.get_level_values(0)]
        pages=int(np.ceil(len(sel)/n))
        barw,gapw,gapb=0.8,1,0.5
        for pg in range(pages):
            subs=sel[pg*n:(pg+1)*n]; fig,ax=plt.subplots(figsize=(max(18,len(subs)*1.6),9))
            xpos,tpos,tlabels=[],[],[]
            for i,c in enumerate(subs):
                for j,y in enumerate(years_to_include):
                    try: row=pivot.loc[(c,y)]
                    except KeyError: continue
                    x=i*(gapw*len(years_to_include)+gapb)+j*gapw; bpos,bneg=0,0
                    for t in corder:
                        v=row.get(t,0); col=cmap.get(t,[0.6,0.6,0.6])
                        if prefix_by_tech[t] in ["COCCS","NGCCS","BMCCS"]:
                            ax.bar(x,v,bottom=(bpos if v>=0 else bneg),width=barw,
                                   color=col,edgecolor="white",linewidth=0,hatch="/////",zorder=3)
                        else:
                            ax.bar(x,v,bottom=(bpos if v>=0 else bneg),width=barw,
                                   color=col,zorder=3)
                        if v>=0: bpos+=v
                        else: bneg+=v
                    xpos.append(x); tpos.append(x); tlabels.append(str(y))
            ax.set_xticks(tpos); ax.set_xticklabels(tlabels,rotation=90,fontsize=14)
            lblpos=[i*(gapw*len(years_to_include)+gapb)+(gapw*(len(years_to_include)-1))/2 for i in range(len(subs))]
            lblnames=[country_name_map.get(cd,cd) for cd in subs]
            for xp,l in zip(lblpos,lblnames): ax.text(xp,-0.18,l,fontsize=14,ha='center',va='top',transform=ax.get_xaxis_transform())
            ax.set_xlim(min(xpos)-1,max(xpos)+1); ax.set_ylabel("Share of Total Technology Activity (%)",fontsize=16)
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0)); ax.tick_params(axis='y',labelsize=13)
            ax.set_title(f"{name} – Technology Activity Shares (2021, 2030, 2050) – {tag}",fontsize=16,pad=20)
            ax.grid(True,which="major",axis="y",linestyle="--",alpha=0.5,zorder=0); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            legend=[Patch(facecolor=cmap[t],edgecolor="white" if prefix_by_tech[t] in ["COCCS","NGCCS","BMCCS"] else None,
                          linewidth=0,hatch="/////" if prefix_by_tech[t] in ["COCCS","NGCCS","BMCCS"] else None,
                          label=techname_map.get(prefix_by_tech[t],t)) for t in corder]
            ax.legend(handles=legend,loc='lower center',bbox_to_anchor=(0.5,-0.40),ncol=ncol,fontsize=11,frameon=False)
            plt.tight_layout(rect=[0,0.05,1,0.95])
            pdf.savefig(fig,bbox_inches='tight')
            fig.savefig(f"{out_prefix}_{name}_page{pg+1}.png",dpi=900,bbox_inches='tight'); plt.close()

    out_pdf=f"{out_prefix}.pdf"
    with PdfPages(out_pdf) as pdf:
        plot_region("Europe",europe,pdf,countries_per_page_eu,order_eu,cmap_eu,ncol=12)
        plot_region("Africa",africa,pdf,countries_per_page_africa,order_af,cmap_af,ncol=8)

    print(f"✅ Visualisation successfully completed, check {out_pdf}")


# === Run single file from CMD ===
process_file(data_file, out_prefix, tag)
