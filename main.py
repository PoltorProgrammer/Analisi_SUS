import pandas as pd
import numpy as np
import requests
from io import StringIO
import json
from datetime import datetime
import warnings
import os
import sys
warnings.filterwarnings('ignore')

# Validar dependències requerides
PAQUETS_REQUERITS = ['pandas', 'numpy', 'requests']
paquets_que_falten = []

for paquet in PAQUETS_REQUERITS:
    try:
        __import__(paquet)
    except ImportError:
        paquets_que_falten.append(paquet)

if paquets_que_falten:
    print(f"❌ ERROR: Falten els paquets requerits: {', '.join(paquets_que_falten)}")
    print(f"📦 Instal·la amb: pip install {' '.join(paquets_que_falten)}")
    sys.exit(1)

class ExtractorDades:
    """Classe per extreure i validar dades de Google Sheets"""
    
    def __init__(self, url_full=None):
        self.url_full = url_full
        self.dades_mostra = self._obtenir_dades_mostra()
        
    def _obtenir_dades_mostra(self):
        """Dades de mostra quan no es pot accedir a Google Sheets"""
        return {
            'Marca temporal': ['22/05/2025 17:46:26', '22/05/2025 17:46:35', '22/05/2025 17:46:39', '22/05/2025 17:48:55', '22/05/2025 17:49:10', '22/05/2025 17:49:25'],
            'Edat:': ['18 a 23', '24 a 28', '29 a 33', '34 a 39', '18 a 23', '29 a 33'],
            'Familiaritat amb tecnologies digitals:': [4, 5, 3, 2, 4, 3],
            'Has utilitzat abans recursos web de la UAB?': ['SI', 'SI', 'NO', 'NO', 'SI', 'NO'],
            'G01': [5, 5, 5, 5, 4, 3], 'G02': [1, 1, 2, 1, 2, 3], 'G03': [5, 5, 5, 5, 4, 4], 'G04': [1, 2, 1, 1, 2, 2], 'G05': [5, 5, 5, 5, 5, 4],
            'G06': [1, 2, 1, 2, 1, 2], 'G07': [5, 4, 4, 5, 4, 3], 'G08': [2, 1, 1, 1, 2, 3], 'G09': [5, 5, 5, 5, 4, 4], 'G10': [1, 5, 5, 5, 3, 2],
            'M01': [5, 5, 5, 1, 3, 4], 'M02': [1, 1, 1, 5, 3, 2], 'M03': [5, 5, 5, 1, 4, 3], 'M04': [1, 5, 5, 2, 2, 3], 'M05': [5, 1, 5, 5, 4, 4],
            'M06': [1, 5, 1, 1, 3, 2], 'M07': [5, 1, 5, 5, 4, 3], 'M08': [1, 5, 5, 1, 2, 4], 'M09': [5, 1, 5, 5, 4, 4], 'M10': [1, 5, 5, 1, 3, 2]
        }
    
    def extreure_id_full(self, url):
        """Extreure l'ID del Google Sheet de l'URL"""
        if not url:
            return None
        try:
            if '/spreadsheets/d/' in url:
                return url.split('/spreadsheets/d/')[1].split('/')[0]
        except Exception:
            pass
        return None
    
    def obtenir_dades(self):
        """Extreure dades de Google Sheet o usar dades de mostra"""
        print("🔄 Intentant extreure dades de Google Sheets...")
        
        if not self.url_full:
            print("⚠️ No s'ha proporcionat cap URL de Google Sheets")
            return self._usar_dades_mostra()
        
        try:
            id_full = self.extreure_id_full(self.url_full)
            if not id_full:
                raise ValueError("URL de Google Sheet no vàlida")
            
            # Provar diferents mètodes d'extracció
            metodes = [
                f"https://docs.google.com/spreadsheets/d/{id_full}/export?format=csv",
                f"https://docs.google.com/spreadsheets/d/{id_full}/gviz/tq?tqx=out:csv"
            ]
            
            for metode in metodes:
                try:
                    print(f"🔗 Provant: {metode}")
                    resposta = requests.get(metode, timeout=10)
                    if resposta.status_code == 200 and len(resposta.text.strip()) > 0:
                        df = pd.read_csv(StringIO(resposta.text))
                        if len(df) > 0:
                            print(f"✅ Dades extretes correctament: {len(df)} files")
                            return self._validar_i_netejar(df)
                except Exception as e:
                    print(f"⚠️ Mètode fallit: {e}")
                    continue
                    
            raise Exception("No es pot accedir a Google Sheets amb cap mètode")
            
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return self._usar_dades_mostra()
    
    def _usar_dades_mostra(self):
        """Usar dades de mostra quan les dades reals no estan disponibles"""
        print("📋 Usant dades de mostra...")
        df = pd.DataFrame(self.dades_mostra)
        return self._validar_i_netejar(df)
    
    def _validar_i_netejar(self, df):
        """Validar i netejar les dades"""
        print("🧹 Validant i netejant dades...")
        
        if df is None or len(df) == 0:
            raise ValueError("No hi ha dades disponibles")
        
        # Identificar columnes de preguntes SUS
        columnes_galeria = [col for col in df.columns if any(f'G{i:02d}' in str(col) for i in range(1, 11))]
        columnes_mapa = [col for col in df.columns if any(f'M{i:02d}' in str(col) for i in range(1, 11))]
        
        if not columnes_galeria:
            columnes_galeria = [col for col in df.columns if col.startswith('G') and len(col) <= 4]
        if not columnes_mapa:
            columnes_mapa = [col for col in df.columns if col.startswith('M') and len(col) <= 4]
        
        # Ordenar columnes
        try:
            columnes_galeria = sorted(columnes_galeria, key=lambda x: int(''.join(filter(str.isdigit, x))))
            columnes_mapa = sorted(columnes_mapa, key=lambda x: int(''.join(filter(str.isdigit, x))))
        except ValueError:
            print("⚠️ Avís: No s'han pogut ordenar les columnes correctament")
        
        print(f"📊 Columnes Galeria: {columnes_galeria}")
        print(f"🗺️ Columnes Mapa: {columnes_mapa}")
        
        if len(columnes_galeria) != 10:
            print(f"⚠️ Avís: S'esperaven 10 columnes de Galeria, trobades {len(columnes_galeria)}")
        if len(columnes_mapa) != 10:
            print(f"⚠️ Avís: S'esperaven 10 columnes de Mapa, trobades {len(columnes_mapa)}")
        
        # Convertir respostes a numèric i validar rang
        for col in columnes_galeria + columnes_mapa:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Validar rang 1-5
                mascara_valida = (df[col] >= 1) & (df[col] <= 5)
                comptatge_invalid = (~mascara_valida & df[col].notna()).sum()
                if comptatge_invalid > 0:
                    print(f"⚠️ Avís: {comptatge_invalid} valors no vàlids a {col} (fora del rang 1-5)")
                    df.loc[~mascara_valida, col] = np.nan
        
        # Eliminar files amb dades incompletes
        files_inicials = len(df)
        totes_columnes_sus = columnes_galeria + columnes_mapa
        df = df.dropna(subset=totes_columnes_sus)
        files_finals = len(df)
        
        if files_finals == 0:
            raise ValueError("No s'han trobat respostes completes després de la neteja de dades")
        
        if files_inicials != files_finals:
            print(f"🗑️ Eliminades {files_inicials - files_finals} files amb dades incompletes")
        
        print(f"✅ Dades validades: {files_finals} respostes vàlides")
        return df, columnes_galeria, columnes_mapa

