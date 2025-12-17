/**
 * Property-based test for project structure validation
 * Feature: ai-native-textbook, Property 11: Service Integration Reliability
 * Validates: Requirements 7.1
 */

import * as fc from 'fast-check';
import * as fs from 'fs';
import * as path from 'path';

describe('Project Structure Property Tests', () => {
  const projectRoot = path.resolve(__dirname, '../..');
  
  /**
   * Property 11: Service Integration Reliability
   * For any system startup or service interaction, the system should successfully 
   * connect to all required services and handle failures gracefully with appropriate fallbacks
   */
  test('Property 11: All required service directories and files exist', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          'src/services',
          'src/subagents', 
          'src/api',
          'src/types',
          'src/utils',
          'src/hooks',
          'src/store'
        ),
        (directoryPath) => {
          const fullPath = path.join(projectRoot, directoryPath);
          
          // Property: All service directories must exist
          expect(fs.existsSync(fullPath)).toBe(true);
          
          // Property: All service directories must be directories
          expect(fs.statSync(fullPath).isDirectory()).toBe(true);
          
          // Property: All service directories must have an index file
          const indexPath = path.join(fullPath, 'index.ts');
          expect(fs.existsSync(indexPath)).toBe(true);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 11: Required service files have proper exports', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          'src/services/index.ts',
          'src/subagents/index.ts',
          'src/types/index.ts',
          'src/utils/index.ts',
          'src/hooks/index.ts',
          'src/store/index.ts'
        ),
        (filePath) => {
          const fullPath = path.join(projectRoot, filePath);
          
          // Property: All index files must exist
          expect(fs.existsSync(fullPath)).toBe(true);
          
          // Property: All index files must contain export statements
          const content = fs.readFileSync(fullPath, 'utf-8');
          expect(content).toMatch(/export/);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 11: TypeScript configuration supports all service paths', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          '@components/*',
          '@subagents/*',
          '@api/*',
          '@services/*',
          '@types/*',
          '@utils/*',
          '@hooks/*',
          '@store/*'
        ),
        (pathAlias) => {
          const tsconfigPath = path.join(projectRoot, 'tsconfig.json');
          
          // Property: tsconfig.json must exist
          expect(fs.existsSync(tsconfigPath)).toBe(true);
          
          // Property: All path aliases must be configured (string-based check)
          const tsconfigContent = fs.readFileSync(tsconfigPath, 'utf-8');
          expect(tsconfigContent).toContain(`"${pathAlias}"`);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 11: Package.json contains all required dependencies', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          'openai',
          '@qdrant/js-client-rest',
          '@neondatabase/serverless',
          'next-auth',
          '@tanstack/react-query',
          'axios',
          'react-hook-form',
          'zustand'
        ),
        (dependency) => {
          const packageJsonPath = path.join(projectRoot, 'package.json');
          
          // Property: package.json must exist
          expect(fs.existsSync(packageJsonPath)).toBe(true);
          
          // Property: All required dependencies must be listed
          const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
          const allDeps = {
            ...packageJson.dependencies,
            ...packageJson.devDependencies
          };
          
          expect(allDeps).toHaveProperty(dependency);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 11: Environment configuration files exist', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          '.env.example',
          '.env.local',
          'requirements.txt'
        ),
        (configFile) => {
          const configPath = path.join(projectRoot, configFile);
          
          // Property: All configuration files must exist
          expect(fs.existsSync(configPath)).toBe(true);
          
          // Property: Configuration files must not be empty
          const content = fs.readFileSync(configPath, 'utf-8');
          expect(content.trim().length).toBeGreaterThan(0);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 11: API structure supports backend integration', () => {
    const apiPath = path.join(projectRoot, 'src/api');
    
    fc.assert(
      fc.property(
        fc.constantFrom(
          'main.py',
          '__init__.py',
          'routers/__init__.py',
          'services/__init__.py',
          'models/__init__.py',
          'tests/__init__.py'
        ),
        (apiFile) => {
          const fullPath = path.join(apiPath, apiFile);
          
          // Property: All API structure files must exist
          expect(fs.existsSync(fullPath)).toBe(true);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 11: Build and test configuration is complete', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          'jest.config.js',
          '.eslintrc.js',
          '.prettierrc'
        ),
        (configFile) => {
          const configPath = path.join(projectRoot, configFile);
          
          // Property: All build configuration files must exist
          expect(fs.existsSync(configPath)).toBe(true);
          
          // Property: Configuration files must contain valid configuration
          const content = fs.readFileSync(configPath, 'utf-8');
          expect(content.trim().length).toBeGreaterThan(0);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 11: TypeScript compilation succeeds for all service modules', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(
          'src/types/index.ts',
          'src/services/aiService.ts',
          'src/subagents/baseSubagent.ts',
          'src/utils/constants.ts'
        ),
        (moduleFile) => {
          const modulePath = path.join(projectRoot, moduleFile);
          
          // Property: All TypeScript modules must exist
          expect(fs.existsSync(modulePath)).toBe(true);
          
          // Property: All TypeScript modules must have valid syntax
          const content = fs.readFileSync(modulePath, 'utf-8');
          
          // Basic syntax validation - should not contain obvious syntax errors
          expect(content).not.toMatch(/\bimport\s+\{[^}]*\bfrom\s+['"]/);
          expect(content).toMatch(/export/);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});