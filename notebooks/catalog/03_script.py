#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os
from datetime import datetime

root = tk.Tk()
root.withdraw()
correct_files=0
name_file_asked=""

def messagebox(title, text):
    tk.messagebox.showinfo(title, text)  #tkinter.messagebox.showinfo(title, text)

def select_file(msg):
    messagebox("Information",msg)
    ruta = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
    if ruta !="":
        return ruta
    else:
        leave_question= tk.messagebox.askquestion("Question","Do you want to exit?")
        if leave_question== "yes":
            sys.exit()
        else:
            messagebox("Information","You have to select a "+name_file_asked+"file")
        return 0

def read(file_route, name, column_list, correct_file): 
    ruta = file_route
    correct_files=0
    str1=""
    try:
        file = pd.read_csv(ruta,sep=",")  
        if set(list(file.columns.values.tolist())) != set(column_list):
            col_names= ' , '.join([str(elem) for elem in column_list])
            messagebox("Information","Your input "+name +" file should have the following column names: " + col_names+". Please select the file again.")
            leave_question= tk.messagebox.askquestion("Question","Do you want to exit?")
            if leave_question== "yes":
                sys.exit()
        else: 
            correct_files = 1
    except FileNotFoundError:
        print("No file selected")
        leave_question= tk.messagebox.askquestion("Question","Do you want to exit?")
        if leave_question== "yes":
            sys.exit()
        messagebox("Information","You have to select the two files")
    return file, correct_files

def melt_barcodes(df,product_id,barcodes):
    aux = pd.melt(df.set_index(product_id)[barcodes].astype(str).str.split(',',expand=True), 
                 ignore_index=False, value_name=barcodes).dropna()
    aux[barcodes] = aux[barcodes].str.replace('[','').str.replace(']','')
    df = df.drop(columns=barcodes).merge(aux, on=product_id, how='outer') #estaba en outer
    return df


def add_check_digit(barcode):
    even = 0
    odd = 0
    counter = 1
    for d in barcode:
        if counter % 2 == 0:
            counter += 1
            even += int(d)
        else:
            counter += 1
            odd += int(d)
    if 10 - (even + odd * 3) % 10 <= 9:
        check_digit = str(10 - (even + odd * 3) % 10)
    else:
        check_digit = str(0)
    return barcode + check_digit

def correct_barcode(barcode):
    if barcode.zfill(14) == add_check_digit(barcode.zfill(14)[0:len(barcode.zfill(14)) - 1]):
        return barcode.zfill(12)
    else:
        if len(barcode) < 14:
            return add_check_digit(barcode.zfill(13)).lstrip('0').zfill(12)
        elif len(barcode) >= 14:
            return 'BARCODE ISSUE'  
        
def barcode_12digit(barcode_list):
        barcodes_12_digit=[]
        for barcode in barcode_list:
            barcode_str=str(barcode).lstrip('0')
            if len(barcode_str)==12:
                barcodes_12_digit.append(barcode_str)
            elif len(barcode_str)<12 and len(barcode_str)>=7:
                barcode_str_new=str(barcode_str).zfill(12)
                barcodes_12_digit.append(barcode_str_new)
            else:
                barcodes_12_digit.append("does not meet condition")
        return barcodes_12_digit

def short_barcode (barcodes_12_digit):        
    barcode_verify=[]        
    for barcode in barcodes_12_digit:
        barcode_aux=str(barcode)
        if len(barcode_aux)==12 and barcode_aux !="does not meet condition":
            if (barcode_aux[10]=='5' or barcode_aux[10]=='6' or barcode_aux[10]=='7' or barcode_aux[10]=='8' or barcode_aux[10]=='9') and barcode_aux[5]!='0' and barcode_aux[6]=='0' and barcode_aux[7]=='0' and barcode_aux[8]=='0' and barcode_aux[9]=='0':
                new_barcode=barcode_aux[0]+barcode_aux[1]+barcode_aux[2]+barcode_aux[3]+barcode_aux[4]+barcode_aux[5]+barcode_aux[10]+barcode_aux[11]
                barcode_verify.append(new_barcode)

            elif barcode_aux[5]=='0' and barcode_aux[6]=='0' and barcode_aux[7]=='0' and barcode_aux[8]=='0' and barcode_aux[9]=='0' and barcode_aux[4]!='0':
                new_barcode=barcode_aux[0]+barcode_aux[1]+barcode_aux[2]+barcode_aux[3]+barcode_aux[4]+barcode_aux[10]+'4'+barcode_aux[11]
                barcode_verify.append(new_barcode)

            elif barcode_aux[4]=='0' and barcode_aux[5]=='0' and barcode_aux[6]=='0' and barcode_aux[7]=='0' and (barcode_aux[3]=='0' or barcode_aux[3]=='1' or barcode_aux[3]=='2'):
                new_barcode=barcode_aux[0]+barcode_aux[1]+barcode_aux[2]+barcode_aux[8]+barcode_aux[9]+barcode_aux[10]+barcode_aux[3]+barcode_aux[11]
                barcode_verify.append(new_barcode)

            elif barcode_aux[4]=='0' and barcode_aux[5]=='0' and barcode_aux[6]=='0' and barcode_aux[7]=='0' and barcode_aux[8]=='0' and (barcode_aux[3]=='3' or barcode_aux[3]=='4' or barcode_aux[3]=='5' or barcode_aux[3]=='6' or barcode_aux[3]=='7' or barcode_aux[3]=='8' or barcode_aux[3]=='9'):
                new_barcode=barcode_aux[0]+barcode_aux[1]+barcode_aux[2]+barcode_aux[3]+barcode_aux[9]+barcode_aux[10]+'3'+barcode_aux[11]
                barcode_verify.append(new_barcode)
            else:
                barcode_verify.append('No short barcode') 

        else:
            barcode_verify.append('No short barcode') 
    return barcode_verify
 

