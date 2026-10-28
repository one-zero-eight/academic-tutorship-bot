# AGENTS.md

Guidance for AI agents working on the Academic Tutorship Bot.

## What This Is

Telegram bot for Academic Tutorship at Innopolis University. Two bots run from one process:
the **control bot** (main UX, aiogram-dialog) and the **notification bot** (separate token, plain handlers).

Stack: Python 3.13, aiogram 3, aiogram-dialog 2, SQLAlchemy 2 (async) + Alembic, APScheduler,
Fluent (`.ftl`) localisation, uv, Ruff, pytest.

## Project Structure

```
src/
  config.py, config_schema.py     settings loaded from settings.yaml (pydantic, generates settings.schema.yaml)
  accounts_sdk.py                 InNoHassle Accounts client (authentication)
  prepare.py                      BASE_DIR and other path helpers

  domain/models.py                pydantic models + enums (UserStatus, MeetingStatus, Student, Tutor, ...)

  db/
    schema.py                     SQLAlchemy Table definitions (single source of DB truth)
    repositories/                 db = SQLDatabase(...) + student_repo / tutor_repo / admin_repo /
                                  meeting_repo / discipline_repo singletons
  alembic/versions/               migrations

  bot/
    __main__.py, app.py           entrypoint; bot/dispatcher wiring, router registration, i18n, error handlers
    dispatcher.py                 CustomDispatcher: logs and answers unhandled updates
    middlewares.py                AutoAuthMiddleware (auth + status + self_tutor sync), AuthGuardMiddleware,
                                  DialogI18nMiddleware
    filters.py                    get_user_roles / get_user_status, StatusFilter, UserAuthenticatedFilter
    user_errors.py                domain-level user-facing exception types
    exceptions.py                 UnauthenticatedException, AuthorityException
    utils.py                      get_windows(*_ww), user_status_getter, BLANK_BTN, parsing helpers
    i18n.py, constants.py         I18NFormat, translation helpers
    logging_.py                   logger + log_info / log_warning / log_error
    dialog_extension/             ExtendedDialogManager (+extend_dialog), ExtendedFSMContext,
                                  guards.py (StatusGuard, StatusGuardedDialog, require_status)
    custom_widgets/               reusable Text widgets (MeetingInfoText, ...)
    routers/
      commands.py                 non-dialog handlers: /start, /excel, /add-discipline, ...
      queries.py                  callbacks from notification messages
    dialogs/                      one package per dialog (see "Dialog Anatomy")

  notifications/                  notification bot: manager, texts, handles, its own Dispatcher
  scheduling/                     APScheduler jobs for meeting reminders
  utils/                          excel export, discipline command parsing

locales/{en,ru}/LC_MESSAGES/      dialog.ftl, handles.ftl, notifications.ftl, notification_handles.ftl
tests/                            pytest suite; fixtures.py builds in-memory SQLite repos
scripts/                          settings schema generator, alembic autogen helper, redis cleanup
docs/                             DB ERD diagrams, feature/text reference
```

## Core Layers

* **domain/models.py** — pydantic models with business methods (`Meeting.announce()`, `Meeting._check_for_approval()`).
  Keep behaviour here, not in handlers.
