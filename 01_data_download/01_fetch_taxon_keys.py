#!/usr/bin/env python
# coding: utf-8

"""
Author       : Aditya Jain
Date Started : May 9, 2022

Edited by    : Katriona Goldmann, Levan Bokeria
About        : This script fetches unique taxon keys for species list
                from GBIF database
"""

from pygbif import species as species_api
import pandas as pd
import argparse
import warnings

warnings.filterwarnings("ignore")


parser = argparse.ArgumentParser()
parser.add_argument(
    "--species_filepath", help="path of the species list", required=True
)
parser.add_argument(
    "--column_name", help="column name of the species entries", required=True
)
parser.add_argument(
    "--output_filepath",
    help="path to the output file with csv extension",
    required=True,
)
args = parser.parse_args()

file_path = args.species_filepath
column_name = args.column_name
out_filename = args.output_filepath


def get_gbif_key_backbone(name):
    """given a species name, this function returns the unique gbif key and
    other attributes using backbone API
    """

    # default values
    taxon_key = [-1]
    order = ["NA"]
    family = ["NA"]
    genus = ["NA"]
    search_species = [name]
    # the name returned on search, can be different from the search
    gbif_species = ["NA"]
    confidence = [""]
    status = ["NA"]
    match_type = ["NONE"]

    data = species_api.name_backbone(name=name, strict=True, rank="species")

    # if rank not a key in data
    if "rank" not in data:
        print(name + " returns no rank")

    elif data["rank"] != "SPECIES":
        print(name + " returns rank=" + data["rank"] + " instead of SPECIES")

    else:
        if data["matchType"] == "NONE":
            confidence = [data["confidence"]]

        else:

            taxon_key = [data["usageKey"]]
            order = [data["order"]]
            family = [data["family"]]
            genus = [data["genus"]]
            confidence = [data["confidence"]]
            gbif_species = [data["species"]]
            status = [data["status"]]
            match_type = [data["matchType"]]

        df = pd.DataFrame(
            list(
                zip(
                    taxon_key,
                    order,
                    family,
                    genus,
                    search_species,
                    gbif_species,
                    confidence,
                    status,
                    match_type,
                )
            ),
            columns=[
                "taxon_key_gbif_id",
                "order_name",
                "family_name",
                "genus_name",
                "search_species_name",
                "gbif_species_name",
                "confidence",
                "status",
                "match_type",
            ],
        )
        return df


# fetch species names from the list
data = pd.read_csv(file_path, index_col=False)
species_list = []
for indx in data.index:
    species_list.append(data[column_name][indx])

data_final = pd.DataFrame(
    columns=[
        "taxon_key_gbif_id",
        "order_name",
        "family_name",
        "genus_name",
        "search_species_name",
        "gbif_species_name",
        "confidence",
        "status",
        "match_type",
    ],
    dtype=object,
)

# fetch taxonomy data from GBIF
for name in species_list:
    data = get_gbif_key_backbone(name)
    data_final = data_final.append(data, ignore_index=True)

# save the file
data_final.to_csv(out_filename, index=False)
