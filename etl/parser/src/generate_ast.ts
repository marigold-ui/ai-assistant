/**
 * Parses MDX files from data/raw and converts them to structured JSON.
 * Output goes to data/processed directory.
 */
import { mkdirSync, writeFileSync } from 'fs';
import { basename, join, resolve, dirname } from 'path';
import { glob } from 'glob';
import { fileURLToPath } from 'url';
import { ASTBuilder } from './ast-builder.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const rawDir = resolve(__dirname, '../../data/raw');
const outDir = resolve(__dirname, '../../data/processed');

// Ensure output directory exists
mkdirSync(outDir, { recursive: true });

// Find all MDX files
const files = await glob(`${rawDir}/**/*.mdx`);
if (files.length === 0) throw new Error(`No MDX files found in ${rawDir}`);

const builder = new ASTBuilder();
let successCount = 0;

// Parse each MDX file to JSON
for (const file of files) {
  const filename = basename(file, '.mdx') + '.json';

  try {
    const parsed = builder.parseDocument(file);
    writeFileSync(join(outDir, filename), JSON.stringify(parsed, null, 2));
    successCount++;
  } catch (error) {
    console.warn(`Failed to parse ${filename}:`, error instanceof Error ? error.message : error);
  }
}

console.log(`Processed ${successCount}/${files.length} files`);
