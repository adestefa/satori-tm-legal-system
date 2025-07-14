const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto('http://127.0.0.1:8000');
  await page.waitForLoadState();
  
  console.log('Page loaded with NO POLLING - testing pure animation...');
  await page.waitForTimeout(2000);
  
  console.log('Clicking youssef_button with zero polling interference...');
  
  // Execute JavaScript to click the button and observe animation
  const result = await page.evaluate(() => {
    const button = document.getElementById('youssef_button');
    if (button) {
      console.log('Found youssef_button, clicking with NO polling to destroy DOM...');
      button.click();
      return 'Button clicked - NO polling interference';
    } else {
      console.log('Button not found');
      return 'Button not found';
    }
  });
  
  console.log('Result:', result);
  
  // Observe for 15 seconds to see the pure animation
  console.log('Watching for 15 seconds to observe UNINTERRUPTED sequential file processing...');
  await page.waitForTimeout(15000);
  
  console.log('Test complete - animation should have been visible');
  await browser.close();
})();