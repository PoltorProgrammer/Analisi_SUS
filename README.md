# Analitzador SUS

[![Deploy](https://img.shields.io/badge/🔗%20Veure%20Informe-Live-blue)](https://poltorprogrammer.github.io/Analisi_SUS/informe_sus.html)

Aquest projecte analitza dades de qüestionaris SUS (System Usability Scale) per comparar la Galeria Botànica i el Mapa Botànic de la UAB.

## 🔍 Funcionalitats  
✅ Extracció automàtica de dades des de Google Sheets  
✅ Càlcul i interpretació de puntuacions SUS  
✅ Generació d’un informe HTML interactiu amb gràfics  
✅ Exportació de resultats en format JSON i CSV

## 🚀 Com executar-ho

1️⃣ Clona aquest repositori:
```bash
git clone https://github.com/PoltorProgrammer/Analisi_SUS.git
cd analitzador-sus
```

2️⃣ Instal·la les dependències:
```bash
pip install -r requirements.txt
```

3️⃣ Executa el script principal:
```bash
python main.py
```

4️⃣ Obre l’informe generat (`informe_sus.html`) amb el navegador.

[![Deploy](https://img.shields.io/badge/🔗%20Veure%20Informe-HTML-yellow)](https://poltorprogrammer.github.io/Analisi_SUS/informe_sus.html)

---

## 📊 Què trobaràs a l’informe?

L’informe generat (`informe_sus.html`) inclou:

- 🎯 **Resum Executiu:**  
  Comparació directa entre la Galeria Botànica i el Mapa Botànic amb les puntuacions mitjanes SUS, qualificacions i diferències entre eines.

- 📚 **Què és el SUS?**  
  Explicació detallada del System Usability Scale, amb context, característiques clau i interpretació de les puntuacions.

- 🧮 **Càlcul detallat:**  
  Desglossament del procés de càlcul SUS pas a pas amb exemples pràctics, perquè puguis entendre com es transforma cada resposta.

- 🖼️ **Estadístiques per eina:**  
  Puntuació mitjana, mediana, desviació típica, rang i qualificació per a cada eina (Galeria i Mapa).

- ⚖️ **Anàlisi comparativa:**  
  Gràfics radar per comparar les estadístiques clau entre les dues eines.

- 👥 **Perfil demogràfic:**  
  Gràfics de distribució per edat, familiaritat tecnològica i experiència amb recursos UAB, amb un resum numèric dels participants.

- 💡 **Recomanacions personalitzades:**  
  Accions i suggeriments basats en els resultats i el perfil dels usuaris per millorar l’experiència.

- 🗄️ **Base de dades:**  
  Enllaç directe als Google Sheets i Google Forms originals, amb opcions per exportar les dades en JSON i CSV.

  [![Google Sheets](https://img.shields.io/badge/🔗%20Google%20Sheets-Original-darkgreen)](https://docs.google.com/spreadsheets/d/1HRiTEf8T8RSsMsaZESj56y-9GuxvvFtM8iO7qmVdFCQ/edit?usp=sharing)
  [![Google Forms](https://img.shields.io/badge/🔗%20Google%20Forms-Original-purple)](https://docs.google.com/forms/d/e/1FAIpQLSf-ovmBzQeFW-0ZoAeZ-UtwspY84UZt4y8vBluaQiYTSYq2tA/viewform?usp=sharing)

- 📝 **Formulari d’enquesta:**  
  Accés al formulari original per recollir més respostes o actualitzar les dades.

---

## 🖨️ Conversió a PDF (opcional)

Al repositori trobaràs el fitxer `convert_html_to_pdf.js` que utilitza **Puppeteer** per convertir automàticament l’informe HTML a PDF.

### Com usar-ho:
1️⃣ Assegura’t que tens instal·lat Node.js i Puppeteer:
```bash
npm install puppeteer
```

2️⃣ Executa el script:
```bash
node convert_html_to_pdf.js
```

Aquest script buscarà automàticament el fitxer `.html` al directori i generarà un fitxer `.pdf` amb la mateixa base de nom.

---

## 📦 Requeriments

- Python 3.8+
- Connexió a internet per accedir a Google Sheets

## 💻 Desenvolupament

Si vols contribuir o millorar el projecte:
- Usa un entorn virtual (`python -m venv venv`)
- Usa `requirements-dev.txt` per les dependències de desenvolupament (tests, linting)

## 📄 Llicència

Aquest projecte està sota llicència MIT. Consulta el fitxer `LICENSE` per a més detalls.

## ✨ Autor

Tomás González Bartomeu

Amb la tutoria de **** **** ****

Universitat Autònoma de Barcelona
