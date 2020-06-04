import pandas as pd
import numpy as np
import os
import shutil
import glob

#Directory that all hashtag scrapes are gathered in
base_dir =  r"C:\Users\Dustin\Python_Scripts\Generative_Deep_Learning\PotterGAN\PotterGAN\data"

#names of folders within base dir, each with post_details.csv from scraping process
hashtag_folder_list = ['ceramicmug','ceramiccup','handmademug']

#Will create in base dir for combined dataset
output_folder = 'aggregate_mug_data'
output_dir_name = os.path.join(base_dir,output_folder)

if not os.path.exists(output_dir_name):
    os.makedirs(output_dir_name)

aggregate_posts = pd.DataFrame(columns = ['post_link','media_type','likes','post_age','caption','hashtags','account_name'])

for ht in hashtag_folder_list:
    dir_name = os.path.join(base_dir,ht)

    #Aggregate post details
    single_ht_data = pd.read_csv(os.path.join(dir_name,'post_details.csv'),
    names = ['post_link','media_type','likes','post_age','caption','hashtags','account_name'],
    index_col=False)

    aggregate_posts = aggregate_posts.append(single_ht_data)

    #Copy Files - ending up with unique images in the folder
    src_files = os.listdir(dir_name)
    for file_name in glob.iglob(os.path.join(dir_name,"*.jpg")):
        shutil.copy(file_name, output_dir_name)

#Get unique posts
aggregate_posts['filename'] = aggregate_posts['post_link'].str.split('/',expand=True).iloc[:,-2]
aggregate_posts.drop_duplicates(subset=['post_link'], inplace=True)
aggregate_posts.to_csv(os.path.join(output_dir_name,'aggregate_post_details.csv'),index=False)

