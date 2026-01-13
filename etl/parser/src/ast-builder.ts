/**
 * Parses MDX documents into structured sections with metadata, demos, and heading hierarchy.
 */
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkMdx from 'remark-mdx';
import remarkGfm from 'remark-gfm';
import { readFileSync, existsSync } from 'fs';
import { dirname, basename, join } from 'path';
import type { Node } from 'unist';

interface ASTNode extends Node {
  type: string;
  value?: string;
  depth?: number;
  children?: ASTNode[];
  name?: string;
  attributes?: Array<{ name: string; value: string }>;
}

export interface Section {
  heading: string;
  level: number;
  content: string;
  path: string[];
  parent?: string;
  demos: string[];
}

export interface ParsedDocument {
  component: string;
  metadata: Record<string, string>;
  demos: Array<{ file: string; code: string }>;
  sections: Section[];
}

const MARKDOWN_PROCESSOR = unified().use(remarkParse).use(remarkGfm).use(remarkMdx);

export class ASTBuilder {
  private readonly processor = MARKDOWN_PROCESSOR;

  parseDocument(filePath: string): ParsedDocument {
    const content = readFileSync(filePath, 'utf-8');
    const ast = this.processor.parse(content) as ASTNode;
    const dir = dirname(filePath);

    const demos: ParsedDocument['demos'] = [];
    const sections: Section[] = [];
    const stack: Array<{ title: string; level: number }> = [];

    let currentContent: string[] = [];
    let currentDemos: string[] = [];
    let currentHeading = '';
    let currentLevel = 0;
    let currentParent: string | undefined;

    for (const node of ast.children || []) {
      if (node.type === 'heading') {
        this.saveSection(
          sections,
          stack,
          currentHeading,
          currentLevel,
          currentContent,
          currentDemos,
          currentParent
        );
        this.updateStack(stack, node.depth || 1);
        currentParent =
          stack.length > 0 && (node.depth || 1) >= 3 ? stack[stack.length - 1]!.title : undefined;
        currentHeading = this.toText(node);
        currentLevel = (node.depth || 1) - 1;
        currentContent = [];
        currentDemos = [];
        continue;
      }

      if (node.type === 'mdxJsxFlowElement' && node.name === 'ComponentDemo') {
        const file = node.attributes?.find((a) => a.name === 'file')?.value;
        if (file) {
          const code = this.loadDemo(dir, file);
          if (code) {
            demos.push({ file, code });
            currentDemos.push(file);
          }
        }
        continue;
      }

      if (node.type === 'mdxJsxFlowElement' && node.name) {
        const jsx = this.extractJSX(node);
        if (jsx) currentContent.push(jsx);
        continue;
      }

      const text = this.toText(node).trim();
      if (text) currentContent.push(text);
    }

    if (currentHeading && currentContent.length > 0) {
      this.saveSection(
        sections,
        stack,
        currentHeading,
        currentLevel,
        currentContent,
        currentDemos,
        currentParent
      );
    }

    return {
      component: basename(filePath, '.mdx'),
      metadata: this.extractFrontmatter(content),
      demos,
      sections,
    };
  }

  private saveSection(
    sections: Section[],
    stack: Array<{ title: string; level: number }>,
    heading: string,
    level: number,
    content: string[],
    demos: string[],
    parent: string | undefined
  ): void {
    if (!heading && content.length === 0) return;
    const section: Section = {
      heading: heading || 'Introduction',
      level,
      content: content.join('\n').trim(),
      path: stack.map((h) => h.title),
      demos,
    };
    if (parent) section.parent = parent;
    sections.push(section);
  }

  private updateStack(stack: Array<{ title: string; level: number }>, headingLevel: number): void {
    const level = headingLevel - 1;
    while (stack.length && stack[stack.length - 1]!.level >= level) stack.pop();
    if (level === 1) stack.length = 0;
  }

  private toText(node: ASTNode): string {
    if (node.value) return node.value;
    return (node.children || [])
      .map((c) => this.toText(c))
      .filter(Boolean)
      .join(' ');
  }

  /**
   * Extracts and formats content from JSX components (GuidelineTiles, Table, Image, etc.)
   */
  private extractJSX(node: ASTNode): string {
    const { name, children = [], attributes = [] } = node;

    if (name === 'GuidelineTiles') {
      return children
        .filter((c) => c.type === 'mdxJsxFlowElement' && ['Do', 'Dont'].includes(c.name || ''))
        .map((child) => {
          const type = child.name!;
          const desc = this.findNode(child, `${type}.Description`);
          const fig = this.findNode(child, `${type}.Figure`);
          if (desc) return `[${type.toUpperCase()}] ${this.toText(desc)}`;
          if (fig) {
            const img = this.findNode(fig, 'Image');
            const alt = img?.attributes?.find((a) => a.name === 'alt')?.value;
            if (alt) return `[${type.toUpperCase()}] ${alt}`;
          }
          return '';
        })
        .filter(Boolean)
        .join('\n');
    }

    if (name === 'SectionMessage') {
      const variant = attributes.find((a) => a.name === 'variant')?.value;
      const title = this.findNode(node, 'SectionMessage.Title');
      const content = this.findNode(node, 'SectionMessage.Content');
      return [
        variant && `[${variant.toUpperCase()}]`,
        title && `${this.toText(title)}:`,
        content && this.toText(content),
      ]
        .filter(Boolean)
        .join(' ');
    }

    if (name === 'Table') {
      const rows: string[] = [];
      const header = this.findNode(node, 'Table.Header');
      const body = this.findNode(node, 'Table.Body');

      if (header) {
        const cols = (header.children || [])
          .filter((c) => c.type === 'mdxJsxFlowElement' && c.name === 'Table.Column')
          .map((c) => this.toText(c).trim());
        if (cols.length) rows.push(cols.join(' | '));
      }

      if (body) {
        (body.children || [])
          .filter((c) => c.type === 'mdxJsxFlowElement' && c.name === 'Table.Row')
          .forEach((row) => {
            const cells = (row.children || [])
              .filter((c) => c.type === 'mdxJsxFlowElement' && c.name === 'Table.Cell')
              .map((c) => this.toText(c).trim());
            if (cells.length) rows.push(cells.join(' | '));
          });
      }

      return rows.join('\n');
    }

    if (name === 'Image') {
      const alt = attributes.find((a) => a.name === 'alt')?.value;
      const src = attributes.find((a) => a.name === 'src')?.value;
      return alt ? `[Image: ${alt}]` : src ? `[Image: ${src}]` : '[Image]';
    }

    const text = this.toText(node).trim();
    return text || `<${name} />`;
  }

  /**
   * Recursively finds a child node by name
   */
  private findNode(node: ASTNode, name: string): ASTNode | undefined {
    if (node.type === 'mdxJsxFlowElement' && node.name === name) return node;
    for (const child of node.children || []) {
      const found = this.findNode(child, name);
      if (found) return found;
    }
  }

  private loadDemo(dir: string, file: string): string | null {
    const paths = [join(dir, file), join(dir, 'components', file)];
    for (const path of paths) {
      if (existsSync(path)) return readFileSync(path, 'utf-8');
    }
    return null;
  }

  /**
   * Parses YAML frontmatter from markdown content
   */
  private extractFrontmatter(content: string): Record<string, string> {
    const match = content.match(/^---\n([\s\S]*?)\n---/);
    if (!match) return {};
    return Object.fromEntries(
      match[1]!
        .split('\n')
        .map((line) => line.split(':').map((s) => s.trim().replace(/^['"]|['"]$/g, '')))
        .filter((parts) => parts.length === 2)
    );
  }
}
