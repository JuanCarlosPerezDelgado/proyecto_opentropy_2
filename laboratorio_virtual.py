import streamlit as st

#Para eliminar caché
st.cache_data.clear()
st.cache_resource.clear()

#Función 
def imagen_360():
    
    #Llamada al servidor donde se encuentra alojado el html con la imagen 
    st.write(f"""
        <div style="width: 100%; height: 1000px;">
            <iframe src="http://localhost:8000/pannellum.html" width="100%" height="100%" style="border: none;"></iframe>
        </div>
        """,unsafe_allow_html=True)

