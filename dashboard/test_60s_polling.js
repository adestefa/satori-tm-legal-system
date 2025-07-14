const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto('http://127.0.0.1:8000');
  await page.waitForLoadState();
  
  console.log('Page loaded, waiting for youssef case to be NEW status...');
  await page.waitForTimeout(3000);
  
  console.log('Clicking youssef_button with 60s polling...');
  
  // Execute JavaScript to click the button and observe animation
  const result = await page.evaluate(() => {
    const button = document.getElementById('youssef_button');
    if (button) {
      console.log('Found youssef_button, clicking...');
      button.click();
      return 'Button clicked - observing animation for 10 seconds';
    } else {
      console.log('Button not found');
      return 'Button not found';
    }
  });
  
  console.log('Result:', result);
  
  // Observe for 10 seconds to see the animation
  console.log('Watching for 10 seconds to observe sequential file processing...');
  await page.waitForTimeout(10000);
  
  console.log('Test complete - closing browser');
  await browser.close();
})();