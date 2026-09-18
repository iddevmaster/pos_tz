# Certificate editor handoff — 2026-09-18

## Resume at home

- Branch: `uat_tz`.
- Pull this branch, activate a working Python environment, then run `python manage.py migrate app 0003` against the intended database. This migration has already been applied to the database used during this session.
- Open `/certificate/settings/th/` or `/certificate/settings/eng/` after logging in. The main sidebar menu is **ตั้งค่าใบเซอร์**.
- Access requires an active staff account and the appropriate CertificateLayout add/change permission (superusers have these).
- Local database settings in `trainingzenter/settings.py` were already modified before this work and are NOT included in this commit. Configure the home environment separately. Do not copy credentials into this document.

## Implemented

- Django CertificateLayout model, migration 0003, admin and main-site editor.
- 24 draggable/resizable elements, fonts, colors, visibility, locking, text editing, language-specific database layouts.
- Redesigned editor with canvas, property inspector, fit-to-width zoom and save status.
- Shared renderer for saved layouts and print; names/course/date remain dynamic.
- Thai legacy print template aligned with the English structure; Thai corner artwork now responds to frame width.
- Editor corner artwork uses cover instead of contain to eliminate empty margins; default Thai corner dimensions match the legacy print template's 40% width.

## Important current state

- A nonempty saved layout activates the shared renderer. An absent/empty layout uses the legacy language-specific HTML template.
- At the user's request, the Thai saved layout was reset to `{}` to match the then-current English legacy layout. The previous Thai layout was backed up only on the work computer at `C:\Users\itser\AppData\Local\Temp\certificate-th-layout-20260918-092423.json`.
- Layout data lives in the database and does not travel with Git. Saving in the editor activates that layout for all certificates in its language.
- No certificate-specific layout versioning or image upload UI is implemented.

## Verification and remaining visual check

- 11 tests in `app/test_certificate_layout.py` passed using an isolated in-memory SQLite database; Django system check and JavaScript syntax checks passed.
- Existing models have unrelated migration drift. Do not generate a broad migration to resolve it as part of this feature.
- Browser interaction/visual print verification was unavailable in this session. Check Thai corner backgrounds, dragging, saved preview and actual A4 landscape print at home.
- Example certificate: `/register/certificate/c55d6c68-c7a9-4850-86da-4347dcb2d0d2`.
- Use Ctrl+F5 after pulling to refresh editor CSS/JS.