class AnalitzadorSUS:
    """Classe per calcular i analitzar puntuacions SUS"""
    
    def __init__(self, df, columnes_galeria, columnes_mapa):
        self.df = df.copy()
        self.columnes_galeria = columnes_galeria
        self.columnes_mapa = columnes_mapa
        self.elements_inversos = [2, 4, 6, 8, 10]  # Elements inversos (base 1)
        
    def calcular_puntuacio_sus(self, respostes, mostrar_calcul=False):
        """Calcular puntuació SUS amb explicació detallada"""
        if len(respostes) != 10:
            return None, None
        
        if pd.isna(respostes).any():
            return None, None
        
        passos_calcul = []
        puntuacio_total = 0
        
        for i, resposta in enumerate(respostes, 1):
            # Assegurar que la resposta està en rang vàlid
            if not (1 <= resposta <= 5):
                return None, None
                
            if i in self.elements_inversos:
                # Elements inversos
                puntuacio_element = 5 - resposta
                passos_calcul.append({
                    'element': i,
                    'tipus': 'Invers',
                    'resposta': resposta,
                    'calcul': f'5 - {resposta} = {puntuacio_element}',
                    'puntuacio': puntuacio_element
                })
            else:
                # Elements normals
                puntuacio_element = resposta - 1
                passos_calcul.append({
                    'element': i,
                    'tipus': 'Normal',
                    'resposta': resposta,
                    'calcul': f'{resposta} - 1 = {puntuacio_element}',
                    'puntuacio': puntuacio_element
                })
            
            puntuacio_total += puntuacio_element
        
        puntuacio_final = puntuacio_total * 2.5
        
        if mostrar_calcul:
            print(f"\n📋 CÀLCUL DETALLAT SUS:")
            print("-" * 50)
            for pas in passos_calcul:
                print(f"Element {pas['element']:2d} ({pas['tipus']:7s}): Resposta={pas['resposta']}, Càlcul={pas['calcul']}, Punts={pas['puntuacio']}")
            print("-" * 50)
            print(f"Suma total: {puntuacio_total}")
            print(f"Puntuació SUS: {puntuacio_total} × 2.5 = {puntuacio_final}")
            print("-" * 50)
        
        return puntuacio_final, passos_calcul
    
    def interpretar_puntuacio(self, puntuacio):
        """Interpretar puntuació SUS segons estàndards acadèmics"""
        if puntuacio >= 90:
            return "A+", "Excel·lent++", "success", "🏆"
        elif puntuacio >= 80:
            return "A", "Excel·lent", "success", "⭐"
        elif puntuacio >= 70:
            return "B", "Bo", "info", "👍"
        elif puntuacio >= 60:
            return "C", "Acceptable", "warning", "⚠️"
        elif puntuacio >= 50:
            return "D", "Deficient", "warning", "👎"
        else:
            return "F", "Inacceptable", "danger", "❌"
    
    def generar_recomanacions(self, puntuacio_galeria, puntuacio_mapa, demografics):
        """Generar recomanacions personalitzades basades en resultats"""
        recomanacions = []
        
        # Anàlisi general
        if puntuacio_galeria >= 80 and puntuacio_mapa >= 80:
            recomanacions.append({
                'tipus': 'success',
                'icona': '🎉',
                'titol': 'Excel·lent Usabilitat Global',
                'missatge': 'Ambdues eines han assolit nivells excel·lents d\'usabilitat.'
            })
        elif puntuacio_galeria >= 70 and puntuacio_mapa >= 70:
            recomanacions.append({
                'tipus': 'info',
                'icona': '✅',
                'titol': 'Bona Usabilitat General',
                'missatge': 'Ambdues eines tenen una usabilitat acceptable a bona.'
            })
        
        # Anàlisi específic d'eines
        if puntuacio_galeria < 70:
            recomanacions.append({
                'tipus': 'warning',
                'icona': '🖼️',
                'titol': 'La Galeria Necessita Millores',
                'missatge': f'La galeria ({puntuacio_galeria:.1f}) requereix millores d\'usabilitat.'
            })
        
        if puntuacio_mapa < 70:
            recomanacions.append({
                'tipus': 'warning',
                'icona': '🗺️',
                'titol': 'El Mapa Necessita Millores',
                'missatge': f'El mapa ({puntuacio_mapa:.1f}) requereix millores de navegació i interacció.'
            })
        
        # Diferència significativa
        diferencia = abs(puntuacio_galeria - puntuacio_mapa)
        if diferencia > 15:
            millor = "Galeria" if puntuacio_galeria > puntuacio_mapa else "Mapa"
            recomanacions.append({
                'tipus': 'info',
                'icona': '⚖️',
                'titol': 'Diferència Significativa',
                'missatge': f'{millor} supera l\'altra eina per {diferencia:.1f} punts. Considera estandarditzar l\'experiència.'
            })
        
        # Recomanacions basades en demografia
        if demografics.get('familiaritat_tec_mitja', 3) < 3:
            recomanacions.append({
                'tipus': 'info',
                'icona': '💡',
                'titol': 'Usuaris amb Baixa Familiaritat Tecnològica',
                'missatge': 'Els usuaris mostren baixa familiaritat tecnològica. Afegeix tutorials i ajudes visuals.'
            })
        
        if demografics.get('experiencia_uab_no', 0) > demografics.get('experiencia_uab_si', 0):
            recomanacions.append({
                'tipus': 'info',
                'icona': '🎓',
                'titol': 'Nous Usuaris UAB',
                'missatge': 'Molts usuaris no han utilitzat recursos web de la UAB. Considera una orientació específica.'
            })
        
        return recomanacions
    
    def analitzar(self):
        """Realitzar anàlisi completa SUS"""
        print("\n🧮 INICIANT ANÀLISI SUS...")
        print("=" * 60)
        
        # Calcular puntuacions individuals
        puntuacions_galeria = []
        puntuacions_mapa = []
        
        for index, fila in self.df.iterrows():
            # Galeria
            respostes_galeria = [fila[col] for col in self.columnes_galeria]
            puntuacio_galeria, calcul_galeria = self.calcular_puntuacio_sus(respostes_galeria)
            puntuacions_galeria.append(puntuacio_galeria)
            
            # Mapa
            respostes_mapa = [fila[col] for col in self.columnes_mapa]
            puntuacio_mapa, calcul_mapa = self.calcular_puntuacio_sus(respostes_mapa)
            puntuacions_mapa.append(puntuacio_mapa)
            
            if index == 0:  # Mostrar càlcul detallat per al primer usuari
                print(f"\n👤 EXEMPLE DE CÀLCUL (Usuari 1):")
                print(f"Respostes Galeria: {respostes_galeria}")
                puntuacio_galeria, _ = self.calcular_puntuacio_sus(respostes_galeria, mostrar_calcul=True)
                
                print(f"\nRespostes Mapa: {respostes_mapa}")
                puntuacio_mapa, _ = self.calcular_puntuacio_sus(respostes_mapa, mostrar_calcul=True)
        
        # Afegir puntuacions al DataFrame
        self.df['SUS_Galeria'] = puntuacions_galeria
        self.df['SUS_Mapa'] = puntuacions_mapa
        
        # Calcular estadístiques
        estadistiques_galeria = self._calcular_estadistiques(puntuacions_galeria, "Galeria")
        estadistiques_mapa = self._calcular_estadistiques(puntuacions_mapa, "Mapa")
        
        # Anàlisi demogràfica
        demografics = self._analitzar_demografia()
        
        # Generar recomanacions
        recomanacions = self.generar_recomanacions(
            estadistiques_galeria['mitjana'] if estadistiques_galeria else 0, 
            estadistiques_mapa['mitjana'] if estadistiques_mapa else 0, 
            demografics
        )
        
        return {
            'galeria': estadistiques_galeria,
            'mapa': estadistiques_mapa,
            'demografia': demografics,
            'recomanacions': recomanacions,
            'dades_en_brut': self.df
        }
    
    def _calcular_estadistiques(self, puntuacions, nom_component):
        """Calcular estadístiques descriptives"""
        puntuacions_valides = [p for p in puntuacions if p is not None]
        
        if not puntuacions_valides:
            print(f"❌ No hi ha puntuacions vàlides per {nom_component}")
            return None
        
        estadistiques = {
            'mitjana': np.mean(puntuacions_valides),
            'mediana': np.median(puntuacions_valides),
            'desviacio_tipica': np.std(puntuacions_valides, ddof=1) if len(puntuacions_valides) > 1 else 0,
            'minim': np.min(puntuacions_valides),
            'maxim': np.max(puntuacions_valides),
            'comptatge': len(puntuacions_valides),
            'puntuacions': puntuacions_valides
        }
        
        # Interpretació
        nota, interpretacio, estat, icona = self.interpretar_puntuacio(estadistiques['mitjana'])
        estadistiques.update({
            'nota': nota,
            'interpretacio': interpretacio,
            'estat': estat,
            'icona': icona
        })
        
        print(f"\n📊 ESTADÍSTIQUES {nom_component.upper()}:")
        print(f"   Mitjana: {estadistiques['mitjana']:.2f} ({interpretacio})")
        print(f"   Mediana: {estadistiques['mediana']:.2f}")
        print(f"   Desv. Típica: {estadistiques['desviacio_tipica']:.2f}")
        print(f"   Rang: {estadistiques['minim']:.1f} - {estadistiques['maxim']:.1f}")
        print(f"   Nota: {nota} {icona}")
        
        return estadistiques
    
    def _analitzar_demografia(self):
        """Analitzar dades demogràfiques"""
        demografia = {
            'total_respostes': len(self.df),
            'familiaritat_tec_mitja': 0,
            'experiencia_uab_si': 0,
            'experiencia_uab_no': 0,
            'distribucio_edat': {},
            'distribucio_tecnologia': {}
        }
        
        # Familiaritat tecnològica
        col_tec = None
        for col in self.df.columns:
            if any(paraula in col.lower() for paraula in ['familiaritat', 'tecnolog', 'technology', 'familiarity']):
                col_tec = col
                break
        
        if col_tec and col_tec in self.df.columns:
            try:
                demografia['familiaritat_tec_mitja'] = float(self.df[col_tec].mean())
                demografia['distribucio_tecnologia'] = self.df[col_tec].value_counts().to_dict()
            except Exception:
                pass
        
        # Experiència UAB
        col_uab = None
        for col in self.df.columns:
            if 'uab' in col.lower():
                col_uab = col
                break
        
        if col_uab and col_uab in self.df.columns:
            try:
                comptatge_uab = self.df[col_uab].value_counts()
                demografia['experiencia_uab_si'] = int(comptatge_uab.get('SI', 0))
                demografia['experiencia_uab_no'] = int(comptatge_uab.get('NO', 0))
            except Exception:
                pass
        
        # Distribució d'edat
        col_edat = None
        for col in self.df.columns:
            if 'edat' in col.lower() or 'age' in col.lower():
                col_edat = col
                break
        
        if col_edat and col_edat in self.df.columns:
            try:
                demografia['distribucio_edat'] = self.df[col_edat].value_counts().to_dict()
            except Exception:
                pass
        
        return demografia

