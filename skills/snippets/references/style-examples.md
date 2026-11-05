# One-liner style

The report is read by the whole team. Every bullet must make sense to Marketing or Sales — follow the User-Facing Copy rules in `AGENTS.md` (the product's vocabulary, no internal operational details, no internal codenames).

Rules:

- In the team's language. In Spanish, open with a past participle: *Arreglado/a, Añadido/a, Mejorado/a, Optimizado/a, Publicado/a, Convertido/a...* Headers stay in English as templated.
- Describe the **outcome for the team or the customer**, not the mechanism. "Arreglada la alarma que saltaba sin motivo", not "cambiado el nivel de log a INFO".
- Proper nouns stay untranslated: product names, customers, tools.
- One line per topic. Group siblings with `(xN)` and list all links.
- Links: `([#12](https://github.com/<org>/<repo>/pull/12))`; issues use `/issues/`. Chat-only work gets no link — never fabricate one.

## Example transformations

| PR/issue title | Bullet |
| --- | --- |
| `[api] Log request body at INFO to stop alarm false positives` | Arreglada la alarma de la API que saltaba sin motivo ([#12](https://github.com/<org>/<repo>/pull/12)) |
| `[api] Anomaly consumer: fetch series once per account; cap warehouse load` | Optimizado el detector de anomalías para no sobrecargar el almacén de datos ([#13](https://github.com/<org>/<repo>/pull/13)) |
| `[devops] Promote ship-it, ship-it-lite, lgtm, and yolo to team skills` | Convertidas en skills de equipo las de crear, revisar y mergear PRs ([#14](https://github.com/<org>/<repo>/pull/14)) |
| `[web] Persist active environment when saving reports` | Arreglado que los informes guardados no recordaran el entorno activo ([#15](https://github.com/<org>/<repo>/pull/15)) |

## Mini rendered example

```
## 📚 Done

### 👨‍💻 Coding

**Bugs/Cleanups (⭐ Sheriff!)**

Arreglada la alarma de la API que saltaba sin motivo ([#12](https://github.com/<org>/<repo>/pull/12))

**DevOps**

Revisión semanal de costes (x2) ([#17](https://github.com/<org>/<repo>/pull/17), [#18](https://github.com/<org>/<repo>/pull/18))

### 🆘 Support

Mejorada la cobertura de datos de un cliente para sus informes ([#16](https://github.com/<org>/<repo>/pull/16))

### 🧙‍♂️ Product

### ✔️ Reviewing & Collaborating

### 🤖 Dev Team Stuff

Configurada la cuenta del proveedor de modelos con su soporte

### 🎲 Others

## 📅 To Do

Reunión con un cliente — 24 jul

Terminar y mergear la nueva integración ([#19](https://github.com/<org>/<repo>/pull/19))
```
