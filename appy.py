#import snowflake.connector
import openpyxl
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
#import logging
import time
import numpy as np
from random import randint
import base64
from io import BytesIO
from datetime import datetime

st.sidebar.title('Easy Inventory Planner')
st.sidebar.header('Content')
yan_sayfa_secenek = st.sidebar.radio(
    '',
    ('Easy Inventory Planner', 'About Analyses', 'Analyses')
)


if yan_sayfa_secenek == 'Analyses' :

 
 st.info('Once excel file is uploaded, analyses will automatically start.')
 rowy=[]
 rowy=['Product No','Category','Sub Category','21 Gün','42 Gün','63 Gün','84 Gün','Stok']
 st.write('Column order in excel file must be :')
 rowy   
 st.set_option('deprecation.showfileUploaderEncoding', False)
 uploaded_file = st.file_uploader("Select Excel File To Upload", type=['xlsx'])
 
 if uploaded_file :
  #try:
  df = pd.read_excel(uploaded_file)
  df.columns=['Product','Category','Sub-Category','Sales21','Sales42','Sales63','Sales84','Inventory']
  df['Product'] = df['Product'].astype('str')
  df['Category'] = df['Category'].astype('str')
  df['Sub-Category'] = df['Sub-Category'].astype('str')
  df_dummx= df.copy() 
  df_dummx= df_dummx.astype(str)
    
  df['Product'].fillna('-',inplace=True)
  df['Category'].fillna('-',inplace=True)
  df['Sub-Category'].fillna('-',inplace=True)
  df['Sales21'].fillna(0,inplace=True)
  df['Sales42'].fillna(0,inplace=True)
  df['Sales63'].fillna(0,inplace=True)
  df['Sales84'].fillna(0,inplace=True)
  df['Inventory'].fillna(0,inplace=True)
  st.dataframe(df_dummx) 
  #except:
  'Dosya yüklemede hata'
  'Excel dosyayı kontrol edin.'
   
  #st.stop() 
  #df=pd.DataFrame(rows) 
  
  #try:
  df_sfr= df.loc[df['Sales84']==0].copy()
  
  df_analiz= df.loc[df['Sales84'] > 0].copy()
  
  df_analiz['Range1']= df_analiz.Sales21
  df_analiz['Range2']= df_analiz.Sales42-df_analiz.Sales21
  df_analiz['Range3']= df_analiz.Sales63-df_analiz.Sales42
  df_analiz['Range4']= df_analiz.Sales84-df_analiz.Sales63
  
  df_analiz['ktsy']= (df_analiz[['Range1','Range2','Range3','Range4']].std(axis=1))/(df_analiz[['Range1','Range2','Range3','Range4']].mean(axis=1))
  
  kosul=[
  
  (df_analiz['ktsy']>= 0) & (df_analiz['ktsy']< 0.36), 
  (df_analiz['ktsy']>= 0.36) & (df_analiz['ktsy']< 0.70),
  (df_analiz['ktsy']>= 0.70 )& (df_analiz['ktsy']< 1.26),
  (df_analiz['ktsy']>= 1.26) ]
  
  secenek=[4,3,2,1]
  df_analiz['Label']= np.select(kosul,secenek,default=4)
  
  df_hedef= df_analiz[['Label','Range1','Range2','Range3','Range4']]
  
  hedef=df_hedef.values.tolist()
  kuple=[]
  tops=[]
  
  
  
  for i in hedef:
   bol=int(i[0])
   #print(bol)
   i.remove(i[0])
   kuple= sorted(i,reverse=True)
  
   tops.append(sum(kuple[0:bol])/bol)
   kuple=[]
  
  df_analiz['Predicted_Sales']= tops
  
  
  
  df_analiz['Label']=df_analiz['Label'].replace(1,'New Product1')
  df_analiz['Label']=df_analiz['Label'].replace(2,'New Product2')
  df_analiz['Label']=df_analiz['Label'].replace(3,'Predictable Sales')
  df_analiz['Label']=df_analiz['Label'].replace(4,'Very Predictable Sales')
  
  df_analiz.loc[((df_analiz['Range4'] != 0) & (df_analiz['Label'] == 'New Product1')), 'Label'] = 'Unpredictable Sales'
  
  df_analiz.loc[((df_analiz['Range1'] == 0) & (df_analiz['Label'] == 'New Product1')), 'Label'] = 'Unpredictable Sales'
  
  df_analiz.loc[((df_analiz['Range1'] != 0) & (df_analiz['Label'] == 'New Product1') & (df_analiz['Range3'] != 0) ), 'Label'] = 'Unpredictable Sales' 
  
  df_analiz.loc[((df_analiz['Range4'] != 0) & (df_analiz['Label'] == 'New Product2')), 'Label'] = 'Unpredictable Sales'
  
  df_analiz.loc[((df_analiz['Range2'] == 0) & (df_analiz['Label'] == 'New Product2')), 'Label'] = 'Unpredictable Sales'
  
  df_analiz.loc[((df_analiz['Range1'] == 0) & (df_analiz['Label'] == 'New Product2')), 'Label'] = 'Unpredictable Sales'
  
  df_analiz.loc[((df_analiz['Range1'] <df_analiz['Range2'] ) & (df_analiz['Label'] == 'Predictable Sales') & (df_analiz['Range1'] <df_analiz['Range3'] ) &
   (df_analiz['Range1'] <df_analiz['Range4'] )), 'Label'] = 'Decreasing Sales' 
  
  df_analiz.loc[((df_analiz['Range3']> df_analiz['Range1']) & (df_analiz['Range2']> df_analiz['Range1']) & 
   (df_analiz['Label'] == 'New Product2')), 'Label'] = 'Decreasing Sales'
  
  df_analiz['Stock_Cover'] = (df_analiz.Inventory)/(df_analiz.Predicted_Sales/21)
  df_analiz['Predicted_Sales'] = (df_analiz.Predicted_Sales/21)*30
   
  df_analiz=df_analiz.sort_values(by='Predicted_Sales', ascending=False) 
  
  df_analiz_download= df_analiz[['Product','Inventory','Sales21','Sales42','Sales63','Sales84','Label',
   'Stock_Cover', 'Predicted_Sales']].copy()
  
  df_analiz_download['Predicted_Sales']= df_analiz_download['Predicted_Sales'].round(0)
  df_analiz_download['Stock_Cover']= df_analiz_download['Stock_Cover'].round(0)
  
  
  
  
  df_analiz['Label']=df_analiz['Label'].replace('New Product1','New Products')
  df_analiz['Label']=df_analiz['Label'].replace('New Product2','New Products')
  
  df_analiz['Label']=df_analiz['Label'].replace('Very Predictable Sales','Predictable Sales')
   
  df_tutarlk = pd.pivot_table(df_analiz, values=['Product'], index=['Label'],  aggfunc='count' )
  df_tutarlk = df_tutarlk.reset_index()                #index to columns
  
  df_tutarlk['Kum']=  df_tutarlk['Product'].sum()
  total_product= df_tutarlk['Product'].sum()
  df_tutarlk['Ratio']= df_tutarlk.Product / df_tutarlk.Kum
  
  df_tutarlk.drop(['Kum'], inplace=True, axis=1)
  df_tutarlk.columns= ['Label','Product_Count','Ratio']
  
  df_tutarlk2=df_tutarlk.copy()
  
  df_tutarlk2['Ratio']=df_tutarlk2['Ratio']*100
  df_tutarlk2['Ratio']= df_tutarlk2['Ratio'].round(0)  
  
  total_product= str(total_product) + ' products analysed'
  #df_tutarlk['Product_Count']=df_tutarlk['Product_Count'].astype(str)
  #df_tutarlk['Ratio']=df_tutarlk['Ratio'].astype(str)
  #df.style.format("{:.2%}")
  #df.style.format({'B': "{:0<4.0f}", 'D': '{:+.2f}'})
  #df_tutarlk= df_tutarlk.style.format({'Ratio': '{:.0%}'})
  st.info('A- Predictability Analysis') 
  total_product
  
  df_tutarlk2=df_tutarlk2.astype(str)
  df_tutarlk2=df_tutarlk2.sort_values(by='Ratio', ascending=False)
  df_tutarlk2['Ratio']='%' + df_tutarlk2['Ratio']
  st.dataframe(df_tutarlk2)
  'Predictability Analysis shows the quality of inventory management. The higher percentage of the "Predictable Sales" ratio indicates the good quality of the inventory management.'
  #download_data
  st.info('B- Inventory Planner')
  'Stock_Cover : The number of days until a product will be out of stock with the predicted sales speed.'
  'Predicted_Sales : Estimated 30-day sale values '
  
  isim= 'Analsed_Data.csv'
  indir = df_analiz_download.to_csv(index=False)
  b64 = base64.b64encode(indir.encode(encoding='ISO-8859-1')).decode(encoding='ISO-8859-1')  # some strings
  linko_final= f'<a href="data:file/csv;base64,{b64}" download={isim}>Download Analysed Data</a>'
  st.markdown(linko_final, unsafe_allow_html=True)  
  
  df_analiz_show= df_analiz[['Product','Category','Sub-Category','Inventory','Label','Stock_Cover', 'Predicted_Sales','Sales21','Sales42','Sales63','Sales84']].copy()
  
  df_analiz_show['Predicted_Sales']= df_analiz_show['Predicted_Sales'].round(0)
  df_analiz_show['Stock_Cover']= df_analiz_show['Stock_Cover'].round(0)
  
  df_analiz_show['Stock_Cover']=df_analiz_show['Stock_Cover'].astype(int)
  df_analiz_show['Predicted_Sales']=df_analiz_show['Predicted_Sales'].astype(int)
  df_analiz_show=df_analiz_show.reset_index(drop=True)
  df_analiz_show2=df_analiz_show.astype(str)
  st.dataframe(df_analiz_show2)
   
  if len(df_sfr)>0:
   st.info('C- Zero Sales') 
   'The table shows the products which have no sales in last 80 days.'
   df_sfr=df_sfr.reset_index(drop=True)
   df_sfr2=df_sfr.astype(str).copy()
   st.dataframe(df_sfr2)   
  #except:
  #'Excel dosya sütunlarını kontrol edin.'


