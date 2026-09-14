# EAFinder — Frontend

Aplicación Angular del asistente EAFinder.

```bash
npm install
npm start      # http://localhost:4200
npm run build  # compila a dist/
```

La URL del backend está en `src/environments/environment.ts`.

## Estructura

```text
src/app/
├── core/     # api.service · session.service · chat.store · models
├── layout/   # sidebar · topbar · composer
├── pages/
│   ├── welcome/   # pantalla inicial, sugerencias y enlaces (US03)
│   └── chat/      # conversación con fuentes citadas (US09)
├── app.ts    # shell de la aplicación
└── app.routes.ts
```

Todo el diseño vive en un único archivo, `src/styles.css`, para que sea
fácil ajustarlo en equipo.
