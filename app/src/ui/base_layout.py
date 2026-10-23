import streamlit as st



def style_background_home():

    st.markdown("""
        <style>

                .stApp {
                    background: #5865F2 !important;
                }

                .stApp div[data-testid="stColumn"]{
                    background-color:#E0E3FF !important;
                    padding:2.5rem !important;
                    border-radius: 5rem !important;
                    }
        </style>  

                """
            ,unsafe_allow_html=True)
    

def style_background_dashboard():

    st.markdown("""
        <style>

                .stApp {
                    background: #E0E3FF !important;
                }

        </style>  

                """
            ,unsafe_allow_html=True)
    

    

def style_base_layout():
# asdasd
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');

                
         /* Hide Streamlit Top Bar, Footer, and Host/Viewer badges */
                
            #MainMenu, footer, header {
                visibility: hidden !important;
                display: none !important;
            }
            
            header[data-testid="stHeader"] {
                visibility: hidden !important;
                display: none !important;
            }

            [data-testid="stDecoration"] {
                visibility: hidden !important;
                display: none !important;
            }

            [data-testid="stStatusWidget"] {
                visibility: hidden !important;
                display: none !important;
            }

            [data-testid="manage-app-button"] {
                visibility: hidden !important;
                display: none !important;
            }

            .viewerBadge_container__1QSob, [class*="viewerBadge"], [class*="manageAppButton"] {
                visibility: hidden !important;
                display: none !important;
            }

            div[data-testid="stToolbar"] {
                visibility: hidden !important;
                display: none !important;
            }

            .stDeployButton {
                visibility: hidden !important;
                display: none !important;
            }

            footer:after {
                content: "" !important;
                visibility: hidden !important;
                display: none !important;
            }
                
            .block-container {
                padding-top:1.5rem !important;    
            }

            h1 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 3.5rem !important;
                line-height:1.1 1important;
                margin-bottom:0rem !important;
            }
                

            h2 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 2rem !important;
                line-height:0.9 !important;
                margin-bottom:0rem !important;
            }
                
            h3, h4, p {
                font-family: 'Outfit', sans-serif;    
            }
                

            button{
                border-radius: 1.5rem !important;
                background-color: #5865F2 !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button[kind="secondary"]{
                border-radius: 1.5rem !important;
                background-color: #EB459E !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button[kind="tertiary"]{
                border-radius: 1.5rem !important;
                background-color: black !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button:hover{
                transform :scale(1.05)}
        </style>  

                """
            ,unsafe_allow_html=True)