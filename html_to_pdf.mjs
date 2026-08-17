// html_to_pdf.mjs — render a local HTML file to PDF with Chromium.
//
// ⚠️ DEPENDENCY, stated because a script that cannot run where it lives is worse
//    than one in the wrong folder: this needs `playwright` on the module path.
//    It was written inside a sibling repository that already had it installed,
//    and is copied here so the paper's toolchain is complete in one place. Run
//    it from a directory with playwright available, or `npm i playwright` first.
//
// Usage:
//   node html_to_pdf.mjs <input.html> <output.pdf> [--top 20mm --bottom 30mm --side 20mm]
//
// The margins MUST match the @page margins that make_pdf.py wrote into the HTML;
// make_pdf.py prints the exact flags to pass.
//
// Prints the resulting page count so the length claim can be MEASURED rather
// than estimated from a formula. (Every page count in this project until
// 2026-08-17 came from constants I invented; the measured one is 765 words per
// page, not the 600 I had assumed.)
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';
import { readFileSync, statSync } from 'fs';
import path from 'path';

const [, , inFile, outFile] = process.argv;
if (!inFile || !outFile) {
  console.error('usage: node html_to_pdf.mjs <input.html> <output.pdf>');
  process.exit(2);
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.goto(pathToFileURL(path.resolve(inFile)).href, { waitUntil: 'load' });
await page.emulateMedia({ media: 'print' });
await page.waitForTimeout(600);

// ⚠️ These MUST match the @page margins in the HTML, or the absolutely
// positioned page-one footnote lands in the wrong band. make_pdf.py prints the
// values to pass. Defaults follow its --tight preset.
const arg = (n, d) => {
  const i = process.argv.indexOf(n);
  return i > -1 ? process.argv[i + 1] : d;
};
const TOP = arg('--top', '20mm'), BOTTOM = arg('--bottom', '30mm'),
      SIDE = arg('--side', '20mm');

await page.pdf({
  path: outFile,
  format: 'A4',
  printBackground: true,
  margin: { top: TOP, right: SIDE, bottom: BOTTOM, left: SIDE },
  displayHeaderFooter: true,
  headerTemplate: '<span></span>',
  // 🚩 THE FOOTNOTE LIVES HERE, not in the document body.
  //    An absolutely positioned element cannot be placed in a page's bottom
  //    margin: paged CSS gives the flow no access to the margin band, so an
  //    element pushed past the content box simply lands on the NEXT page, and
  //    one placed inside the box has prose flow underneath it. Chromium's
  //    footerTemplate is the only thing that renders into the margin itself.
  //    It repeats on every page, which for a venue attribution is normal and
  //    arguably better than page one alone.
  footerTemplate:
    '<div style="width:100%;font:7.5pt Georgia,serif;color:#555;' +
    'padding:0 20mm;display:flex;justify-content:space-between;' +
    'border-top:0.5px solid #bbb;padding-top:3px;">' +
    '<span>Research conducted at the Digital Minds Research Sprint, August 2026</span>' +
    '<span><span class="pageNumber"></span> / <span class="totalPages"></span></span>' +
    '</div>',
});
await browser.close();

// Count pages from the PDF itself rather than trusting the renderer's word.
const buf = readFileSync(outFile);
const s = buf.toString('latin1');
const counts = [...s.matchAll(/\/Type\s*\/Page[^s]/g)].length;
console.log(`wrote ${outFile}  ${(statSync(outFile).size / 1024).toFixed(0)} KB`);
console.log(`MEASURED page count: ${counts}`);
