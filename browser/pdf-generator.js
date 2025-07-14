#!/usr/bin/env node

/**
 * TM Browser PDF Generator PoC
 * 
 * Headless Chromium PDF generation using Puppeteer
 * Designed for Tiger-Monkey legal document processing system
 * 
 * Purpose: Generate court-ready PDFs from HTML files with pixel-perfect accuracy
 * Architecture: Standalone proof-of-concept for eventual container deployment
 */

const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

class PDFGenerator {
    constructor() {
        this.browser = null;
        this.startTime = null;
        this.memoryUsage = null;
    }

    /**
     * Initialize headless browser with optimized settings for legal documents
     */
    async initialize() {
        console.log('🚀 Initializing headless Chromium...');
        this.startTime = Date.now();
        
        this.browser = await puppeteer.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-zygote',
                '--single-process'
            ]
        });

        console.log('✅ Browser initialized successfully');
    }

    /**
     * Generate PDF from HTML file with legal document formatting
     * 
     * @param {string} htmlFilePath - Path to HTML file
     * @param {string} outputPath - Output PDF path  
     * @param {Object} options - PDF generation options
     */
    async generatePDF(htmlFilePath, outputPath, options = {}) {
        if (!this.browser) {
            throw new Error('Browser not initialized. Call initialize() first.');
        }

        const startTime = Date.now();
        console.log(`📄 Processing: ${path.basename(htmlFilePath)}`);

        try {
            // Verify HTML file exists
            await fs.access(htmlFilePath);
            
            // Create new page
            const page = await this.browser.newPage();
            
            // Set viewport for consistent rendering
            await page.setViewport({ 
                width: 1200, 
                height: 1600, 
                deviceScaleFactor: 1 
            });

            // Load HTML file
            const fileUrl = `file://${path.resolve(htmlFilePath)}`;
            await page.goto(fileUrl, { 
                waitUntil: 'networkidle0',
                timeout: 30000 
            });

            // Wait for any dynamic content
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Generate PDF with legal document specifications
            const pdfOptions = {
                path: outputPath,
                format: 'A4',
                printBackground: true,
                margin: {
                    top: '1in',
                    right: '1in', 
                    bottom: '1in',
                    left: '1in'
                },
                displayHeaderFooter: false,
                ...options
            };

            await page.pdf(pdfOptions);
            
            // Get memory usage
            this.memoryUsage = process.memoryUsage();
            
            const processingTime = Date.now() - startTime;
            console.log(`✅ PDF generated: ${outputPath}`);
            console.log(`⏱️  Processing time: ${processingTime}ms`);
            console.log(`💾 Memory usage: ${Math.round(this.memoryUsage.heapUsed / 1024 / 1024)}MB`);

            await page.close();
            
            return {
                success: true,
                outputPath,
                processingTime,
                memoryUsage: this.memoryUsage
            };

        } catch (error) {
            console.error(`❌ Error generating PDF: ${error.message}`);
            throw error;
        }
    }

    /**
     * Process multiple HTML files in batch
     * 
     * @param {string[]} htmlFiles - Array of HTML file paths
     * @param {string} outputDir - Output directory for PDFs
     */
    async batchProcess(htmlFiles, outputDir) {
        const results = [];
        
        // Ensure output directory exists
        await fs.mkdir(outputDir, { recursive: true });

        for (const htmlFile of htmlFiles) {
            const fileName = path.basename(htmlFile, '.html');
            const outputPath = path.join(outputDir, `${fileName}.pdf`);
            
            try {
                const result = await this.generatePDF(htmlFile, outputPath);
                results.push(result);
            } catch (error) {
                results.push({
                    success: false,
                    inputFile: htmlFile,
                    error: error.message
                });
            }
        }

        return results;
    }

    /**
     * Performance analysis and system diagnostics
     */
    getPerformanceMetrics() {
        const uptime = Date.now() - this.startTime;
        const memory = process.memoryUsage();
        
        return {
            uptime,
            memory: {
                rss: Math.round(memory.rss / 1024 / 1024),
                heapTotal: Math.round(memory.heapTotal / 1024 / 1024),
                heapUsed: Math.round(memory.heapUsed / 1024 / 1024),
                external: Math.round(memory.external / 1024 / 1024)
            },
            browserActive: !!this.browser
        };
    }

    /**
     * Clean shutdown
     */
    async close() {
        if (this.browser) {
            await this.browser.close();
            console.log('🔒 Browser closed');
        }
    }
}

