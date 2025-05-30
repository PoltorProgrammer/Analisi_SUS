const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
  const dir = __dirname;
  const htmlFile = fs.readdirSync(dir).find(f => f.toLowerCase().endsWith('.html'));

  if (!htmlFile) {
    console.error("❌ No s'ha trobat cap fitxer HTML.");
    return;
  }

  const filePath = `file://${path.join(dir, htmlFile)}`;
  const outputPDF = path.join(dir, htmlFile.replace(/\.html?$/i, '.pdf'));

  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.goto(filePath, { waitUntil: 'networkidle0' });

  // Esperar que els gràfics s’hagin carregat (opcional)
  try {
    await page.waitForFunction(() => {
      return window.Chart && Object.keys(Chart.instances).length > 0;
    }, { timeout: 5000 });
  } catch {
    console.warn("⚠️ No s'han detectat gràfics Chart.js o timeout.");
  }

  // Obtenir dimensions totals del contingut
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  const width = 1240; // píxels (aproximadament A4)

  await page.pdf({
    path: outputPDF,
    width: `${width}px`,
    height: `${height}px`,
    printBackground: true
  });

  await browser.close();
  console.log(`✅ PDF infinit generat correctament: ${outputPDF}`);
})();
