#!/usr/bin/env node
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.HTML_PPT_EDIT_PORT || 8801);
const deckDir = path.resolve(process.env.HTML_PPT_DECK_DIR || process.cwd());
const deckId = process.env.HTML_PPT_DECK_ID || path.basename(deckDir);
const stateFile = path.join(deckDir, 'deck-state.json');
const exportsDir = path.join(deckDir, 'exports');

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.pdf': 'application/pdf',
};

function send(res, status, body, type = 'application/json; charset=utf-8') {
  res.writeHead(status, {
    'Content-Type': type,
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Cache-Control': 'no-store',
  });
  res.end(body);
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function writeJsonAtomic(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp-${Date.now()}`;
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2), 'utf8');
  fs.renameSync(tmp, file);
}

function safeResolve(urlPath) {
  const clean = decodeURIComponent(urlPath.split('?')[0]);
  const rel = clean === '/' ? 'index.html' : clean.replace(/^\/+/, '');
  const file = path.resolve(deckDir, rel);
  if (!file.startsWith(`${deckDir}${path.sep}`) && file !== deckDir) return null;
  return file;
}

function handleSave(req, res) {
  let raw = '';
  req.on('data', chunk => {
    raw += chunk;
    if (raw.length > 100 * 1024 * 1024) req.destroy();
  });
  req.on('end', () => {
    try {
      const payload = JSON.parse(raw || '{}');
      if (payload.deckId && payload.deckId !== deckId) {
        return send(res, 400, JSON.stringify({ ok: false, error: `deckId mismatch: expected ${deckId}` }));
      }
      const state = payload.state;
      if (!state || !Array.isArray(state.slideOrder)) {
        return send(res, 400, JSON.stringify({ ok: false, error: 'missing state.slideOrder' }));
      }
      state.deckId = state.deckId || deckId;
      state.savedBy = 'html-ppt-studio edit-server template';
      state.savedAt = new Date().toISOString();
      state.totalSlides = state.slideOrder.length;
      state.revision = Number(state.revision || 0) + 1;
      writeJsonAtomic(stateFile, state);
      send(res, 200, JSON.stringify({
        ok: true,
        deckId,
        totalSlides: state.totalSlides,
        revision: state.revision,
        stateFile,
        savedAt: state.savedAt,
      }));
    } catch (err) {
      send(res, 500, JSON.stringify({ ok: false, error: String(err && err.message || err) }));
    }
  });
}

function handleState(req, res) {
  try {
    if (!fs.existsSync(stateFile)) {
      return send(res, 404, JSON.stringify({ ok: false, error: 'deck-state.json not found' }));
    }
    send(res, 200, fs.readFileSync(stateFile, 'utf8'));
  } catch (err) {
    send(res, 500, JSON.stringify({ ok: false, error: String(err && err.message || err) }));
  }
}

async function handleExportPdf(req, res) {
  let browser;
  try {
    const { chromium } = require('playwright');
    const { PDFDocument } = require('pdf-lib');
    const state = fs.existsSync(stateFile) ? readJson(stateFile) : null;
    const totalSlides = Number(state?.totalSlides || state?.slideOrder?.length || 0);
    if (!totalSlides) {
      return send(res, 400, JSON.stringify({ ok: false, error: 'no persisted slide state found' }));
    }

    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    await page.goto(`http://127.0.0.1:${PORT}/index.html?mode=audience&export=pdf&v=${Date.now()}`, {
      waitUntil: 'load',
      timeout: 30000,
    });
    await page.waitForTimeout(500);

    const pdf = await PDFDocument.create();
    for (let i = 0; i < totalSlides; i += 1) {
      await page.evaluate(index => {
        if (typeof window.show === 'function') window.show(index);
        document.body.classList.add('audience-mode', 'pdf-export');
      }, i);
      await page.waitForTimeout(250);
      const stage = await page.$('.stage, .deck-stage');
      if (!stage) throw new Error('stage element not found');
      const png = await stage.screenshot({ type: 'png' });
      const image = await pdf.embedPng(png);
      const pdfPage = pdf.addPage([960, 540]);
      pdfPage.drawImage(image, { x: 0, y: 0, width: 960, height: 540 });
    }

    fs.mkdirSync(exportsDir, { recursive: true });
    const filename = `${deckId}-${new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)}.pdf`;
    const file = path.join(exportsDir, filename);
    fs.writeFileSync(file, await pdf.save());
    send(res, 200, JSON.stringify({ ok: true, type: 'screenshot-pdf', totalSlides, filename, url: `/exports/${filename}` }));
  } catch (err) {
    send(res, 500, JSON.stringify({
      ok: false,
      error: String(err && err.message || err),
      hint: 'Install optional dependencies with npm install in templates/edit-server, or remove PDF export from this deck.',
    }));
  } finally {
    if (browser) await browser.close();
  }
}

function serveStatic(req, res) {
  const file = safeResolve(req.url);
  if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
    return send(res, 404, 'Not found', 'text/plain; charset=utf-8');
  }
  const type = mimeTypes[path.extname(file).toLowerCase()] || 'application/octet-stream';
  send(res, 200, fs.readFileSync(file), type);
}

const server = http.createServer((req, res) => {
  if (req.method === 'OPTIONS') return send(res, 204, '');
  const url = new URL(req.url, `http://127.0.0.1:${PORT}`);
  if (req.method === 'GET' && url.pathname === '/api/state') return handleState(req, res);
  if (req.method === 'POST' && url.pathname === '/api/save-state') return handleSave(req, res);
  if (req.method === 'POST' && url.pathname === '/api/export-pdf') return void handleExportPdf(req, res);
  return serveStatic(req, res);
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`html-ppt-studio edit server`);
  console.log(`Deck: ${deckDir}`);
  console.log(`URL: http://127.0.0.1:${PORT}/`);
  console.log(`State: ${stateFile}`);
});