class GeneradorInformeHTML:
    """Classe per generar informes HTML elegants"""
    
    def __init__(self):
        self.colors = {
            'primari': '#2C3E50',
            'secundari': '#34495E', 
            'exit': '#27AE60',
            'avís': '#F39C12',
            'perill': '#E74C3C',
            'info': '#3498DB',
            'galeria': '#8E44AD',
            'mapa': '#E67E22'
        }
    
    def _generar_dades_grafics_demografia(self, demo):
        """Generar dades JavaScript per als gràfics de demografia"""
        # Gràfic d'edats
        edats_data = demo.get('distribucio_edat', {})
        edats_labels = list(edats_data.keys())
        edats_values = list(edats_data.values())
        edats_colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        
        # Gràfic de familiaritat tecnològica
        tech_data = demo.get('distribucio_tecnologia', {})
        tech_labels = [f'Nivell {k}' for k in sorted(tech_data.keys())]
        tech_values = [tech_data[k] for k in sorted(tech_data.keys())]
        tech_colors = ['#FF4444', '#FF8800', '#FFBB33', '#00C851', '#007E33']
        
        # Gràfic d'experiència UAB
        uab_si = demo.get('experiencia_uab_si', 0)
        uab_no = demo.get('experiencia_uab_no', 0)
        uab_labels = ['Amb experiència UAB', 'Sense experiència UAB']
        uab_values = [uab_si, uab_no]
        uab_colors = ['#28a745', '#dc3545']
        
        return {
            'edats': {'labels': edats_labels, 'values': edats_values, 'colors': edats_colors},
            'tecnologia': {'labels': tech_labels, 'values': tech_values, 'colors': tech_colors},
            'uab': {'labels': uab_labels, 'values': uab_values, 'colors': uab_colors}
        }
    
    def _generar_grafic_comparatiu_estadistiques(self, galeria, mapa):
        """Generar dades per al gràfic comparatiu d'estadístiques"""
        return {
            'galeria': {
                'mediana': galeria.get('mediana', 0),
                'desviacio': galeria.get('desviacio_tipica', 0),
                'rang': galeria.get('maxim', 0) - galeria.get('minim', 0)
            },
            'mapa': {
                'mediana': mapa.get('mediana', 0),
                'desviacio': mapa.get('desviacio_tipica', 0),
                'rang': mapa.get('maxim', 0) - mapa.get('minim', 0)
            }
        }
    
    def generar_informe_html(self, resultats, url_base_dades=None):
        """Generar informe HTML complet"""
        
        galeria = resultats.get('galeria', {})
        mapa = resultats.get('mapa', {})
        demo = resultats.get('demografia', {})
        recomanacions = resultats.get('recomanacions', [])
        
        # Gestionar dades mancants amb elegància
        if not galeria or not mapa:
            print("⚠️ Avís: Falten resultats d'anàlisi, generant informe bàsic")
            galeria = galeria or {'mitjana': 0, 'mediana': 0, 'desviacio_tipica': 0, 'minim': 0, 'maxim': 0, 'comptatge': 0, 'nota': 'N/A', 'interpretacio': 'Sense dades', 'estat': 'danger', 'icona': '❌'}
            mapa = mapa or {'mitjana': 0, 'mediana': 0, 'desviacio_tipica': 0, 'minim': 0, 'maxim': 0, 'comptatge': 0, 'nota': 'N/A', 'interpretacio': 'Sense dades', 'estat': 'danger', 'icona': '❌'}
        
        # Generar dades per als gràfics
        dades_demografia = self._generar_dades_grafics_demografia(demo)
        dades_comparatives = self._generar_grafic_comparatiu_estadistiques(galeria, mapa)
        
        # Secció de base de dades
        seccio_base_dades = ""
        if url_base_dades:
            seccio_base_dades = f"""
            <div class="card full-width">
                <div class="card-header">
                    <div class="card-icon">🗄️</div>
                    <div class="card-title">Base de Dades</div>
                </div>
                
                <div style="text-align: center; padding: 20px;">
                    <p style="font-size: 1.1rem; color: #34495E; margin-bottom: 15px;">
                        Les dades analitzades provenen de les següents Fonts:
                    </p>
                    <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                        <a href="{url_base_dades}" target="_blank" class="btn" style="background: linear-gradient(135deg, #0F9D58, #34A853); display: inline-block;">
                            🔗 Veure Base de Dades Original
                        </a>
                        <a href="https://docs.google.com/forms/d/e/1FAIpQLSf-ovmBzQeFW-0ZoAeZ-UtwspY84UZt4y8vBluaQiYTSYq2tA/viewform?usp=sharing&ouid=111166641628531390157"
                            target="_blank" class="btn" style="background: linear-gradient(135deg, #673AB7, #8E24AA); display: inline-block;">
                            📝 Obre el Formulari d’Enquesta
                        </a>
                    </div>
                </div>
            </div>
            """
        
        # Variables JavaScript amb valors reals
        puntuacio_galeria_js = galeria.get('mitjana', 0)
        puntuacio_mapa_js = mapa.get('mitjana', 0)
        
        contingut_html = f"""

<!DOCTYPE html>
<html lang="ca">
<head>
   <meta charset="UTF-8">
   <meta name="viewport" content="width=device-width, initial-scale=1.0">
   <title>Informe SUS - Galeria vs Mapa Botànic</title>
   <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
   <style>
       * {{
           margin: 0;
           padding: 0;
           box-sizing: border-box;
       }}
       
       body {{
           font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
           background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
           color: #333;
           line-height: 1.6;
           min-height: 100vh;
       }}
       
       .container {{
           max-width: 1400px;
           margin: 0 auto;
           padding: 20px;
       }}
       
       .header {{
           background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%);
           color: white;
           text-align: center;
           padding: 40px 20px;
           border-radius: 20px;
           margin-bottom: 30px;
           box-shadow: 0 15px 35px rgba(0,0,0,0.1);
       }}
       
       .header h1 {{
           font-size: 2.5rem;
           margin-bottom: 10px;
           font-weight: 700;
       }}
       
       .header p {{
           font-size: 1.2rem;
           opacity: 0.9;
           margin-bottom: 5px;
       }}
       
       .grid {{
           display: grid;
           grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
           gap: 30px;
           margin-bottom: 30px;
       }}
       
       .card {{
           background: white;
           border-radius: 20px;
           padding: 30px;
           box-shadow: 0 15px 35px rgba(0,0,0,0.08);
           border: 1px solid rgba(255,255,255,0.2);
           backdrop-filter: blur(10px);
           transition: transform 0.3s ease, box-shadow 0.3s ease;
           margin-bottom: 50px;
       }}
       
       .card:hover {{
           transform: translateY(-5px);
           box-shadow: 0 25px 45px rgba(0,0,0,0.15);
       }}
       
       .card-header {{
           display: flex;
           align-items: center;
           margin-bottom: 25px;
           padding-bottom: 15px;
           border-bottom: 2px solid #f8f9fa;
       }}
       
       .card-icon {{
           font-size: 2.5rem;
           margin-right: 15px;
       }}
       
       .card-title {{
           font-size: 1.5rem;
           font-weight: 700;
           color: #2C3E50;
       }}
       
       .metric {{
           display: flex;
           justify-content: space-between;
           align-items: center;
           padding: 15px 0;
           border-bottom: 1px solid #f1f2f6;
       }}
       
       .metric:last-child {{
           border-bottom: none;
       }}
       
       .metric-label {{
           font-weight: 600;
           color: #34495E;
       }}
       
       .metric-value {{
           font-weight: 700;
           font-size: 1.1rem;
       }}
       
       .score-big {{
           text-align: center;
           margin: 20px 0;
       }}
       
       .score-number {{
           font-size: 4rem;
           font-weight: 900;
           margin-bottom: 10px;
           background: linear-gradient(135deg, #8E44AD, #3498DB);
           -webkit-background-clip: text;
           -webkit-text-fill-color: transparent;
       }}
       
       .score-grade {{
           font-size: 1.8rem;
           font-weight: 700;
           margin-bottom: 5px;
       }}
       
       .score-interpretation {{
           font-size: 1.2rem;
           color: #7F8C8D;
           font-style: italic;
       }}
       
       .badge {{
           display: inline-block;
           padding: 8px 16px;
           border-radius: 25px;
           font-weight: 600;
           font-size: 0.9rem;
           text-transform: uppercase;
           letter-spacing: 0.5px;
       }}
       
       .badge-success {{ background: linear-gradient(135deg, #27AE60, #2ECC71); color: white; }}
       .badge-warning {{ background: linear-gradient(135deg, #F39C12, #E67E22); color: white; }}
       .badge-danger {{ background: linear-gradient(135deg, #E74C3C, #C0392B); color: white; }}
       .badge-info {{ background: linear-gradient(135deg, #3498DB, #2980B9); color: white; }}
       
       .recommendation {{
           background: linear-gradient(135deg, #f8f9fa, #ffffff);
           border-left: 5px solid #3498DB;
           padding: 20px;
           margin: 15px 0;
           border-radius: 10px;
           transition: all 0.3s ease;
       }}
       
       .recommendation:hover {{
           transform: translateX(5px);
           box-shadow: 0 5px 15px rgba(0,0,0,0.1);
       }}
       
       .recommendation-header {{
           display: flex;
           align-items: center;
           margin-bottom: 10px;
       }}
       
       .recommendation-icon {{
           font-size: 1.5rem;
           margin-right: 10px;
       }}
       
       .recommendation-title {{
           font-weight: 700;
           color: #2C3E50;
       }}
       
       .recommendation-message {{
           color: #34495E;
           line-height: 1.5;
       }}
       
       .chart-container {{
           position: relative;
           height: 400px;
           margin: 20px 0;
       }}
       
       .chart-container-small {{
           position: relative;
           height: 300px;
           margin: 20px 0;
       }}
       
       .full-width {{
           grid-column: 1 / -1;
       }}
       
       .comparison-container {{
           background: linear-gradient(135deg, #f8f9fa, #ffffff);
           border-radius: 15px;
           padding: 25px;
           margin: 20px 0;
       }}
       
       .vs-indicator {{
           text-align: center;
           font-size: 3rem;
           font-weight: 900;
           color: #E74C3C;
           margin: 20px 0;
       }}
       
       .export-buttons {{
           text-align: center;
           margin: 30px 0;
       }}
       
       .btn {{
           display: inline-block;
           padding: 12px 30px;
           background: linear-gradient(135deg, #3498DB, #2980B9);
           color: white;
           text-decoration: none;
           border-radius: 25px;
           font-weight: 600;
           margin: 0 10px;
           transition: all 0.3s ease;
           border: none;
           cursor: pointer;
       }}
       
       .btn:hover {{
           transform: translateY(-2px);
           box-shadow: 0 10px 25px rgba(52, 152, 219, 0.3);
       }}
       
       .demographic-grid {{
           display: grid;
           grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
           gap: 20px;
           margin: 20px 0;
       }}
       
       .stat-comparison-container {{
           background: linear-gradient(135deg, #e8f5e8, #f0f8f0);
           border-radius: 15px;
           padding: 25px;
           margin: 20px 0;
           position: relative;
           overflow: hidden;
       }}
       
       .stat-comparison-container::before {{
           content: '';
           position: absolute;
           top: 0;
           left: 0;
           right: 0;
           bottom: 0;
           background: linear-gradient(90deg, 
               rgba(220,53,69,0.8) 0%, 
               rgba(255,193,7,0.8) 25%, 
               rgba(255,193,7,0.8) 50%, 
               rgba(40,167,69,0.8) 75%, 
               rgba(40,167,69,0.8) 100%);
           opacity: 0.1;
           z-index: 0;
       }}
       
       .stat-comparison-content {{
           position: relative;
           z-index: 1;
       }}
       
       @media (max-width: 768px) {{
           .grid {{
               grid-template-columns: 1fr;
           }}
           .header h1 {{
               font-size: 2rem;
           }}
           .score-number {{
               font-size: 3rem;
           }}
           .demographic-grid {{
               grid-template-columns: 1fr;
           }}
       }}
   </style>
</head>
<body>
   <div class="container">
       <div class="header">
            <h1>📊 Informe d'Anàlisi SUS</h1>
            <p>Galeria Botànica vs Mapa Botànic</p>
            <p>Generat el {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            <div style="margin-top: 15px;">
                <a href="https://github.com/PoltorProgrammer/Analisi_SUS?tab=readme-ov-file#analitzador-sus" target="_blank" class="btn">
                    🛠️ Veure a GitHub
                </a>
            </div>
       </div>
       
       <!-- Resum Executiu -->
       <div class="card full-width">
           <div class="card-header">
               <div class="card-icon">🎯</div>
               <div class="card-title">Resum Executiu</div>
           </div>
           <div class="comparison-container">
               <div style="display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 20px;">
                   <div style="text-align: center;">
                       <h3>🖼️ Galeria Botànica</h3>
                       <div class="score-big">
                           <div class="score-number">{galeria.get('mitjana', 0):.1f}</div>
                           <div class="score-grade">{galeria.get('nota', 'N/A')} {galeria.get('icona', '')}</div>
                           <div class="score-interpretation">{galeria.get('interpretacio', 'Sense dades')}</div>
                       </div>
                   </div>
                   <div class="vs-indicator">VS</div>
                   <div style="text-align: center;">
                       <h3>🗺️ Mapa Botànic</h3>
                       <div class="score-big">
                           <div class="score-number">{mapa.get('mitjana', 0):.1f}</div>
                           <div class="score-grade">{mapa.get('nota', 'N/A')} {mapa.get('icona', '')}</div>
                           <div class="score-interpretation">{mapa.get('interpretacio', 'Sense dades')}</div>
                       </div>
                   </div>
               </div>
           </div>
       </div>

<!-- Explicació del Mètode SUS -->
        <div class="card full-width">
            <div class="card-header">
                <div class="card-icon">📚</div>
                <div class="card-title">Què és el System Usability Scale (SUS)?</div>
            </div>
            <div style="padding: 20px; background: linear-gradient(135deg, #f8f9fa, #ffffff); border-radius: 15px; margin: 20px 0;">
                <h4 style="color: #2C3E50; margin-bottom: 15px;">📖 Introducció al Mètode</h4>
                <p style="line-height: 1.6; margin-bottom: 15px;">
                    El <strong>System Usability Scale (SUS)</strong> és un qüestionari estandarditzat desenvolupat per John Brooke el 1986 
                    per avaluar la usabilitat percebuda d'un sistema. És una eina àmpliament utilitzada en la investigació d'experiència 
                    d'usuari (UX) i és reconeguda per la seva simplicitat i fiabilitat.
                </p>
                
                <h4 style="color: #2C3E50; margin: 20px 0 15px 0;">🎯 Característiques Clau</h4>
                <ul style="line-height: 1.6; margin-left: 20px;">
                    <li><strong>10 preguntes</strong> amb escala Likert de 5 punts (1=Totalment en desacord, 5=Totalment d'acord)</li>
                    <li><strong>Preguntes alternades</strong>: 5 positives (1, 3, 5, 7, 9) i 5 negatives (2, 4, 6, 8, 10)</li>
                    <li><strong>Puntuació de 0 a 100</strong> que no representa un percentatge sinó una escala de usabilitat</li>
                    <li><strong>Ràpid i econòmic</strong>: es pot completar en 2-3 minuts</li>
                </ul>

                <h4 style="color: #2C3E50; margin: 20px 0 15px 0;">🔢 Interpretació de Puntuacions</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 15px 0;">
                    <div style="background: #dc3545; color: white; padding: 10px; border-radius: 8px; text-align: center;">
                        <strong>0-50</strong><br>Inacceptable ❌
                    </div>
                    <div style="background: #ffc107; color: #212529; padding: 10px; border-radius: 8px; text-align: center;">
                        <strong>50-68</strong><br>Acceptable ⚠️
                    </div>
                    <div style="background: #17a2b8; color: white; padding: 10px; border-radius: 8px; text-align: center;">
                        <strong>68-80</strong><br>Bo 👍
                    </div>
                    <div style="background: #28a745; color: white; padding: 10px; border-radius: 8px; text-align: center;">
                        <strong>80-100</strong><br>Excel·lent ⭐
                    </div>
                </div>
            </div>
        </div>

        <!-- Càlcul Detallat del SUS -->
        <div class="card full-width">
            <div class="card-header">
                <div class="card-icon">🧮</div>
                <div class="card-title">Com es Calcula la Puntuació SUS?</div>
            </div>
            <div style="padding: 20px; background: linear-gradient(135deg, #e8f4fd, #ffffff); border-radius: 15px; margin: 20px 0;">
                <h4 style="color: #2C3E50; margin-bottom: 15px;">📝 Procés de Càlcul Pas a Pas</h4>
                
                <div style="background: #fff; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #3498DB;">
                    <h5 style="color: #2C3E50;">1️⃣ Transformació de Respostes</h5>
                    <p><strong>Preguntes positives (1, 3, 5, 7, 9):</strong> Puntuació = Resposta - 1</p>
                    <p><strong>Preguntes negatives (2, 4, 6, 8, 10):</strong> Puntuació = 5 - Resposta</p>
                    <p style="font-style: italic; color: #7F8C8D;">Aquesta transformació converteix totes les respostes en una escala de 0-4 punts.</p>
                </div>

                <div style="background: #fff; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #E67E22;">
                    <h5 style="color: #2C3E50;">2️⃣ Suma Total</h5>
                    <p>S'afegeixen totes les puntuacions transformades (rang: 0-40 punts)</p>
                </div>

                <div style="background: #fff; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 4px solid #27AE60;">
                    <h5 style="color: #2C3E50;">3️⃣ Escalatge Final</h5>
                    <p><strong>Puntuació SUS = Suma Total × 2.5</strong></p>
                    <p style="font-style: italic; color: #7F8C8D;">Això converteix el rang 0-40 en una escala de 0-100 punts.</p>
                </div>

                <h4 style="color: #2C3E50; margin: 20px 0 15px 0;">💡 Exemple Pràctic</h4>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; font-family: monospace;">
                    <p><strong>Respostes d'un usuari:</strong> [4, 2, 5, 1, 4, 2, 5, 1, 4, 2]</p>
                    <br>
                    <p><strong>Transformacions:</strong></p>
                    <p>P1 (positiva): 4 - 1 = 3</p>
                    <p>P2 (negativa): 5 - 2 = 3</p>
                    <p>P3 (positiva): 5 - 1 = 4</p>
                    <p>P4 (negativa): 5 - 1 = 4</p>
                    <p>... i així successivament</p>
                    <br>
                    <p><strong>Suma total:</strong> 30 punts</p>
                    <p><strong>Puntuació SUS:</strong> 30 × 2.5 = <span style="color: #E67E22; font-weight: bold;">75 punts</span> (Bo 👍)</p>
                </div>
            </div>
        </div>

        <!-- Comentat: Gràfic de comparació principal
        <div class="card full-width">
            <div class="card-header">
                <div class="card-icon">📊</div>
                <div class="card-title">Comparació de Puntuacions SUS</div>
            </div>
            <div class="chart-container">
                <canvas id="susChart"></canvas>
            </div>
        </div>
        -->

       <!-- Estadístiques Detallades -->
       <div class="grid">
           <!-- Galeria Stats -->
           <div class="card">
               <div class="card-header">
                   <div class="card-icon">🖼️</div>
                   <div class="card-title">Galeria Botànica</div>
               </div>
               <div class="metric">
                   <span class="metric-label">Puntuació Mitjana</span>
                   <span class="metric-value">{galeria.get('mitjana', 0):.2f}</span>
               </div>
               <div class="metric">
                   <span class="metric-label">Mediana</span>
                   <span class="metric-value">{galeria.get('mediana', 0):.2f}</span>
               </div>
               <div class="metric">
                   <span class="metric-label">Desviació Típica</span>
                   <span class="metric-value">{galeria.get('desviacio_tipica', 0):.2f}</span>
               </div>
               <div class="metric">
                   <span class="metric-label">Rang</span>
                   <span class="metric-value">{galeria.get('minim', 0):.1f} - {galeria.get('maxim', 0):.1f}</span>
               </div>
               <div class="metric">
                   <span class="metric-label">Qualificació</span>
                   <span class="badge badge-{galeria.get('estat', 'info')}">{galeria.get('nota', 'N/A')}</span>
               </div>
           </div>

           <!-- Mapa Stats -->
           <div class="card">
               <div class="card-header">
                   <div class="card-icon">🗺️</div>
                   <div class="card-title">Mapa Botànic</div>
               </div>
               <div class="metric">
                   <span class="metric-label">Puntuació Mitjana</span>
                   <span class="metric-value">{mapa.get('mitjana', 0):.2f}</span>
               </div>
               <div class="metric">
                   <span class="metric-label">Mediana</span>
                   <span class="metric-value">{mapa.get('mediana', 0):.2f}</span>
               </div>
               <div class="metric">
                   <span class="metric-label">Desviació Típica</span>
                   <span class="metric-value">{mapa.get('desviacio_tipica', 0):.2f}</span>
               </div>
               <div class="metric">
                   <span class="metric-label">Rang</span>
                   <span class="metric-value">{mapa.get('minim', 0):.1f} - {mapa.get('maxim', 0):.1f}</span>
               </div>
               <div class="metric">
                   <span class="metric-label">Qualificació</span>
                   <span class="badge badge-{mapa.get('estat', 'info')}">{mapa.get('nota', 'N/A')}</span>
               </div>
           </div>
       </div>

       <!-- Anàlisi Comparativa Avançada -->
       <div class="card full-width">
           <div class="card-header">
               <div class="card-icon">⚖️</div>
               <div class="card-title">Anàlisi Comparativa d'Estadístiques</div>
           </div>
           <div class="stat-comparison-container">
               <div class="stat-comparison-content">
                   <div class="chart-container">
                       <canvas id="statsComparisonChart"></canvas>
                   </div>
               </div>
           </div>
       </div>

       <!-- Demografia -->
       <div class="card full-width">
           <div class="card-header">
               <div class="card-icon">👥</div>
               <div class="card-title">Perfil Demogràfic dels Participants</div>
           </div>
           <div class="demographic-grid">
               <div class="chart-container-small">
                   <h4 style="text-align: center; margin-bottom: 15px;">Distribució per Edat 👨🏻‍👧🏻</h4>
                   <canvas id="edatChart"></canvas>
               </div>
               <div class="chart-container-small">
                   <h4 style="text-align: center; margin-bottom: 15px;">Familiaritat Tecnològica 💻</h4>
                   <canvas id="tecnologiaChart"></canvas>
               </div>
               <div class="chart-container-small">
                   <h4 style="text-align: center; margin-bottom: 15px;">Experiència UAB 🎓</h4>
                   <canvas id="uabChart"></canvas>
               </div>
           </div>
           <div style="text-align: center; margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
               <h4>📈 Resum Demogràfic</h4>
               <p><strong>Total de participants:</strong> {demo.get('total_respostes', 0)}</p>
               <p><strong>Familiaritat tecnològica mitjana:</strong> {demo.get('familiaritat_tec_mitja', 0):.1f}/5</p>
               <p><strong>Amb experiència UAB:</strong> {demo.get('experiencia_uab_si', 0)} | <strong>Sense experiència:</strong> {demo.get('experiencia_uab_no', 0)}</p>
           </div>
       </div>

       <!-- Recomanacions -->
       <div class="card full-width">
           <div class="card-header">
               <div class="card-icon">💡</div>
               <div class="card-title">Recomanacions i Pròxims Passos</div>
           </div>
           {self._generar_recomanacions_html(recomanacions)}
       </div>

       {seccio_base_dades}

       <!-- Botons d'Exportació -->
       <div class="export-buttons">
           <button onclick="exportToJSON()" class="btn">📄 Exportar JSON</button>
           <button onclick="exportToCSV()" class="btn">📊 Exportar CSV</button>
       </div>
</div>
   </div>

   <script>
       // Dades del gràfic
       const puntuacioGaleria = {puntuacio_galeria_js:.1f};
       const puntuacioMapa = {puntuacio_mapa_js:.1f};
       
       // Dades demogràfiques
       const dadesEdat = {json.dumps(dades_demografia['edats'])};
       const dadesTecnologia = {json.dumps(dades_demografia['tecnologia'])};
       const dadesUab = {json.dumps(dades_demografia['uab'])};
       
       // Dades estadístiques comparatives
       const dadesComparatives = {json.dumps(dades_comparatives)};
       
       // Configuració del gràfic
       Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
       Chart.defaults.font.size = 12;
       
       // Gràfic de comparació SUS
       if (document.getElementById('susChart')) {{
           new Chart(document.getElementById('susChart'), {{
               type: 'bar',
               data: {{
                   labels: ['🖼️ Galeria Botànica', '🗺️ Mapa Botànic'],
                   datasets: [{{
                       label: 'Puntuació SUS',
                       data: [puntuacioGaleria, puntuacioMapa],
                       backgroundColor: [
                           'rgba(142, 68, 173, 0.8)',
                           'rgba(230, 126, 34, 0.8)'
                       ],
                       borderColor: [
                           'rgba(142, 68, 173, 1)',
                           'rgba(230, 126, 34, 1)'
                       ],
                       borderWidth: 3,
                       borderRadius: 15
                   }}]
               }},
               options: {{
                   responsive: true,
                   maintainAspectRatio: false,
                   scales: {{
                       y: {{
                           beginAtZero: true,
                           max: 100,
                           ticks: {{
                               callback: function(value) {{
                                   return value + ' pts';
                               }}
                           }}
                       }}
                   }},
                   plugins: {{
                       legend: {{
                           display: false
                       }},
                       tooltip: {{
                           callbacks: {{
                               label: function(context) {{
                                   const percentage = ((context.parsed.y / 100) * 100).toFixed(1);
                                   return context.label + ': ' + context.parsed.y + ' pts (' + percentage + '%)';
                               }}
                           }}
                       }}
                   }}
               }}
           }});
       }}
       
       // Gràfic comparatiu d'estadístiques amb fons de colors
       if (document.getElementById('statsComparisonChart')) {{
           new Chart(document.getElementById('statsComparisonChart'), {{
               type: 'radar',
               data: {{
                   labels: ['Mediana', 'Desviació Típica', 'Rang'],
                   datasets: [{{
                       label: '🖼️ Galeria',
                       data: [
                           dadesComparatives.galeria.mediana,
                           dadesComparatives.galeria.desviacio,
                           dadesComparatives.galeria.rang
                       ],
                       borderColor: 'rgba(142, 68, 173, 1)',
                       backgroundColor: 'rgba(142, 68, 173, 0.2)',
                       borderWidth: 3,
                       pointBackgroundColor: 'rgba(142, 68, 173, 1)',
                       pointBorderColor: '#fff',
                       pointBorderWidth: 2,
                       pointRadius: 6
                   }}, {{
                       label: '🗺️ Mapa',
                       data: [
                           dadesComparatives.mapa.mediana,
                           dadesComparatives.mapa.desviacio,
                           dadesComparatives.mapa.rang
                       ],
                       borderColor: 'rgba(230, 126, 34, 1)',
                       backgroundColor: 'rgba(230, 126, 34, 0.2)',
                       borderWidth: 3,
                       pointBackgroundColor: 'rgba(230, 126, 34, 1)',
                       pointBorderColor: '#fff',
                       pointBorderWidth: 2,
                       pointRadius: 6
                   }}]
               }},
               options: {{
                   responsive: true,
                   maintainAspectRatio: false,
                   scales: {{
                       r: {{
                           beginAtZero: true,
                           max: 100,
                           ticks: {{
                               stepSize: 20,
                               callback: function(value) {{
                                   if (value <= 50) return value + ' (Inacceptable)';
                                   if (value <= 68) return value + ' (Acceptable)';
                                   return value + ' (Bo/Excel·lent)';
                               }}
                           }},
                           grid: {{
                               color: function(context) {{
                                   const value = context.tick.value;
                                   if (value <= 50) return 'rgba(220, 53, 69, 0.3)';
                                   if (value <= 68) return 'rgba(255, 193, 7, 0.3)';
                                   return 'rgba(40, 167, 69, 0.3)';
                               }}
                           }},
                           angleLines: {{
                               color: 'rgba(0, 0, 0, 0.1)'
                           }}
                       }}
                   }},
                   plugins: {{
                       legend: {{
                           position: 'top',
                           labels: {{
                               padding: 20,
                               usePointStyle: true
                           }}
                       }},
                       tooltip: {{
                           callbacks: {{
                               label: function(context) {{
                                   return context.dataset.label + ': ' + context.parsed.r.toFixed(1);
                               }}
                           }}
                       }}
                   }}
               }}
           }});
       }}
       
       // Gràfic de formatge per edat
       if (document.getElementById('edatChart') && dadesEdat.values.length > 0) {{
           new Chart(document.getElementById('edatChart'), {{
               type: 'pie',
               data: {{
                   labels: dadesEdat.labels,
                   datasets: [{{
                       data: dadesEdat.values,
                       backgroundColor: dadesEdat.colors,
                       borderWidth: 2,
                       borderColor: '#fff'
                   }}]
               }},
               options: {{
                   responsive: true,
                   maintainAspectRatio: false,
                   plugins: {{
                       legend: {{
                           position: 'bottom',
                           labels: {{
                               padding: 20,
                               usePointStyle: true
                           }}
                       }},
                       tooltip: {{
                           callbacks: {{
                               label: function(context) {{
                                   const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                   const percentage = ((context.parsed * 100) / total).toFixed(1);
                                   return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                               }}
                           }}
                       }}
                   }}
               }}
           }});
       }}
       
       // Gràfic de formatge per familiaritat tecnològica
       if (document.getElementById('tecnologiaChart') && dadesTecnologia.values.length > 0) {{
           new Chart(document.getElementById('tecnologiaChart'), {{
               type: 'pie',
               data: {{
                   labels: dadesTecnologia.labels,
                   datasets: [{{
                       data: dadesTecnologia.values,
                       backgroundColor: dadesTecnologia.colors,
                       borderWidth: 2,
                       borderColor: '#fff'
                   }}]
               }},
               options: {{
                   responsive: true,
                   maintainAspectRatio: false,
                   plugins: {{
                       legend: {{
                           position: 'bottom',
                           labels: {{
                               padding: 20,
                               usePointStyle: true
                           }}
                       }},
                       tooltip: {{
                           callbacks: {{
                               label: function(context) {{
                                   const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                   const percentage = ((context.parsed * 100) / total).toFixed(1);
                                   return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                               }}
                           }}
                       }}
                   }}
               }}
           }});
       }}
       
       // Gràfic de formatge per experiència UAB
       if (document.getElementById('uabChart') && dadesUab.values.length > 0) {{
           new Chart(document.getElementById('uabChart'), {{
               type: 'pie',
               data: {{
                   labels: dadesUab.labels,
                   datasets: [{{
                       data: dadesUab.values,
                       backgroundColor: dadesUab.colors,
                       borderWidth: 2,
                       borderColor: '#fff'
                   }}]
               }},
               options: {{
                   responsive: true,
                   maintainAspectRatio: false,
                   plugins: {{
                       legend: {{
                           position: 'bottom',
                           labels: {{
                               padding: 20,
                               usePointStyle: true
                           }}
                       }},
                       tooltip: {{
                           callbacks: {{
                               label: function(context) {{
                                   const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                   const percentage = ((context.parsed * 100) / total).toFixed(1);
                                   return context.label + ': ' + context.parsed + ' (' + percentage + '%)';
                               }}
                           }}
                       }}
                   }}
               }}
           }});
       }}
       
       // Funcions d'exportació
       function exportToJSON() {{
           const dades = {{
               galeria: {json.dumps(galeria, default=str)},
               mapa: {json.dumps(mapa, default=str)},
               demografia: {json.dumps(demo, default=str)},
               generat_el: new Date().toISOString()
           }};
           
           const blob = new Blob([JSON.stringify(dades, null, 2)], {{type: 'application/json'}});
           const url = URL.createObjectURL(blob);
           const a = document.createElement('a');
           a.href = url;
           a.download = 'informe_sus.json';
           a.click();
           URL.revokeObjectURL(url);
       }}
       
       function exportToCSV() {{
           const contingutCSV = "data:text/csv;charset=utf-8," +
               "Eina,Puntuació SUS,Interpretació,Nota\\n" +
               "Galeria Botànica,{galeria.get('mitjana', 0):.1f},{galeria.get('interpretacio', 'Sense dades')},{galeria.get('nota', 'N/A')}\\n" +
               "Mapa Botànic,{mapa.get('mitjana', 0):.1f},{mapa.get('interpretacio', 'Sense dades')},{mapa.get('nota', 'N/A')}";
           
           const uriCodificat = encodeURI(contingutCSV);
           const enllaç = document.createElement("a");
           enllaç.setAttribute("href", uriCodificat);
           enllaç.setAttribute("download", "informe_sus.csv");
           enllaç.click();
       }}
       
       // Animacions d'entrada
       window.addEventListener('load', function() {{
           const cartes = document.querySelectorAll('.card');
           cartes.forEach((carta, index) => {{
               carta.style.opacity = '0';
               carta.style.transform = 'translateY(20px)';
               setTimeout(() => {{
                   carta.style.transition = 'all 0.6s ease';
                   carta.style.opacity = '1';
                   carta.style.transform = 'translateY(0)';
               }}, index * 100);
           }});
       }});
   </script>
</body>
</html>
        """
       
        return contingut_html
   
    def _generar_recomanacions_html(self, recomanacions):
       """Generar HTML per recomanacions"""
       if not recomanacions:
           return "<p>No hi ha recomanacions específiques disponibles.</p>"
       
       html = ""
       for rec in recomanacions:
           color_classe = {
               'success': '#27AE60',
               'warning': '#F39C12', 
               'danger': '#E74C3C',
               'info': '#3498DB'
           }.get(rec.get('tipus', 'info'), '#3498DB')
           
           html += f"""
           <div class="recommendation" style="border-left-color: {color_classe};">
               <div class="recommendation-header">
                   <div class="recommendation-icon">{rec.get('icona', '💡')}</div>
                   <div class="recommendation-title">{rec.get('titol', 'Recomanació')}</div>
               </div>
               <div class="recommendation-message">{rec.get('missatge', 'No hi ha missatge disponible')}</div>
           </div>
           """
       
       return html

