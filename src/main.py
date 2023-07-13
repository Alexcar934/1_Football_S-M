import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import plotly.express as px
import plotly.graph_objs as go
import openpyxl

st.set_page_config(page_title = 'Mercado Futbolístico 2022/23', #Nombre de la pagina, sale arriba cuando se carga streamlit
                   page_icon = ':trophy:', # https://www.webfx.com/tools/emoji-cheat-sheet/
                   layout="wide")

st.title(':clipboard: Reporte Estadístico') #Titulo del Dash
st.subheader('Mercado futbolístico actual')
st.markdown('##') #Para separar el titulo de los KPIs, se inserta un paragrafo usando un campo de markdown


archivo_mercado = 'src/Data_Processed/Market_Value.csv'
archivo_stats = 'src/Data_Processed/Stats.csv'

df_market = pd.read_csv(archivo_mercado,index_col=0)
df_market = df_market[df_market['Club_Valor']!='Desconocido']

df_stats = pd.read_csv(archivo_stats,index_col=0)

# st.dataframe(df_market)
# st.markdown('##')
# st.dataframe(df_stats)

pagina_1 = st.container()
pagina_2 = st.container()
pagina_3 = st.container()
pagina_4 = st.container()


# Menú desplegable para seleccionar la página
opcion = st.sidebar.selectbox('Selecciona una página:',
                      ('Página Principal', 'Buscador_MV', 'Dashboard' ,'Conclusiones'))

# INTRODUCCIÓN AL TRABAJO

if opcion == 'Página Principal':
    with pagina_1:
        st.header('Página Principal')
        st.write('Bienvenido a la página 1')




### BUSCADOR DE JUGADORES

