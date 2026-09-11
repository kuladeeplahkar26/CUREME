import streamlit as st


def apply_styles():
    # Retrieve accessibility settings from session state
    text_size_mode = st.session_state.get("text_size", "Standard")
    contrast_mode = st.session_state.get("contrast", "Standard")

    # Font sizing scale
    if text_size_mode == "Large":
        base_font_size = "20px"
        h1_font_size = "2.85rem"
        h2_font_size = "2.25rem"
        h3_font_size = "1.75rem"
        body_font_size = "1.25rem"
        stat_font_size = "2.5rem"
    else:
        base_font_size = "16px"
        h1_font_size = "2.25rem"
        h2_font_size = "1.75rem"
        h3_font_size = "1.35rem"
        body_font_size = "1.05rem"
        stat_font_size = "2.2rem"

    # Contrast settings
    if contrast_mode == "High":
        bg_color = "#FFFFFF"
        card_bg = "#FFFFFF"
        border_color = "#1F3042"
        text_primary = "#000000"
        text_secondary = "#243238"
        card_shadow = "0 0 0 2px #1F3042"
    else:
        bg_color = "#F7F8F4"
        card_bg = "#FFFFFF"
        border_color = "#DDE5E1"
        text_primary = "#0F1D23"
        text_secondary = "#66757D"
        card_shadow = "0 2px 8px -2px rgba(31, 48, 66, 0.05), 0 1px 3px 0 rgba(31, 48, 66, 0.03)"

    st.markdown(f"""
        <style>
        /* Import Plus Jakarta Sans, Atkinson Hyperlegible Next, and Material Symbols */
        @import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:ital,wght@0,400..700;1,400..700&family=Plus+Jakarta+Sans:ital,wght@0,500;0,600;0,700;1,500;1,600&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');
        
        :root {{
            --primary-dark: #1F3042;
            --dark-navy: #1F3042;
            --secondary-dark: #37485B;
            --primary-green: #176B4D;
            --light-green: #E7F4ED;
            --accent-blue: #4F6074;
            --accent-yellow: #E9A23B;
            --accent-purple: #7B61D9;
            --accent-orange: #845400;
            --bg-color: {bg_color};
            --card-bg: {card_bg};
            --text-primary: {text_primary};
            --text-secondary: {text_secondary};
            --border-color: {border_color};
            --error: #BA1A1A;
            --success: #176B4D;
        }}

        .material-symbols-outlined {{
            font-family: 'Material Symbols Outlined' !important;
            font-weight: normal !important;
            font-style: normal !important;
            font-size: 24px;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            vertical-align: middle;
        }}

        /* Base Typography and Body */
        html, body, [class*="css"], .stApp {{
            font-family: 'Atkinson Hyperlegible Next', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: var(--bg-color) !important;
            color: var(--text-primary) !important;
            font-size: {base_font_size} !important;
            line-height: 1.6 !important;
        }}

        /* Container Sizing */
        .block-container {{
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1350px !important;
            margin: 0 auto !important;
        }}

        /* Headings */
        h1, h2, h3, h4, .apon-title {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: var(--primary-dark) !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }}
        h1 {{
            font-size: {h1_font_size} !important;
            line-height: 1.25 !important;
            margin-bottom: 12px !important;
        }}
        h2 {{
            font-size: {h2_font_size} !important;
            line-height: 1.3 !important;
            margin-bottom: 16px !important;
        }}
        h3 {{
            font-size: {h3_font_size} !important;
            line-height: 1.35 !important;
            margin-bottom: 12px !important;
        }}
        p {{
            color: var(--text-secondary) !important;
            font-size: {body_font_size} !important;
        }}

        /* Clean Restorative Cards */
        .card, .apon-card {{
            background-color: var(--card-bg);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border-color);
            box-shadow: {card_shadow};
            margin-bottom: 20px;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .card:hover, .apon-card:hover {{
            box-shadow: 0 8px 24px -4px rgba(23, 107, 77, 0.08);
            border-color: var(--primary-green);
        }}

        /* Metric / Stat Card */
        .stat-card {{
            background-color: var(--card-bg);
            border-radius: 16px;
            padding: 20px 24px;
            border: 1px solid var(--border-color);
            box-shadow: {card_shadow};
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 120px;
        }}
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            font-weight: 500;
            margin-bottom: 8px;
        }}
        .stat-value {{
            color: var(--primary-dark);
            font-size: {stat_font_size};
            font-weight: 700;
            line-height: 1.1;
            margin-bottom: 4px;
        }}
        .stat-sub {{
            color: var(--primary-green);
            font-size: 0.85rem;
            font-weight: 600;
        }}

        /* Buttons */
        .stButton>button, .btn-primary {{
            background-color: var(--primary-green) !important;
            color: #FFFFFF !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            border: none !important;
            font-weight: 600 !important;
            font-size: {body_font_size} !important;
            min-height: 48px !important;
            transition: background-color 0.15s ease, transform 0.15s ease !important;
            box-shadow: 0 2px 8px rgba(31, 167, 122, 0.2) !important;
        }}
        .stButton>button:hover, .btn-primary:hover {{
            background-color: #188a64 !important;
            transform: translateY(-1px);
        }}

        /* Secondary / Outlined Button */
        .btn-secondary {{
            background-color: transparent !important;
            color: var(--dark-navy) !important;
            border: 1.5px solid var(--border-color) !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            min-height: 48px !important;
        }}
        .btn-secondary:hover {{
            background-color: #ECEFF1 !important;
            border-color: var(--dark-navy) !important;
        }}

        /* Streamlit Input Fields */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {{
            border-radius: 10px !important;
            border: 1px solid var(--border-color) !important;
            padding: 12px 16px !important;
            font-size: {body_font_size} !important;
            background-color: #FFFFFF !important;
            color: var(--text-primary) !important;
        }}
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
            border-color: var(--primary-green) !important;
            box-shadow: 0 0 0 3px rgba(31, 167, 122, 0.2) !important;
        }}

        /* Hide Streamlit default chrome */
        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}
        header[data-testid="stHeader"] {{
            display: none !important;
        }}

        /* Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
        }}
        .badge-green {{
            background-color: var(--light-green);
            color: var(--primary-green);
        }}
        .badge-blue {{
            background-color: #E6F0FA;
            color: var(--accent-blue);
        }}
        .badge-yellow {{
            background-color: #FEF8E7;
            color: #B58A00;
        }}

        /* Responsive Mobile Layout Adjustments */
        @media (max-width: 768px) {{
            .block-container {{
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 1rem !important;
            }}
            h1 {{
                font-size: 1.85rem !important;
            }}
            .stat-value {{
                font-size: 1.8rem !important;
            }}
            .card, .apon-card {{
                padding: 16px !important;
            }}
        }}
        </style>
    """, unsafe_allow_html=True)


def card(content, border_accent=None):
    border_style = f"border-left: 4px solid {border_accent};" if border_accent else ""
    st.markdown(f'<div class="card" style="{border_style}">{content}</div>', unsafe_allow_html=True)