def main():
   """Funció principal del sistema d'anàlisi SUS"""
   
   print("🚀 SISTEMA D'ANÀLISI SUS - GALERIA vs MAPA BOTÀNIC")
   print("=" * 60)
   
   # URL per defecte de Google Sheet - es pot canviar aquí
   url_full_defecte = "https://docs.google.com/spreadsheets/d/1HRiTEf8T8RSsMsaZESj56y-9GuxvvFtM8iO7qmVdFCQ/edit?usp=sharing"
   
   # Permetre entrada d'URL personalitzada
   # url_personalitzat = input(f"📝 Introdueix URL de Google Sheets (o prem Enter per usar per defecte): ").strip()
   url_personalitzat = "https://docs.google.com/spreadsheets/d/1HRiTEf8T8RSsMsaZESj56y-9GuxvvFtM8iO7qmVdFCQ/edit?usp=sharing"
   url_full = url_personalitzat if url_personalitzat else url_full_defecte
   
   try:
       # 1. Extracció de dades
       print("\n📥 FASE 1: EXTRACCIÓ DE DADES")
       print("-" * 40)
       extractor = ExtractorDades(url_full)
       df, columnes_galeria, columnes_mapa = extractor.obtenir_dades()
       
       # 2. Anàlisi SUS
       print("\n🧮 FASE 2: ANÀLISI SUS")
       print("-" * 40)
       analitzador = AnalitzadorSUS(df, columnes_galeria, columnes_mapa)
       resultats = analitzador.analitzar()
       
       # 3. Generació d'informe HTML
       print("\n🎨 FASE 3: GENERACIÓ D'INFORME HTML")
       print("-" * 40)
       generador_html = GeneradorInformeHTML()
       contingut_html = generador_html.generar_informe_html(resultats, url_full)
       
       # 4. Guardar informe
       nom_fitxer_informe = 'informe_sus.html'
       with open(nom_fitxer_informe, 'w', encoding='utf-8') as f:
           f.write(contingut_html)
       
       # 5. Exportar resultats
       print("\n💾 FASE 4: EXPORTANT RESULTATS")
       print("-" * 40)
       
       # JSON complet
       dades_exportacio = {
           'metadades': {
               'generat_el': datetime.now().isoformat(),
               'metodologia': 'System Usability Scale (SUS)',
               'mida_mostra': resultats['demografia']['total_respostes'],
               'url_full': url_full
           },
           'resultats': resultats
       }
       
       with open('resultats_sus.json', 'w', encoding='utf-8') as f:
           json.dump(dades_exportacio, f, indent=2, ensure_ascii=False, default=str)
       
       # CSV amb dades processades
       df = resultats['dades_en_brut']
       df.to_csv('dades_sus.csv', index=False, encoding='utf-8')
       
       # 6. Resum final
       print("\n🎯 RESUM FINAL:")
       print("=" * 60)
       print(f"✅ Analitzades {resultats['demografia']['total_respostes']} respostes")
       
       if resultats['galeria'] and resultats['mapa']:
           print(f"🖼️ Galeria: {resultats['galeria']['mitjana']:.1f} punts ({resultats['galeria']['interpretacio']})")
           print(f"🗺️ Mapa: {resultats['mapa']['mitjana']:.1f} punts ({resultats['mapa']['interpretacio']})")
           print(f"⚖️ Diferència: {abs(resultats['galeria']['mitjana'] - resultats['mapa']['mitjana']):.1f} punts")
       else:
           print("⚠️ Anàlisi incompleta a causa de problemes amb les dades")
           
       print(f"💡 Recomanacions generades: {len(resultats['recomanacions'])}")
       print("\n📄 Fitxers generats:")
       print(f"   🌐 {nom_fitxer_informe} - Informe visual interactiu")
       print("   📄 resultats_sus.json - Dades completes")
       print("   📊 dades_sus.csv - Dades processades")
       print(f"\n🌐 Obre '{nom_fitxer_informe}' al teu navegador per veure l'informe complet!")
       
       # Opció per obrir l'informe automàticament
       try:
           import webbrowser
           # resposta = input(f"\n❓ Obrir l'informe HTML automàticament? (s/n): ").lower().strip()
           resposta = "si"
           if resposta in ['s', 'si', 'sí', 'y', 'yes']:
               webbrowser.open(nom_fitxer_informe)
               print("🌐 Informe obert al navegador!")
       except Exception:
           print(f"💡 Obre manualment '{nom_fitxer_informe}' al teu navegador")
       
       return resultats
       
   except Exception as e:
       print(f"❌ ERROR CRÍTIC: {e}")
       print("🔧 Comprova l'URL de Google Sheets o la connexió a internet")
       
       # Opció per mode demostració
       # resposta = input("❓ Executar amb dades de mostra per demostració? (s/n): ").lower().strip()
       resposta = "y"
       if resposta in ['s', 'si', 'sí', 'y', 'yes']:
           print("\n🎭 EXECUTANT EN MODE DEMOSTRACIÓ...")
           try:
               extractor = ExtractorDades(None)  # Sense URL = usar dades de mostra
               df, columnes_galeria, columnes_mapa = extractor.obtenir_dades()
               
               analitzador = AnalitzadorSUS(df, columnes_galeria, columnes_mapa)
               resultats_demo = analitzador.analitzar()
               
               generador_html = GeneradorInformeHTML()
               contingut_html = generador_html.generar_informe_html(resultats_demo, url_full)
               
               nom_fitxer_demo = 'informe_sus_demo.html'
               with open(nom_fitxer_demo, 'w', encoding='utf-8') as f:
                   f.write(contingut_html)
               
               print(f"✅ Informe de demostració generat: '{nom_fitxer_demo}'")
               
               try:
                   import webbrowser
                   webbrowser.open(nom_fitxer_demo)
                   print("🌐 Informe de demostració obert al navegador!")
               except:
                   print(f"💡 Obre manualment '{nom_fitxer_demo}' al navegador")
                   
               return resultats_demo
           except Exception as error_demo:
               print(f"❌ El mode demostració també ha fallat: {error_demo}")
       
       return None

