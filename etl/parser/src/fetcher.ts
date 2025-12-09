/**
 * Downloads documentation from a Git repository and copies it to output directory.
 * Returns the number of files fetched.
 */
import { rmSync, cpSync, existsSync, readdirSync } from 'fs';
import { join } from 'path';
import { execSync } from 'child_process';

export interface FetcherConfig {
  repoUrl: string;
  docsPath: string;
  outputDir: string;
  tempDir: string;
}

/**
 * Clones a Git repo, extracts specific docs path, and copies to output directory.
 * @returns Number of files fetched
 */
export function fetchDocumentation({
  repoUrl,
  docsPath,
  outputDir,
  tempDir,
}: FetcherConfig): number {
  // Clean temp directory
  rmSync(tempDir, { recursive: true, force: true });

  // Clone repository
  execSync(`git clone --depth 1 "${repoUrl}" "${tempDir}"`, { stdio: 'ignore' });

  // Verify docs path exists
  const src = join(tempDir, docsPath);
  if (!existsSync(src)) throw new Error(`Path not found: ${src}`);

  // Replace output directory with fresh copy
  rmSync(outputDir, { recursive: true, force: true });
  cpSync(src, outputDir, { recursive: true });

  // Cleanup temp directory
  rmSync(tempDir, { recursive: true, force: true });

  // Count files
  return readdirSync(outputDir, { recursive: true, withFileTypes: true }).filter((dirent) =>
    dirent.isFile()
  ).length;
}
