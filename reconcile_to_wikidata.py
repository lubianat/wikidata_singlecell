#!/usr/bin/python3

import os
import pandas as pd
from wikidata2df import wikidata2df

today = "25_12_2021"


def main():

    os.system(
        "wget -O data/sc_studies.csv https://docs.google.com/spreadsheets/d/e/2PACX-1vRlo0kIz4xPRjrFf575HbPBDRnuL_jClTCo3BkO5oMaP1sSyY-3c28Z5YDP26DfNUey3lsPNF5ydZiB/pub?gid=0&single=true&output=csv"
    )

    studies = pd.read_csv("data/sc_studies.csv")

    print(studies.head())

    cols_of_interest = ["DOI", "Organism", "Tissue", "Technique", "Data location"]

    studies = studies[cols_of_interest]
    studies["DOI"] = [doi.upper() for doi in studies["DOI"]]

    reconciled_articles = pd.read_csv("reconciled_articles.csv")

    new_studies = studies[
        [doi not in reconciled_articles["DOI"] for doi in studies["DOI"]]
    ]

    doi_list = new_studies["DOI"]

    dois_in_chunks = chunks(doi_list, 99)

    df_now = pd.DataFrame(columns=["itemLabel", "normalized_doi", "item"])

    for doi_list in dois_in_chunks:
        df = get_doi_df(doi_list)
        df_now = df_now.append(df)

    studies = studies.merge(
        df_now, left_on="DOI", right_on="normalized_doi", how="left"
    )

    studies.dropna(subset=["normalized_doi"]).to_csv(
        "reconciled_articles.csv", sep="\t", index=False
    )

    ### Export Main Subject quickstatements

    with open(f"main_subject_scrnaseq_{today}.qs", "w") as f:
        for i, row in new_studies.iterrows():
            s = row["item"]
            p = "P921"  # external data available at
            o = "Q105406038"
            rp1 = "S248"
            ro1 = "Q103034964"
            rp2 = "S854"
            ro2 = '"https://www.nxn.se/single-cell-studies/data.tsv"'
            rp4 = "S813"
            ro4 = "+2021-02-07T00:00:00Z/11"
            f.write(f"{s}|{p}|{o}|{rp1}|{ro1}|{rp2}|{ro2}|{rp4}|{ro4}")
            f.write("\n")


##### Helper functions #####


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_doi_df(doi_list):
    doi_list = ['"' + doi + '"' for doi in doi_list]
    doi_string = " ".join(doi_list)
    query = (
        """
    SELECT ?normalized_doi ?item  ?itemLabel
    WHERE {
      {
        SELECT ?item ?normalized_doi WHERE {
          VALUES ?doi {

          """
        + doi_string
        + """

          }
          BIND(UCASE(?doi) AS ?normalized_doi)
          ?item wdt:P356 ?normalized_doi.
        }
      }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    """
    )
    doi_df = wikidata2df(query)
    return doi_df


if __name__ == "__main__":
    main()