if __name__ == "__main__":
   resultats = main()
   
   if resultats:
       print("\n" + "   " + "="*81)
       print("   " + "🎉 ANÀLISI COMPLETADA AMB ÈXIT!")
       print("   " + "="*81)
       
       # Estadístiques ràpides
       if resultats.get('galeria') and resultats.get('mapa'):
           mitjana_galeria = resultats['galeria']['mitjana']
           mitjana_mapa = resultats['mapa']['mitjana']
           diferencia = abs(mitjana_galeria - mitjana_mapa)
           eina_millor = "Galeria" if mitjana_galeria > mitjana_mapa else "Mapa" if mitjana_mapa > mitjana_galeria else "Empat"

           print(f"""
  ╔════════════════════════════════════════════════════════════════════════════════╗
  ║                              RESULTATS FINALS                                  ║
  ╠════════════════════════════════════════════════════════════════════════════════╣
  ║                                                                                ║
  ║  🖼️  GALERIA BOTÀNICA:                                                         ║
  ║      • Puntuació SUS:                                        {mitjana_galeria:>6.1f} punts      ║
  ║      • Interpretació:                                        {resultats['galeria']['interpretacio']:<15}   ║
  ║      • Nota:                                                 {resultats['galeria']['nota']:<9} {resultats['galeria']['icona']}      ║
  ║                                                                                ║
  ║  🗺️  MAPA BOTÀNIC:                                                             ║
  ║      • Puntuació SUS:                                        {mitjana_mapa:>6.1f} punts      ║
  ║      • Interpretació:                                        {resultats['mapa']['interpretacio']:<15}   ║
  ║      • Nota:                                                 {resultats['mapa']['nota']:<9} {resultats['mapa']['icona']}      ║
  ║                                                                                ║
  ║  ⚖️  COMPARACIÓ:                                                               ║
  ║      • Eina millor:                                                  {eina_millor:<0}      ║
  ║      • Diferència:                                           {diferencia:>6.1f} punts      ║
  ║      • Participants:                                                   {resultats['demografia']['total_respostes']:<0}      ║
  ║                                                                                ║
  ╚════════════════════════════════════════════════════════════════════════════════╝
           """)
       
       print("\n✨ Gràcies per utilitzar l'Analitzador Professional SUS!")
   else:
       print("\n❌ L'anàlisi no s'ha pogut completar")
       print("🔧 Si us plau, comprova l'URL de Google Sheets i torna-ho a provar")