question= tk.messagebox.askquestion("Question","Do you just want to calculate short barcodes?")

if question == "no":
    while correct_files==0:
        supply_file = select_file("Please select the SUPPLY QUERY download from Metabase. Only .csv files are permitted.")
        if supply_file==0:
            correct_files=0
        else:
            supply, correct= read(supply_file, "supply", ["catalog_product_id","barcode","sku_source"], correct_files)
            correct_files = correct
            
    correct_files=0   
    
    while correct_files==0:
        catalog_file = select_file("Please select the CATALOG QUERY download from Metabase. Only .csv files are permitted.")
        if catalog_file==0:
            correct_files=0
        else:
            catalog, correct2= read(catalog_file, "catalog", ["product_id","catalog_barcodes"], correct_files)
            correct_files = correct2

    downloads_route = os.path.dirname(supply_file) #aca guardaremos los archivos

    root.destroy() 
    
    supply = supply.rename(columns={"catalog_product_id": "product_id"})

    #Agrupo los barcodes de supply por product_id 
    supply2 = supply.groupby('product_id')['barcode'].apply(list).reset_index() 
    supply2 = supply2.rename(columns={"barcode": "supply_original_barcode_aux"})
    supply2['supply_not_repeated_barcode'] = supply2['supply_original_barcode_aux']

    list_barcodes_no_checkdigit=[]
    list_products_id_no_checkdigit=[]

    #Reviso los barcodes de supply y creo una lista con aquellos que están repetidos pero sin check digit (ej: 78887990022, 788879900223: elemino el primero)
    for i in range(len(supply2)): 
        prod_id= supply2['product_id'].iloc[i]
        list_barcodes= supply2['supply_original_barcode_aux'].iloc[i]
        ints = [int(item) for item in list_barcodes]
        list_barcodes = list(set(ints)) # sin los duplicados
        sorted_barcodes= sorted(list_barcodes) 
        supply2['supply_not_repeated_barcode'][i]= sorted_barcodes
        if len(sorted_barcodes)>1:
            for b_1 in range(len(sorted_barcodes)-1):
                barcode_1= sorted_barcodes[b_1]
                for barcode_2 in (sorted_barcodes[b_1+1:]):
                    if str(barcode_1).lstrip("0") in str(barcode_2).lstrip("0"):
                        list_barcodes_no_checkdigit.append(barcode_1) #aca tengo que agregar el prod id pq lo que puede pasar es que el barcode se repita para distintos product id
                        list_products_id_no_checkdigit.append(prod_id)

    #Desagrupo los barcodes y creo una linea por product id
    supply3 = melt_barcodes(supply2,'product_id','supply_not_repeated_barcode')

    supply3["supply_not_repeated_barcode"] = supply3["supply_not_repeated_barcode"].str.replace(' ', '')
    supply3 = supply3.rename(columns={"supply_not_repeated_barcode": "barcode"})
    supply3["Information"] = "OK"
    supply3 = supply3.drop("variable", axis=1)
    
    supply3['barcode'] = supply3['barcode'].astype(np.int64)
    supply['barcode'] = supply['barcode'].astype(np.int64)
    
    sup_merged_aux = supply.merge(supply3, how='left', on=["product_id","barcode"]) 
    sup_merged_aux = sup_merged_aux.rename(columns={"barcode": "supply_original_barcode"})
    sup_merged = sup_merged_aux.copy()
    
    for barcode in list_barcodes_no_checkdigit:
        index = sup_merged.index[sup_merged['supply_original_barcode'] == (barcode)]
        for i in index:
            if sup_merged.loc[i,'product_id'] in list_products_id_no_checkdigit:
                sup_merged.loc[i,'Information']= "Repeated barcode with no check-digit"

    sup_merged['Information'] = sup_merged['Information'].replace(np.nan, "Repeated barcode")

    #Binario para considerar o no la linea de supply
    sup_merged['Consider']= 0
    ok_index = sup_merged.index[sup_merged['Information'] == "OK"].tolist()
    for i in ok_index:
        sup_merged.loc[i,'Consider']= 1

    supply=supply.rename(columns={"barcode": "supply_original_barcode"})
    df = catalog.merge(sup_merged, how='left', on=["product_id"])  #con esto no es necesario cambiar lo que pongo en la query de supply

    if (df['supply_original_barcode'].isnull().values.all()):
        messagebox("Information","Check your supply barcode file, it doesn't match with the catalog one. Please start again.")
        sys.exit()
            
    df['supply_original_barcode'] = df['supply_original_barcode'].fillna(0).astype(np.int64)

    barcode_with_check_digit=[]

    for i in range(len(df)):
        if df['supply_original_barcode'][i] != 0 : 
                barcode_str=str(df.supply_original_barcode[i])
                b=correct_barcode(barcode_str)
                barcode_with_check_digit.append(b)   
        else:
            barcode_with_check_digit.append(0)

    df["supply_barcode_corrected"] = barcode_with_check_digit

    df['short barcode']= short_barcode(barcode_12digit(barcode_with_check_digit))

    products_for_tag=[]
    lista_catalog_barcode =[]
    lista_product_id = []
    data= []
    
    agrupado_supply_corrected_barcodes= df.groupby('product_id')['supply_barcode_corrected'].apply(list)  

    for i in range (len(df['product_id'])):
        if df['short barcode'].iloc[i] != 'No short barcode' and df['Consider'].iloc[i] != 0 :
            agrupado_supply_corrected_barcodes[df['product_id'].iloc[i]].append(df['short barcode'].iloc[i])

    for i in range (len(df['catalog_barcodes'])):
        barcodes = (df["catalog_barcodes"].iloc[i])
        supply_barcode_corrected = (df["supply_barcode_corrected"].iloc[i])
        product_id = (df["product_id"].iloc[i])
        considerar = (df["Consider"].iloc[i])
        
        if ',' in str(barcodes):
            lista_catalog_barcodes = list(barcodes.split(','))
            for j in range(len(lista_catalog_barcodes)):
                str_barcode= str(lista_catalog_barcodes[j])
                if len(str_barcode.lstrip('0'))>= 7 and supply_barcode_corrected !=0 and supply_barcode_corrected != 'BARCODE ISSUE' and product_id not in products_for_tag:
                    products_for_tag.append(product_id) #agrego al tag aquellos prod que tienen supply barcode              
        else:
            str_barcode = str(barcodes)
            lista_catalog_barcodes = str_barcode
            if len(str_barcode.lstrip('0'))>= 7 and supply_barcode_corrected !=0 and supply_barcode_corrected != 'BARCODE ISSUE' and product_id not in products_for_tag:
                    products_for_tag.append(product_id) #agrego al tag aquellos prod que tienen supply barcode

        for element in agrupado_supply_corrected_barcodes[product_id]:
            if element != 0 and element != 'BARCODE ISSUE' and considerar ==1 and element not in lista_catalog_barcodes and element.lstrip("0") not in lista_catalog_barcodes and [product_id, element] not in data and [product_id, element.lstrip("0")] not in data:
                   data.append([product_id, element.lstrip("0")])
    prod_1=""
    prod_2=""
     
    #Create the information on duplicated prod_id
    duplicated_barcodes= df.groupby('supply_original_barcode')['product_id'].apply(list).reset_index() 
    duplicated_barcodes['duplicate']=0
    for i in range (len(duplicated_barcodes)):
        lista_product = duplicated_barcodes['product_id'][i]
        barcode = duplicated_barcodes['supply_original_barcode'][i]
        if (len(lista_product) > 1):
            duplicated_barcodes.loc[i,'duplicate']=1
            prod_1 = prod_1 + "," + str(lista_product[0])
            prod_2 = prod_2 + "," + str(lista_product[1])  
    duplicated_barcodes_filtered = (duplicated_barcodes.query('duplicate == 1 and supply_original_barcode > 0'))

    
    query_1 = """ -- YOU SHOULD RUN IT ON THE SUPPLY DATABASE
        with product1 as 
            (select 
            sp.catalog_product_id,
            sp.name,
            sp.sku,
            sp.package,
            sp.img_url,
            sp.brand,
            REPLACE(LTRIM(REPLACE(barcode, '0', ' ')),' ', '0') as barcode,
            string_agg(sp.sku_source, ' , ') as sku_source
        from supply_product sp
        join supply_productbarcode spb on sp.id = spb.product_id
        where 
            sp.catalog_product_id in ("""
    query_2=""")
        group by 1,2,3,4,5,6,7
        ),

        product2 as
        (
        select 
            sp.catalog_product_id,
            sp.name,
            sp.sku,
            sp.package,
            sp.img_url,
            sp.brand,
            REPLACE(LTRIM(REPLACE(barcode, '0', ' ')),' ', '0') as barcode,
            string_agg(sp.sku_source, ' , ') as sku_source
        from supply_product sp
        join supply_productbarcode spb on sp.id = spb.product_id
        where 
            sp.catalog_product_id in ("""
    query_3= """)
        group by 1,2,3,4,5,6,7
        )

        select product1.barcode,
            product1.catalog_product_id as product1_catalog_product_id,
            product2.catalog_product_id as product2_catalog_product_id,
            product1.name as product1_name,
            product2.name as product2_name,
            product1.PACKAGE as product1_package,
            product2.PACKAGE as product2_package,
            product1.brand as product1_brand,
            product2.brand as product2_brand,
            product1.img_url as product1_img_url,
            product2.img_url as product2_img_url,
            product1.sku_source as product1_sku_source,
            product2.sku_source as product2_sku_source
        from product1
        join product2 on product2.barcode = product1.barcode
        order by barcode asc"""
    
    query= query_1 + prod_1[1:] + query_2 + prod_2[1:] + query_3
    
    #*****************************************_Files creation_******************************************
    now = datetime.now() 
    dt_string = now.strftime("%b-%d-%Y_%H:%M:%S") 
    
    directory = "Barcode_files_" + dt_string
    parent_dir = downloads_route
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
        
    print("Directory '% s' with outputs created" % directory)
    
    #  1.barcode tags
    if len(products_for_tag)>0:
        df_tag = pd.DataFrame(products_for_tag)
        df_tag = df_tag.rename(columns={0: "product_id"})
        df_tag['tag']= ("barcode validation required")
        ruta_barcodes_tags= path +"/2.Barcodes_tags.csv"
        df_tag.to_csv(ruta_barcodes_tags,index=False)  
    else:   
        messagebox("Information","There are no barcodes for tag")
     
    #  2.barcode to add in catalog
    if len(data)>0:
        df_barcodes_to_add = pd.DataFrame(data, columns=['product_id', 'barcode_to_Add'])
        df_barcodes_to_add = df_barcodes_to_add.groupby('product_id').agg(barcodes=('barcode_to_Add', ';'.join)).reset_index()
        ruta_barcodes_to_add= path +"/1.Catalog_Barcodes_to_add.csv"
        df_barcodes_to_add.to_csv(ruta_barcodes_to_add,index=False)   
    else:   
        messagebox("Information","There are no barcodes to add in catalog")
    
    #  3.Complete information
    ruta_df=path +"/5.Complete_information.csv"
    df_send = df.drop(["supply_original_barcode_aux","Consider"], axis=1)
    df_send['Information'] = df_send['Information'].replace(np.nan, "No supply barcode")
    df_send.to_csv(ruta_df,index=False)  
    
    #  4.Duplicated products id
    ruta_dup= path +"/3.Duplicated_product_id_info.csv"
    duplicated_barcodes_filtered = duplicated_barcodes_filtered.drop("duplicate", axis=1)
    duplicated_barcodes_filtered.to_csv(ruta_dup,index=False)  
    
    #  5.query    
    ruta_query = path +"/4.query_file.txt"
    query_file = open(ruta_query, "w") #x si no esta
    query_file.write(query)
    query_file.close()

    msg2= "There is a folder with the outputs on the following path of your pc: "+ path
    messagebox("Information",msg2)
    
else:
    correct_files=0
    while correct_files==0:
        barcode_file = select_file("Please select the barcode file, it should have 2 columns: product_id and barcode. Only .cvs files are permitted")
        if barcode_file==0:
            barcode_file=0
        else:
            df, correct_files= read(barcode_file, "barcode", ["product_id","barcode"], correct_files)
    
    downloads_route = os.path.dirname(barcode_file) #aca guardaremos los archivos
    
    barcodes_list = df["barcode"].tolist()
    df['short_barcode']= short_barcode(barcode_12digit(barcodes_list))
    
    df_filtered = (df.query('short_barcode != "No short barcode"'))
    
    ruta_short= downloads_route +"/Short_barcodes.csv"
    df_filtered.to_csv(ruta_short,index=False) 
    
    msg3= "The file was created in the following path of your pc: "+ downloads_route
    messagebox("Information",msg3)


# In[ ]:





# In[ ]:





# In[ ]:




