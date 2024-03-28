"""

Author      : Matija Kovacic
Create-date : 20.10.2023.
Modify-date : 23.01.2024.
Version     : R1-4
File        : quantitySync.py
Description :
    Skripta za sinkroniziranje DELIFE proizvoda.
    Skripta prvo skida zadnju verziju delife csv sa njihovog servera,
    zatim usporedjue kolicine unutar shopify.csv i delife.csv
    Sve količine prepisiju se u shopify.csv i prepisuje se cijeli fajl u new.csv.

"""

import os
from tqdm import tqdm
from time import sleep
import pandas as pd
from texttable import Texttable
from urllib.request import urlretrieve
import progressbar

download = False

version = 'R1-3'
inputFolder = "inputTables/"
outputFolder = "outputTables/"

# checking if the directory exist
if not os.path.exists(inputFolder):
    inputFolder = ""

outputFileName = "quantitySync.csv"
delife_filename = "delife.csv"
shopifyFile = inputFolder + "shopify.csv"
delifeFile  = inputFolder + delife_filename
proceed = True

print("")
print("Version: " + version)
print("")

pbar = None
def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None
        

if download:
    delife_url = ("https://www.delife.eu/xxx")
    print("")
    print("Start download Delife stock status...")
    print("Download URL: " + delife_url)
    print("")
    #delife_filename = "test_down.pdf"
    urlretrieve(delife_url, delifeFile, show_progress)
    print("")
    print("Download completed successfully!")
    print("File is saved: " + delifeFile)
    print("")


if not os.path.exists(shopifyFile):
    print("Input file: " + shopifyFile + " does not exist. Copy file in folder and try again!")
    print("")
    print("")
    input("Press Enter to continue...")
    proceed = False

if not os.path.exists(delifeFile):
    print("Input file: " + delifeFile + " does not exist. Copy file in folder and try again!")
    print("")
    print("")
    input("Press Enter to continue...")
    proceed = False


if proceed == True:
    shopify = pd.read_csv(shopifyFile, sep=',', low_memory=False)
    delife = pd.read_csv(delifeFile, sep=';', low_memory=False)

    shopify_rows = shopify.shape[0]  # Gives number of rows

    table_total = Texttable()
    table_total.set_deco(Texttable.HEADER)
    table_total.set_cols_align(["l", "c"])

    rows_total = []
    header_total = ["Name", "Total"]
    rows_total.append(header_total)

    table_sku = Texttable()
    table_sku.set_deco(Texttable.HEADER)
    table_sku.set_cols_align(["l", "c"])

    rows_sku = []
    header_sku = ["Variant SKU", "Quantity"]
    rows_sku.append(header_sku)

    print("")
    print("Sync start...")
    print("")

    total = 0
    total_zero = 0
    total_positive = 0
    total_not_exist = 0

    with tqdm(total=shopify_rows) as pbar:
        for i in shopify.index:
            pbar.update(1)
            if pd.notna(shopify['Variant SKU'][i]):
                # print(shopify['Variant SKU'][i])
                shopify_id = str(shopify['Variant SKU'][i])
                is_sku_delife = shopify_id.startswith('10')
                exist_in_delife = False
                # get in only if sku is delife
                if is_sku_delife == True:
                    for j in delife.index:
                        delife_id = "10" + str(delife['variationNo'][j])
                        delife_quantity_str = str(delife['stockNet'][j])
                        delife_quantity = delife['stockNet'][j].astype(int)
                        # shopify_id is founded 
                        if shopify_id == delife_id:
                            exist_in_delife = True
                            rows_sku.append([delife_id, delife_quantity_str])
                            total = total + 1
                            shopify.at[i,'Variant Inventory Tracker']='shopify'
                            # delife quantity in less than zero
                            if(delife_quantity <= 0):
                                shopify.at[i,'Variant Inventory Qty']=0
                                total_zero = total_zero + 1
                            else:
                                # shopify.at[i,'Variant Inventory Qty']= 0
                                shopify.at[i,'Variant Inventory Qty']=delife_quantity
                                total_positive = total_positive + 1
                    # article is delife but does not exist in delife excel table
                    if exist_in_delife == False:
                        shopify.at[i,'Variant Inventory Tracker']='shopify'
                        shopify.at[i,'Variant Inventory Qty']=0
                        total_not_exist = total_not_exist + 1

    rows_total.append(["Total", total])
    rows_total.append(["Total negative", total_zero])
    rows_total.append(["Total positive", total_positive])
    rows_total.append(["Total not exist in delife", total_not_exist])

    sleep(1)
    print("")
    print("Sync completed successfully!")
    print("")
    print("")
    sleep(1)
    table_sku.add_rows(rows_sku)
    print(table_sku.draw())
    print("")
    print("")
    table_total.add_rows(rows_total)
    print(table_total.draw())
    print("")
    sleep(0.5)

    # checking if the directory exist
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder) 

    shopify.to_csv(outputFolder + outputFileName, sep=',', index=False,header=True)

    print("")
    print("New file has been successfully saved! File name is: " + outputFolder + outputFileName)
    print("")
    print("")
    input("Press Enter to continue...")