elif opcion == 'Buscador_MV':
    with pagina_2:
        st.header('Buscador de jugadores')
        st.write('Bienvenido al buscador de jugadores')


        st.sidebar.subheader("Buscar en la columna 'Nombre'")
        query = st.text_input("Escribe el nombre que quieres buscar", "Lukaku")

        df_market_search = df_market.loc[df_market['Nombre'].str.contains(query)]
        df_stats_search = df_stats.loc[df_stats['Nombre'].str.contains(query)]

        st.write('Búsquedas encontradas:')

        for i in df_market_search.Nombre.unique(): 
            df_market_returned = df_market_search[df_market_search['Nombre'] == i]
            
            for j in df_market_returned['Nombre_id'].unique():
                
                df_market_returned = df_market_search[(df_market_search['Nombre'] == i)&(df_market_search['Nombre_id'] == j)]
                df_stats_returned = df_stats_search[(df_stats_search['Nombre'] == i)&(df_stats_search['Nombre_id'] == j)]
                st.write('<b><h3>',i , '</b></h3>', unsafe_allow_html=True)


                left_column, right_column = st.columns(2)

            ### COLUMNA IZQUIERDA
                with left_column:

                    try:
                        posicion = df_market_returned['Posición'].unique()[0]
                        st.write("<h5> Posición: \t" + posicion +'</h5>', unsafe_allow_html=True)
                    except:
                        st.write('No encuentro el dato de "Posición"')

                    try:
                        edad_actual = str(df_market_returned['Edad'].max())

                        st.write("<h5>Edad actual: \t" + edad_actual +' años </h5>', unsafe_allow_html=True)
                    except:
                        st.write('No encuentro el dato')

                    try:
                        club_actual = df_market_search[((df_market_search['Nombre'] == i)& (df_market_search['Nombre_id'] == j)) &\
                                    ((df_market_search['Año de actualización'] == 2022)|(df_market_search['Año de actualización'] == 2023))]\
                                        ['Club'].unique()[0]
                        
                        st.write("<h5>Club Actual: \t" + club_actual + '</h5>', unsafe_allow_html=True)
                    except:
                        st.write('No encuentro el dato')
                    
                    try:
                        valor_actual = df_market_search[((df_market_search['Nombre'] == i)& (df_market_search['Nombre_id'] == j)) &\
                                    ((df_market_search['Año de actualización'] == 2022)|(df_market_search['Año de actualización'] == 2023))]\
                                        ['Valor de mercado'].unique()[0]
                        
                        st.write("<h5>Valor Actual: \t" + '{:,}'.format(int(valor_actual)).replace(',', '.') + ' € </h5>', unsafe_allow_html=True)
                    except:
                        st.write('No encuentro el dato')


            ### COLUMNA DERECHA

                with right_column:
                    try:
                        valor_max = str(df_market_returned['Valor de mercado'].max())

                        st.write('<h5>Valor máximo de mercado: \t', '{:,}'.format(int(valor_max)).replace(',', '.'), ' €</h5>',unsafe_allow_html=True)
                    except:
                        st.write('No encuentro el dato')

                    try:
                        edad_valor_max = str(df_market_search[(df_market_search['Nombre'] == i)&\
                                        (df_market_search['Valor de mercado'] == df_market_returned\
                                        ['Valor de mercado'].max())]['Edad'].unique()[-1])
                        
                        st.write('<h5>Edad a la que alcanzó el valor máximo: \t', edad_valor_max,
                            ' años </h5>',unsafe_allow_html=True
                                )
                    except:
                        st.write('No encuentro el dato')
                
                temporada = st.sidebar.multiselect(
                "Seleccione el/los años que desees ver reflejados para :" + str(i),
                options = df_market_returned['Temporada'].unique(),
                default = [df_market_returned['Temporada'].unique()[1], df_market_returned['Temporada'].unique().max()])


                df_seleccion = df_market_returned.query("Temporada == @temporada")
                df_seleccion_stats = df_stats_returned.query("Temporada == @temporada")

                try:
                    fig_valor_temporada = px.bar(
                    df_seleccion,
                    x = 'Fecha de actualización',
                    y="Valor de mercado", 
                    orientation= "v", 
                    title = "<b>Valor de mercado</b>", 
                    color_discrete_sequence = ["#FFA500"] * len(df_seleccion),
                    template='plotly_white')


                    fig_valor_temporada.update_layout(
                    plot_bgcolor = "rgba(10,22,135,0)",
                    width = 800,
                    xaxis=(dict(showgrid = False)))
                
                # Crear una nueva columna para asignar los colores
                    df_seleccion['color'] = ['ascendente' if value >= df_seleccion['Diferencia_Valor'].iloc[i-1] else 'descendente'
                         for i, value in enumerate(df_seleccion['Diferencia_Valor'])]

                # Definir la secuencia de colores en función de ascendente o descendente
                    color_discrete_sequence = ['#00FF00' if color == 'ascendente' else '#FF0000'
                           for color in df_seleccion['color']]
                    

                    dif_valor_temporada = px.line(df_seleccion, 
                                                  x='Fecha de actualización', y='Diferencia_Valor',
                                                  title= 'Evolución del Valor de Mercado',
                                                    color_discrete_sequence=color_discrete_sequence
                                        )
                    
                    left_column, right_column = st.columns(2)

                    left_column.plotly_chart(fig_valor_temporada, use_container_width = True)
                    right_column.plotly_chart(dif_valor_temporada, use_container_width = True)
                except:
                    continue
                
                with st.expander("Ver el DataFrame de Valores de Mercado"):
                    st.dataframe(df_seleccion)


                with st.expander("Ver el DataFrame de Estadísticas"):
                    st.dataframe(df_seleccion_stats)

                st.markdown('---')