/**
 * CLI Interface
 */
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 1) {
        console.log(`
🏛️  TM Browser PDF Generator PoC

Usage:
  node pdf-generator.js <html-file> [output-file]
  node pdf-generator.js --batch <html-dir> <output-dir>
  node pdf-generator.js --test

Examples:
  node pdf-generator.js complaint.html complaint.pdf
  node pdf-generator.js --batch ../outputs/tests/ ./test-outputs/
  node pdf-generator.js --test

Options:
  --batch    Process all HTML files in directory
  --test     Run with sample HTML files from TM system
        `);
        process.exit(1);
    }

    const generator = new PDFGenerator();
    
    try {
        await generator.initialize();

        if (args[0] === '--test') {
            // Test with existing TM HTML files
            const testFiles = [
                '../outputs/tests/Rodriguez/summons/summons_chase_bank_na_(delaware_corporation_authorized_to_do_business_in_new_york).html',
                '../outputs/tests/youssef/summons/summons_equifax_information_services_llc_(georgia_corporation_authorized_to_do_business_in_new_york).html'
            ];
            
            console.log('🧪 Running test with existing TM HTML files...');
            await fs.mkdir('../outputs/browser', { recursive: true });
            
            const results = await generator.batchProcess(testFiles, '../outputs/browser');
            
            console.log('\n📊 Test Results:');
            results.forEach((result, index) => {
                if (result.success) {
                    console.log(`✅ ${testFiles[index]} → ${result.outputPath}`);
                    console.log(`   Time: ${result.processingTime}ms, Memory: ${Math.round(result.memoryUsage.heapUsed / 1024 / 1024)}MB`);
                } else {
                    console.log(`❌ ${result.inputFile}: ${result.error}`);
                }
            });

        } else if (args[0] === '--batch') {
            // Batch processing
            const inputDir = args[1];
            const outputDir = args[2];
            
            if (!inputDir || !outputDir) {
                console.error('❌ Batch mode requires input and output directories');
                process.exit(1);
            }

            const files = await fs.readdir(inputDir);
            const htmlFiles = files
                .filter(file => file.endsWith('.html'))
                .map(file => path.join(inputDir, file));

            if (htmlFiles.length === 0) {
                console.log('⚠️  No HTML files found in directory');
                process.exit(1);
            }

            console.log(`📁 Processing ${htmlFiles.length} HTML files...`);
            const results = await generator.batchProcess(htmlFiles, outputDir);
            
            const successful = results.filter(r => r.success).length;
            console.log(`\n✅ Completed: ${successful}/${results.length} files processed`);

        } else {
            // Single file processing
            const inputFile = args[0];
            const defaultOutputFile = path.join('../outputs/browser', path.basename(inputFile).replace('.html', '.pdf'));
            const outputFile = args[1] || defaultOutputFile;
            
            const result = await generator.generatePDF(inputFile, outputFile);
            
            if (result.success) {
                console.log('\n🎯 Success! PDF generated with pixel-perfect accuracy.');
            }
        }

        // Display performance metrics
        const metrics = generator.getPerformanceMetrics();
        console.log(`\n📈 Performance Metrics:`);
        console.log(`   Uptime: ${metrics.uptime}ms`);
        console.log(`   Memory: ${metrics.memory.heapUsed}MB used / ${metrics.memory.heapTotal}MB total`);

    } catch (error) {
        console.error(`❌ Fatal error: ${error.message}`);
        process.exit(1);
    } finally {
        await generator.close();
    }
}

// Execute if run directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = PDFGenerator;