elif yan_sayfa_secenek == 'Easy Inventory Planner' :
 st.title('Easy Inventory Planner')
 
 htp0='https://raw.githubusercontent.com/ozgurdugmeci/easy-app/main/media/model3.jpg'
 #image0 = Image.open(htp6)
 
 metin2= f'<p> It is possible to estimate a stable sales speed by using Easy Inventory Planner. This can be useful for inventory management, production planning, and other business decisions that \
 depend on accurate sales forecasts predictions. </br> </br>  By grouping items based on their sales characteristics and using historical data to estimate future sales, the model can provide\
 valuable insights for demand planning and inventory management. </br> </br> However, it is important to note that demand planning is a complex process that involves many different factors, \
 including market trends, customer behavior, and supply chain disruptions. Therefore it should be regularly reviewed and updated \
 to ensure it remains relevant and accurate and including other variables to the model, such as marketing campaigns, product information, pricing changes, or seasonal trends,\
 that may impact sales can help make it more comprehensive and accurate. </br> </br> 1- Getting data from Snowflake Cloud (Sales and Inventory Quantity Data) </br> \
 2- Model creates labels by analysing sales data for each product. </br> 3- Model makes sales predictions and calculates stock cover days. </p>'
 ' ' 
 st.markdown(metin2,unsafe_allow_html=True) 

 st.image(htp0, caption= 'Model', width=800)

