### Raccogliere la coverage in Playwright

Playwright deve essere istruito a salvare i dati di copertura alla fine di ogni test. Il modo più pulito per farlo è estendere la funzione base test di Playwright creando una fixture personalizzata.


_GIÀ FATTO IO_
## 1. Installare le librerie necessarie

Posizionati nel terminale all'interno della cartella `frontend/` e installa il plugin per Vite e lo strumento `nyc`:
```bash
npm install -D vite-plugin-istanbul nyc
```

_GIÀ FATTO IO_
## 2. Strumentare il codice in Vite

Modifica il file `vite.config.ts` (o `.js`) per includere il plugin di Istanbul. Questo preparerà il codice per tracciare le righe eseguite:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import istanbul from 'vite-plugin-istanbul'

export default defineConfig({
  plugins: [
    react(),
    istanbul({
      cypress: true,
      requireEnv: false
    })
  ]
})
```

## 3. Raccogliere la coverage in Playwright

Crea un file chiamato `fixtures.ts` per estendere la funzione base di Playwright e salvare i dati alla fine di ogni test:

```javascript
import { test as baseTest, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

export const test = baseTest.extend({
  context: async ({ context }, use) => {
    await context.addInitScript(() => {
      window.__coverage__ = window.__coverage__ || {};
    });
    
    await use(context);
    
    for (const page of context.pages()) {
      const coverage = await page.evaluate(() => window.__coverage__);
      if (coverage && Object.keys(coverage).length > 0) {
        fs.mkdirSync(path.join(process.cwd(), '.nyc_output'), { recursive: true });
        fs.writeFileSync(
          path.join(process.cwd(), '.nyc_output', `coverage-${Date.now()}.json`),
          JSON.stringify(coverage)
        );
      }
    }
  }
});

export { expect };
```

Ora nei tuoi file di test (es. `app.spec.ts`), importa `test` ed `expect` da questa nuova fixture invece che da `@playwright/test`:

```javascript
import { test, expect } from './fixtures';

test('il bottone funziona', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('button')).toBeVisible();
});
```

## 4. Generare il report

Aggiungi questi script al tuo `package.json` nel frontend per eseguire i test e convertire i file estratti in un formato leggibile:

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "coverage:report": "nyc report --reporter=html --reporter=cobertura"
  }
}
```