const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function capturePoster() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({
        viewport: { width: 1080, height: 1920 }
    });

    const htmlPath = path.resolve(process.argv[2] || '/root/.openclaw/workspace/poster-2-efficiency.html');
    const outputPath = process.argv[3] || '/root/.openclaw/workspace/poster-2-efficiency.png';
    
    const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
    await page.setContent(htmlContent, { waitUntil: 'networkidle' });
    
    // Wait for fonts and layout
    await page.waitForTimeout(2000);
    
    const poster = await page.$('.poster');
    await poster.screenshot({ 
        path: outputPath,
        type: 'png'
    });
    
    console.log(`✅ 海报已生成: ${outputPath}`);
    await browser.close();
}

capturePoster().catch(console.error);