elif yan_sayfa_secenek == 'About Analyses' :
 st.subheader('1- Predictability Analysis')
   

 htp6='https://raw.githubusercontent.com/ozgurdugmeci/easy-app/main/media/predict_resim2.jpg'
 #image6 = Image.open(htp6)
 st.image(htp6, caption= 'Predictability Analysis', width=800)
 
 predicty= f'<p>This is the first analysis that appears on the screen once snowflake data is ready. You can download this report in csv file \
  by clicking download link. Application assigns categories for each product. And for each Label\
  model uses different calculation method to predict sales speed. </br>\
  <b>Predictable Sales : </b> Products in this Label have consistent sales speed in every 20 days of 80 days. Predictability Analysis shows the quality of inventory \
  management. The higher percentage of the "Predictable Sales" ratio indicates the good quality of the inventory management. </br> <b>New Products :</b> \
  Application also detects "New Products". Since these products are in sales for less than 41 days, taking this information into consideration, model calculates  \
  sales speed for each product under this Label. </br> <b>Unpredictable Sales :</b> Marketing activities, product availablity, stock-out situations, customer preference have effect on sales.\
  Because of these reasons some products have inconsistent sales trends in between sales ranges. Model obtains these kind of products and labels them as\
  "Unpredictable Sales".  Yet still model estimates a sales speed for the products in this group. </br> <b>Decreasing Sales :</b> Model detects sales decrease. And it groups \
  these products under "Decreasing Sales" Label. It can be an early warning system to check the inventory quantities and to take the necessary actions. </p>'
  
 st.markdown(predicty,unsafe_allow_html=True)
 
 st.subheader('2- Inventory Planner') 
 

 
 htp7='https://raw.githubusercontent.com/ozgurdugmeci/easy-app/main/media/planner_resim.jpg'

 #htp7='gs://imajo/media/planner_resim.jpg'
 
 #image7 = Image.open(htp7)


 st.image(htp7, caption= 'Inventory Planner', width=800)
 planner= f'<p>This analysis gives the core insights to plan inventory. You can check the <b>"Stock_Cover" </b> values. In other words, it shows the number of days until a product\
  will be out of stock. Thus necessary actions can be taken before a product quantity comes to a critical low level. <b>"Predicted_Sales"</b> is the estimated 20-day \
  sale values.  Analysing these values with the Label information can help you in taking decisions.</p>'
 
 st.markdown(planner,unsafe_allow_html=True)
 st.subheader('3- Zero Sales') 
 'The products have no sales in the last 80 days are listed here. If there are no such products, this analysis does not appear on the screen.'


takip= """
<!-- Default Statcounter code for cem-free-duty
https://demandplanningtool.streamlit.app/ -->
<script type="text/javascript">
var sc_project=12877609; 
var sc_invisible=1; 
var sc_security="e3862e34"; 
</script>
<script type="text/javascript"
src="https://www.statcounter.com/counter/counter.js"
async></script>
<noscript><div class="statcounter"><a title="Web Analytics
Made Easy - Statcounter" href="https://statcounter.com/"
target="_blank"><img class="statcounter"
src="https://c.statcounter.com/12877609/0/e3862e34/1/"
alt="Web Analytics Made Easy - Statcounter"
referrerPolicy="no-referrer-when-downgrade"></a></div></noscript>
<!-- End of Statcounter Code -->
"""
#st.markdown(takip, unsafe_allow_html=True)  
components.html(takip,width=200, height=200)