* **db/repositories/** — all SQL lives here; handlers never touch `db.engine` directly.
* **bot/dialogs/** — UI only: render windows, call repositories, call domain methods.
* **notifications/scheduling** — side effects triggered from dialog logic modules.

## Dialog Anatomy

Every dialog package follows the same shape (e.g. `src/bot/dialogs/tutors/`):

| File | Role |
|---|---|
| `states.py` | `StatesGroup` with one `State` per window |
| `windows.py` | `Window(...)` definitions, one per state; **must be named `*_ww`** (`get_windows` collects them) |
| `getters.py` | async data getters; also compute `when=`-flags (`is_admin`, `can_be_deleted`, ...) |
| `handles.py` | `on_click` / `MessageInput` handlers |
| `dialog_buttons.py` | shared keyboard widgets (`ScrollingGroup`, `Select`, blank buttons) |
| `__init__.py` | builds `dialog`, attaches `AuthGuardMiddleware` (and status guard, if privileged) |

Register the dialog in `src/bot/app.py` (`dp.include_router(<dialog>)`).

## Authorization (read before adding any feature)

Two independent concerns:

1. **Authentication** — `AuthGuardMiddleware` on every dialog except `authentication`. Add it to any new dialog.
2. **Authorization** — role is resolved from the DB on **every event** by `get_user_roles()`
   (`src/bot/filters.py`), which returns the set of roles; an admin may also be a tutor.

`when="is_admin"` / `when="is_tutor"` in a window only controls **rendering**. An old keyboard keeps working
after privileges are removed, so `when=` is never sufficient for a privileged action.

### Guard the branch

```python
# src/bot/dialogs/<name>/__init__.py
from src.bot.dialog_extension import StatusGuard, StatusGuardedDialog
from src.domain.models import UserStatus as US

dialog = StatusGuardedDialog(*get_windows(windows), guard=StatusGuard((US.tutor, US.admin)))
```

`StatusGuardedDialog` installs the guard as a root filter on all observers (after `IntentFilter`, so the DB hit
only happens for that dialog's events) **and** re-checks in `process_start`, so a stale `Start` button cannot
even render the branch. Keep plain `Dialog` for fully public dialogs (`root`, `student_meetings`,
`tutor_profile`, `guide`, `discipline_picker`) — do not over-restrict student paths.

### Guard a single button

Use this when a dialog is shared but some actions are privileged (e.g. announce = admin,
assign tutor = admin, tutor profile editing = tutor):

```python
from src.bot.dialog_extension import require_status

@require_status(US.admin)
async def on_some_privileged_action(query, widget, manager): ...
```

* Raises `AuthorityException`; `app.py` answers the callback with `Q_NOT_AUTHORIZED` and resets the stack.
* `require_status(US.tutor, forbidden=(US.admin,))` expresses "tutor but not admin".
* Roles, not a single status: an admin-tutor passes `US.tutor`, matching `user_status_getter`.

Rules:
* New privileged dialog → branch guard. New privileged button in a shared dialog → `require_status`.
* Prefer guarding the **target** branch over the source button when a `Start` has no handler.
* If a handler is shared between dialogs, guard it only if **every** caller should be restricted
  (student-facing handlers such as `open_tutor_profile` must stay unguarded).
* Always pair the guard with the matching `when=` flag from the getter, so the UI hides what is denied.

## Adding a Feature

1. **Decide the surface.** A full flow → new dialog package. A one-shot action → handler in
   `routers/commands.py`. Notification-bot behaviour → `notifications/`.
2. **Search before writing.** Grep for an existing dialog, getter, widget, handler, or repository method that
   already does it. Reuse is preferred over new abstractions — in particular reuse:
   `extend_dialog`, `ExtendedFSMContext` (`get_/set_/sync_` helpers), `user_status_getter`, `BLANK_BTN`,
   `I18NFormat`, `custom_widgets`, `meeting_info_getter`, `selected_disciplines_getter`, `DisciplinePickerStates`.
   `disciplines_control` and `authentication` are the pattern for minimal dialogs.
3. **Data layer.** Add a repository method rather than inlining SQL. Table changes go to `db/schema.py`
   plus an Alembic migration.
4. **Domain rules.** Put state transitions and preconditions on the pydantic models / `logic.py`, not in handlers.
5. **UI.** Add a state, a `*_ww` window, a getter returning the data **and** the `when=` flags, and handlers.
6. **Authorization.** Branch guard or `require_status` (see above).
7. **Text.** New user-visible strings go to `locales/en/LC_MESSAGES/*.ftl` and the `ru` counterpart.
8. **Logging.** Follow the existing event-name style: `log_info("tutor.remove.succeeded", user_id=..., tutor_id=...)`.
9. **Register** the dialog in `app.py` if new.
10. **Test and lint** (see Commands). Add a repository test and, for guarded code, a guard test.

## Conventions

* **Layering**: windows/getters are declarative; handlers orchestrate; repositories do IO; models hold rules.
* **i18n**: never hard-code user text in dialogs (`I18NFormat`/`manager.tr`), use `.ftl` keys. Admin/user
  alert texts come from `handles.ftl` (`Q_*` keys).
* **Errors**: raise the specific types in `bot/user_errors.py` and catch them in the handler to show a
  user-friendly alert; let unexpected errors propagate (they are logged and answered).
* **State**: read/write FSM data through `ExtendedDialogManager.state`, prefer typed helpers
  (`get_meeting`, `sync_meeting`, `get_self_tutor`) over raw `get_value`.
* **HTML**: escape user/db text with `html.escape` in getters; messages use `parse_mode=HTML`.
* **Names**: singular DB entities, `snake_case` modules, dialog package per `StatesGroup`, `*_ww` windows.
* **Style**: Ruff (line length 120, `py313`), imports sorted, `from src...` absolute imports.

## Commands

```bash
uv sync                                  # install deps
uv run -m src.bot                        # run the bots
uv run ruff check src tests              # lint
uv run ruff format src tests             # format
uv run pytest tests -q                   # tests
uv run prek run --all-files              # all pre-commit hooks
```

Settings: copy `settings.example.yaml` → `settings.yaml`; schema in `src/config_schema.py`
(regenerate `settings.schema.yaml` with `scripts/generate_settings_schema.py`).

## Testing

* `tests/fixtures.py` provides in-memory SQLite repositories (`db`, `student_repo`, `tutor_repo`, ...).
* Repository tests use these fixtures; middleware/guard tests monkeypatch the repository singletons
  (`src.bot.filters.tutor_repo.exists`, ...) and use `SimpleNamespace` events.
* For guards, assert both sides: denied role is blocked, required role (including admin-tutor) is allowed.

## Pitfalls

* `when=` is render-time only — never treat it as authorization.
* Filtering `event_from_user` may be `None` for simulated/internal events; guards must return `False` safely.
* `StatusFilter(US.tutor)` means "has tutor role"; effective `status` for display still uses
  admin → tutor → student precedence.
* Do not attach `on_click` with side effects to a `Start` button of another dialog: it runs in the **source**
  handler before the target guard.
* Windows are collected by name — a window not ending in `_ww` silently disappears from the dialog.
* `settings.yaml`, `try/`, `.logs/` are gitignored; never commit secrets.
