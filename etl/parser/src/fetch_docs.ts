/**
 * CLI entry point for fetching Marigold UI documentation from GitHub.
 * Downloads MDX files to data/raw directory.
 */
import * as path from 'path';
import { fileURLToPath } from 'url';
import { fetchDocumentation, type FetcherConfig } from './fetcher.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration for Marigold UI docs
const config: FetcherConfig = {
  repoUrl: 'https://github.com/marigold-ui/marigold.git',
  docsPath: 'docs/content/components',
  outputDir: path.resolve(__dirname, '../../data/raw'),
  tempDir: path.resolve(__dirname, '../../.tmp-repo'),
};

try {
  // DEBUG: Log fetch start
  console.log('Fetching documentation...');
  fetchDocumentation(config);

  // DEBUG: Log success
  console.log('Documentation fetched successfully');
} catch (error) {
  console.error('Failed to fetch documentation:', error);
  process.exit(1);
}