elif opcion == 'Dashboard':
    with pagina_3:
        st.header('Datos de Mercado y Estadísticas')
        st.write('Filtra los datos que quieres observar')

        st.title('Valores de Mercado')

        #Crear una lista con los parametros de una columna

        valor = df_market['Valor de mercado'].unique().tolist() # se crea una lista unica de la columna CIUDAD
        edad = df_market['Edad'].unique().tolist() # se crea una lista unica de la columna CALIFICACION
        temporada = df_market['Temporada'].unique().tolist() # se crea una lista unica de la columna EDAD PERSONA ENCUESTADA


        #Crear un slider para el Valor

        # valor_selector = st.slider('Edad persona encuestada:',
        #                         min_value = min(valor), #el valor minimo va a ser el valor mas pequeño que encuentre dentro de la columna EDAD PERSONA ENCUESTADA
        #                         max_value = max(valor),#el valor maximo va a ser el valor mas grande que encuentre dentro de la columna EDAD PERSONA ENCUESTADA
        #                         value = (min(valor),max(valor)))
        
        # #Crear un slider de edad

        # edad_selector = st.slider('Edad persona encuestada:',
        #                         min_value = min(edad), #el valor minimo va a ser el valor mas pequeño que encuentre dentro de la columna EDAD PERSONA ENCUESTADA
        #                         max_value = max(edad),#el valor maximo va a ser el valor mas grande que encuentre dentro de la columna EDAD PERSONA ENCUESTADA
        #                         value = (min(edad),max(edad))) #que tome desde el minimo, hasta el maximo


        edad_mínima = st.selectbox('Edad:',
                                     edad)
        
        edad_máxima = st.selectbox('Edad Máxima:',
                                     edad)


        #crear multiselectores

        temporada_selector = st.multiselect('Temporada:',
                                        temporada,
                                        default = 2022)
                                        

        #(df_market['Valor de mercado'].between(*valor_selector))&\
        mask = (df_market['Edad'].between(edad_mínima,(edad_máxima+1)))&\
                (df_market['Temporada'].isin(temporada_selector))
        
        numero_resultados = df_market[mask].shape[0] ##number of availables rows
        st.markdown(f'*Resultados Disponibles:{numero_resultados}*') ## sale como un titulo que dice cuantos resultados tiene para ese filtro

        dif_valor_jugador = px.bar(
        df_market[mask].head(25),
        x = 'Nombre',
        y="Diferencia_Valor", 
        orientation= "v", 
        title = "<b>Aumento del Valor de Mercado </b>", 
        color_discrete_sequence = ["#FFA500"] * len(df_market[mask]),
        template='plotly_white', 
        hover_data= ['Nombre','Temporada','Club_Valor'],
        text= 'Diferencia_Valor')

        st.plotly_chart(dif_valor_jugador,  use_container_width = True)

        with st.expander("Ver el DataFrame"):
                st.dataframe(df_market[mask])


else:
    with pagina_4:
        st.header('Conclusiones')
        st.write('Bienvenido a la página 3')

        df_conclusion1 = pd.DataFrame(df_market.groupby(['Club_Valor', 'Temporada'])['Diferencia_Valor']\
                              .sum()).reset_index().sort_values(by='Diferencia_Valor',ascending=False)
        
        df_conclusion1['Diferencia_Valor_Puntos'] = ['{:,}'.format(int(i)).replace(',', '.') for i in df_conclusion1['Diferencia_Valor']]
        
        temporada = df_conclusion1['Temporada'].unique().tolist()
        
        temporada_selector = st.multiselect('Temporada:',
                                        temporada,
                                        default = 2022)
        
        mask = (df_conclusion1['Temporada'].isin(temporada_selector))

        try:
            dif_valor_equipo = px.bar(
            df_conclusion1[mask].head(30),
            x = 'Club_Valor',
            y="Diferencia_Valor", 
            orientation= "v", 
            title = "<b>Aumento del Valor de Mercado </b>", 
            color_discrete_sequence = ["#FFA500"] * len(df_conclusion1),
            template='plotly_white', 
            hover_data= ['Club_Valor'],
            text= 'Diferencia_Valor_Puntos')

            st.plotly_chart(dif_valor_equipo, use_container_width = True)

            with st.expander("Ver el DataFrame"):
                    st.dataframe(df_conclusion1[mask])


            club = df_conclusion1[mask].head(30)['Club_Valor'].unique().tolist()

            club_selector = st.multiselect('Club:',
                                        club,
                                        default = club[0])

            df_conclusion1_players = pd.DataFrame(df_market.groupby(['Club_Valor', 'Temporada','Nombre'])['Diferencia_Valor']\
                              .sum()).reset_index().sort_values(by='Diferencia_Valor',ascending=False)
            df_conclusion1_players['Diferencia_Valor_Puntos'] = ['{:,}'.format(int(i)).replace(',', '.') for i in df_conclusion1_players['Diferencia_Valor']]

            
            
            mask2 = (df_conclusion1_players['Club_Valor'].isin(club_selector))&\
                (df_conclusion1_players['Temporada'].isin(temporada_selector))

            dif_valor_jugador = px.bar(
            df_conclusion1_players[mask2].head(20),
            x = 'Nombre',
            y="Diferencia_Valor", 
            orientation= "v", 
            title = "<b>Aumento del Valor de Mercado </b>", 
            color_discrete_sequence = ["#FFA500"] * len(df_conclusion1_players),
            template='plotly_white', 
            hover_data= ['Nombre','Temporada','Club_Valor'],
            text= 'Diferencia_Valor_Puntos')

            st.plotly_chart(dif_valor_jugador,  use_container_width = True)

            with st.expander("Ver el DataFrame"):
                    st.dataframe(df_conclusion1_players[mask2])
                



            


            
        
        except:
            st.write('')

        


        

