/**
 * Parses MDX documentation files into structured JSON format.
 * Extracts sections, demos, images, and frontmatter metadata.
 */
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkMdx from 'remark-mdx';
import remarkGfm from 'remark-gfm';
import { readFileSync, existsSync } from 'fs';
import { dirname, basename, join } from 'path';
import type { Node } from 'unist';

export interface Section {
  title: string;
  level: number;
  content: string;
  images: Array<{ src: string; alt: string }>;
  demos: string[];
  children: Section[];
}

export interface ParsedDocument {
  component: string;
  metadata: Record<string, string>;
  demos: Array<{ file: string; code: string }>;
  sections: Section[];
}

interface ASTNode extends Node {
  type: string;
  value?: string;
  depth?: number;
  lang?: string;
  children?: ASTNode[];
  name?: string;
  attributes?: Array<{ name: string; value: string }>;
}

type DemoCollection = Array<{ file: string; code: string }>;

/**
 * Builds Abstract Syntax Tree from MDX files using unified/remark.
 */
export class ASTBuilder {
  private processor = unified().use(remarkParse).use(remarkGfm).use(remarkMdx);

  /**
   * Parses an MDX file and returns structured document data.
   */
  parseDocument(filePath: string): ParsedDocument {
    const content = readFileSync(filePath, 'utf-8');
    const mdxDir = dirname(filePath);
    const ast = this.processor.parse(content) as ASTNode;
    const collectedDemos: DemoCollection = [];

    return {
      component: basename(filePath, '.mdx'),
      metadata: this.extractFrontmatter(content),
      demos: collectedDemos,
      sections: this.buildSectionTree(ast.children || [], mdxDir, collectedDemos),
    };
  }

  /**
   * Converts flat AST nodes into hierarchical section tree based on heading levels.
   */
  private buildSectionTree(nodes: ASTNode[], dir: string, demos: DemoCollection): Section[] {
    const sections: Section[] = [];
    const stack: Section[] = [];

    for (const node of nodes) {
      if (node.type === 'heading') {
        const level = node.depth || 1;
        const title = this.serializeNode(node);
        if (level === 1 || title.startsWith('title:')) continue;

        while (stack.length && stack[stack.length - 1]!.level >= level) stack.pop();

        const newSection: Section = {
          title,
          level,
          content: '',
          images: [],
          demos: [],
          children: [],
        };

        (stack.length ? stack[stack.length - 1]!.children : sections).push(newSection);
        stack.push(newSection);
      } else if (stack.length) {
        this.processNode(stack[stack.length - 1]!, node, dir, demos);
      }
    }
    return sections;
  }

  /**
   * Processes individual AST nodes (images, demos, text) and adds to section.
   */
  private processNode(section: Section, node: ASTNode, dir: string, demos: DemoCollection): void {
    if (node.type === 'mdxJsxFlowElement') {
      if (node.name === 'Image') {
        const src = node.attributes?.find((a) => a.name === 'src')?.value;
        if (src) section.images.push({ src, alt: '' });
      } else if (node.name === 'ComponentDemo') {
        const file = node.attributes?.find((a) => a.name === 'file')?.value;
        if (file) {
          const code = this.loadDemoCode(dir, file);
          if (code) {
            section.demos.push(file);
            demos.push({ file, code });
          }
        }
      }
      return;
    }

    const text = this.serializeNode(node).trim();
    if (text) section.content += (section.content ? '\n\n' : '') + text;
  }

  /** Converts AST node to plain text string. */
  private serializeNode(node: ASTNode): string {
    if (node.type === 'code') return `\`\`\`${node.lang || ''}\n${node.value}\n\`\`\``;
    if (node.value) return node.value;
    return (node.children || []).map((c) => this.serializeNode(c)).join('');
  }

  /** Loads demo code from file (checks multiple possible locations). */
  private loadDemoCode(dir: string, file: string): string | null {
    const paths = [join(dir, file), join(dir, 'components', file)];
    for (const p of paths) {
      if (existsSync(p)) return readFileSync(p, 'utf-8');
    }
    return null;
  }

  /** Extracts YAML frontmatter metadata from file content. */
  private extractFrontmatter(content: string): Record<string, string> {
    const match = content.match(/^---\n([\s\S]*?)\n---/);
    if (!match) return {};
    return Object.fromEntries(
      match[1]!
        .split('\n')
        .map((l) => l.split(':').map((s) => s.trim().replace(/^['"]|['"]$/g, '')))
        .filter((p) => p.length === 2)
    );
  }
}
