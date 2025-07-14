const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.goto('http://127.0.0.1:8000');
  await page.waitForLoadState();
  
  console.log('Page loaded, looking for youssef_button...');
  
  // Execute JavaScript to click the button
  const result = await page.evaluate(() => {
    const button = document.getElementById('youssef_button');
    if (button) {
      console.log('Found youssef_button, clicking...');
      button.click();
      return 'Button clicked successfully';
    } else {
      console.log('Button not found');
      return 'Button not found';
    }
  });
  
  console.log('Result:', result);
  
  // Wait a bit to see the animation
  await page.waitForTimeout(8000);
  
  await browser.close();
})();