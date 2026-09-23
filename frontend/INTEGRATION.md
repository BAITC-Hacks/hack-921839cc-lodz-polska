# AKIM AI — интеграция фронтенда

Проверено с `feature/simulation` @ `051401c` и `feature/ai` @ `45c9169`. Действующий контракт — `shared/api-contract.md`. Единственное новое предложение ниже — маршрут совместного AI-сравнения; его ещё нет на сервере, флаг по умолчанию выключен.

## Согласованные границы

- Фронтенд: отдельный Next.js/TypeScript проект в `frontend/`, собственный package.json и package-lock.json. Не требует npm workspaces, общего lockfile или изменений корня.
- Сервер: FastAPI по подробному PDF «четкое разделение участников».
- Стабильные ID районов: `esil`, `almaty`, `saryarka`, `baikonur`, `nura`.
- Меры: `M1` … `M14`; направления: `transport`, `ecology`, `social`, `safety`, `services`.
- Решение: `{ "measureId": "M7", "districtId": "nura" }`. Для городского: `{ "measureId": "M12" }`, поле districtId отсутствует.
- Браузер не передаёт стоимость или Score в simulate/finalize. Не вычисляет Score, синергии, штрафы или совместимость. В UI только предварительные ограничения бюджета, повторного выбора и пяти слотов; обязательная валидация — сервер.
- Серверные ответы проверяются Zod-схемами из `lib/types.ts`. Согласуйте имена полей до интеграции.

## Endpoints

| Метод | Путь                   | Request                        | Response                                    |
| ----- | ---------------------- | ------------------------------ | ------------------------------------------- |
| GET   | /api/districts         | —                              | District[5], массив без обёртки             |
| GET   | /api/measures          | —                              | Measure[14], массив без обёртки             |
| POST  | /api/simulate          | `{decisions: Decision[]}`      | Simulation; 0–5 решений для preview         |
| POST  | /api/scenario/finalize | `{decisions: Decision[]}`      | Simulation; ровно 5 валидных решений        |
| POST  | /api/ai/analyze        | `{scenario: ScenarioSnapshot}` | AnalysisResponse из feature/ai (см. ниже)   |
| POST  | /api/recommend         | `{decisions: Decision[]}`      | Recommendation; включён в live по умолчанию |

Для AI: схема адаптирована к `feature/ai` @ `03cd8a0`, `backend/app/ai/schemas.py`. См. `lib/ai-contract.ts`: request `{scenario: {score_before, score_after, score_delta, budget: {initial,spent,remaining}, decisions: [{measure_id,name,category,scope,cost,district_id,district_name,contribution}], districts: [{district_id,district_name,before_score,after_score,indicators_before,indicators_after}], category_scores: [], critical_indicators_before, critical_indicators_after, synergies}}`. Ответ: `{strengths: [{text,evidence}], risks: [{text,evidence}], tradeoffs: [{text,evidence}], recommendations: string[], answer?: string|null}`. Фронтенд сохраняет evidence и показывает его под выводами. Тип Analysis ниже — нормализованная модель UI, не wire-формат AI.

Сервер извлекает из `scenario.decisions` только ID мер и районов, повторно рассчитывает сценарий и передаёт AI проверенные факты. `scenarioId` — идентификатор содержимого, не ключ серверного хранилища. Frontend не передаёт API-ключи и не вычисляет Score.

## Форматы

```ts
type Indicators = {
  T1: number;
  T2: number;
  E1: number;
  E2: number;
  S1: number;
  S2: number;
  B1: number;
  B2: number;
  C1: number;
  C2: number;
};
type District = {
  id: 'esil' | 'almaty' | 'saryarka' | 'baikonur' | 'nura';
  name: string;
  populationShare: number;
  profile: string;
  indicators: Indicators;
  score: number;
};
type Measure = {
  id: string;
  name: string;
  category: 'transport' | 'ecology' | 'social' | 'safety' | 'services';
  scope: 'city' | 'district';
  cost: number;
  lag: number;
  effects: Partial<Indicators>; // полные эффекты ДО учёта лага, включая отрицательные
  description: string;
  notes: string[]; // описания несовместимости и синергии
};
type Snapshot = {
  score: number;
  cityAverage: number;
  weakestDistrictId: District['id'];
  criticalCount: number;
  districts: District[]; // все 5 районов
};
type Simulation = {
  modelVersion: string;
  dataChecksum?: string; // backend возвращает SHA-256 данных
  scenarioId?: string;
  source: 'backend' | 'fixture';
  decisions: Decision[];
  validation: {
    status: 'valid' | 'invalid' | 'unverified'; // unverified используется только mock
    errors: { code: string; message: string; measureIds?: string[] }[];
  };
  budget: { total: number; spent: number; remaining: number };
  before: Snapshot;
  after: Snapshot | null; // null при невалидном наборе, никакого нулевого fake Score
  scoreDelta: number | null;
  synergies: { measureIds: string[]; districtId: District['id']; description: string }[];
  contributions: { measureId: string; districtId?: District['id']; scoreImpact: number }[];
  notice?: string;
};
type Analysis = {
  source: 'ai' | 'template'; // template только при явном fallback
  summary: string;
  strengths: string[];
  risks: string[];
  tradeoffs: string[];
  recommendations: string[];
};
type Recommendation = {
  found: boolean;
  explanation: string;
  decisions?: Decision[];
  result?: Simulation;
  candidatesChecked: number;
  validCandidates: number;
  costDelta: number | null;
  scoreDelta: number | null;
  weakestScoreDelta: number | null;
};
```

Математические поля в Snapshot всегда приходят с сервера. Preview не считается официальным результатом. Finalize повторно валидирует набор. contributions могут быть пустыми, пока backend не вернул определённый метод атрибуции; UI это обозначает. Backend возвращает Shapley-вклады; сумма совпадает с delta с точностью чисел JSON.

## Ошибки

Невалидный сценарий в simulate: HTTP 200 + `validation.status=invalid`, список ошибок, `after=null`, `scoreDelta=null`. UI не добавляет отвергнутую меру. Для HTTP-ошибок поддержаны `{message:string}`, FastAPI `{detail:string}` и `{detail:[{msg:string}]}`. AI 503/таймаут не убирает числовой результат. Нет автоматического скрытого перехода с live на mock.

Коды ошибок свободны, сообщения — пользовательские, на русском: BUDGET_EXCEEDED, DECISION_COUNT, DUPLICATE_MEASURE, CATEGORY_LIMIT, INCOMPATIBLE_MEASURES, DISTRICT_REQUIRED, UNKNOWN_MEASURE, UNKNOWN_DISTRICT.

## Время ожидания AI

После реальной проверки OpenAI лимиты согласованы с backend: SDK ждёт до 45 секунд без автоматических повторов; frontend ждёт до 60 секунд на `/api/ai/analyze`, `/api/explain`, `/api/report/executive-brief`, включая чтение JSON. Расчётные запросы сохраняют лимит 20 секунд. Ответ AI, пришедший после старых 20 секунд, больше не обрывается преждевременно. Числовой результат остаётся доступным при AI 503 или таймауте. Таймаут reverse proxy для этих маршрутов должен быть не короче 60 секунд. Backend-изменение находится в PR #3; frontend-изменение — в PR #2. Нужны обе версии.

Дополнение интегратора: для `/api/ai/advice` также действует клиентский лимит 60 секунд. В `feature/simulation` @ `d0941fa` этот маршрут принимает `{decisions, question?}` и возвращает проверенные варианты отдельных добавлений к неполному плану. Подробности — `shared/api-contract.md`. Внутренний `AdviceRequest` AI-модуля браузер не отправляет. Перед применением выбранного совета весь новый набор повторно проверяется через `/api/simulate`; устаревшие советы сбрасываются. Добавление UI и отдельного метода клиента остаётся у FRONTEND. Маршрут `/api/ai/compare` по-прежнему является предложением, флаг должен оставаться выключенным.

## Контрольный пример

M7 nura + M8 nura + M10 nura + M12 city + M5 saryarka. Стоимость 95. Исходный Score 52.55768, итоговый 56.54307 согласно плану проекта; backend обязан независимо проверить арифметику. `lib/fixtures.ts` — только статический образец для UI, не математический движок. Для произвольных наборов mock не выдаёт результат.

## Переключение на backend

В `frontend/.env.local`:

```dotenv
NEXT_PUBLIC_API_MODE=live
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_ENABLE_RECOMMENDATIONS=true
NEXT_PUBLIC_ENABLE_AI_COMPARISON=false
```

Перезапустить dev-сервер; для production выполнить новую сборку. Разрешить backend CORS для используемого origin фронтенда (по умолчанию http://127.0.0.1:3000; localhost — отдельный origin). API-ключи AI в браузер не передаются, NEXT_PUBLIC для секретов запрещён.

Если бекенд на другом origin HTTPS, настроить разрешённый origin и TLS. Пустой base URL подходит для same-origin reverse proxy. Сам Next.js здесь не содержит backend API routes.

## Что не нужно менять друг другу

Frontend владеет только `frontend/**`. Backend-интегратор владеет shared/, backend/, общим README и Docker Compose. AI-владелец — своими backend/app/ai и report. Все изменения фронтенда идут в feature/frontend, не напрямую в main.

## Смоук-проверка интеграции

1. GET возвращает 5 районов и 14 мероприятий с официальными значениями.
2. simulate([]) возвращает базу; add/remove меняют preview без stale-response.
3. При M1+M3, M4+M7 в одном районе, M5+M13 в одном районе сервер возвращает понятные ошибки; UI сохраняет предыдущий допустимый набор.
4. Сервер запрещает повторы, превышение 100, 3 меры одного направления, неизвестные ID.
5. finalize допускает только ровно 5 мер. Перестановка не меняет результат.
6. Контрольный пример 95 → 56.54307; AI не меняет числа.
7. AI 503, HTTP 422, неверный JSON и таймаут показываются корректно.
8. «Улучшить одной заменой»: сервер заменяет M5/Сарыарка на M3/Нура. Итог 56.54307 → 57.20556, расход 95 → 100, слабейший район 52.9625 → 54.9825; delta Score +0.66249, бюджета +5, слабейшего +2.02. Таблица показывает ухудшение Сарыарки 56.3 → 55.0875.
9. Сохранить исходный, применить замену: повторный simulate, редактор с пятью новыми решениями. Затем finalize; при HTTP 422 исходные решения и результат сохраняются.
10. Неполный ответ, несогласованные delta, другой набор решений, более одной замены, другой modelVersion/checksum или исходные данные не допускаются к применению. found=false показывает отсутствие улучшения в пределах одной замены, а не глобальную оптимальность.
11. AI-разбор предложенного плана работает через существующий /api/ai/analyze, отдельно от исходного. При 503 можно повторить; числа и применение остаются доступны.

23.09.2026: устаревший корневой AGENTS.md очищен в main @ 573ee0b; AI-модуль возвращён к городскому кейсу в feature/ai @ 03cd8a0. Фронтенд учитывает текущую городскую схему AI.

## Совместный AI-анализ — контракт для участников AI/backend

**Предложение, пока не реализованное в серверных ветках.** Frontend содержит адаптер, панель с доказательствами, loading/error/retry и тесты. По умолчанию `NEXT_PUBLIC_ENABLE_AI_COMPARISON=false`: запросов к отсутствующему маршруту нет. Флаг включается только после реализации и общей проверки ниже; затем требуется пересборка Next.js.

`POST /api/ai/compare` принимает только решения, без клиентских чисел:

```ts
type CompareRequest = {
  originalDecisions: Decision[]; // ровно пять, исходный план
  alternativeDecisions: Decision[]; // ровно пять, предложенный план
};
type CompareResponse = {
  originalScenarioId: string;
  alternativeScenarioId: string;
  modelVersion: string;
  dataChecksum: string;
  analysis: {
    strengths: { text: string; evidence: string[] }[];
    risks: { text: string; evidence: string[] }[];
    tradeoffs: { text: string; evidence: string[] }[];
    recommendations: string[];
    answer: string | null;
  };
};
```

Backend-владелец добавляет маршрут в свой integration bridge: независимо финализирует оба набора по одной текущей модели, получает две проверенные выборки фактов и их ID. Числа от браузера не принимаются. AI-владелец добавляет отдельный метод сравнения двух серверных snapshots; существующий AnalysisRequest с одним scenario сохраняет совместимость. Маршрут не должен дублировать существующие пути.

AI объясняет, какое решение заменено, почему меняются общий Score, бюджет и слабейший район, где есть потери и компромиссы. Ссылается только на переданные сервером факты обоих планов, не пересчитывает Score, не предлагает выдуманные меры и не называет поиск одной замены глобальной оптимизацией. Вывод — существующие finding/evidence и answer в analysis. Поля modelVersion/checksum/ID добавляет backend, а не LLM.

Ошибка любого из двух планов: HTTP 422 с безопасным message. Отсутствие провайдера, некорректный AI-ответ или таймаут: HTTP 503 с message. Без шаблонного ответа под видом AI. SDK: 45 секунд без автоматических повторов; frontend: 60 секунд на весь запрос, включая JSON; reverse proxy не короче 60 секунд.

Frontend проверяет все четыре поля принадлежности ответа: два scenarioId, modelVersion, dataChecksum. При смене данных требует пересчёт; поздний ответ после смены плана не показывается. AI не меняет решения автоматически.

### Приёмка нового маршрута

1. Пересчитать официальный пример и его найденную замену; отправить только два массива decisions.
2. Ответ содержит ID этих двух финализированных сценариев и текущие modelVersion/checksum.
3. AI объясняет +0.66249 Score, +5 расходов, +2.02 у слабейшего района и потерю Сарыарки 1.2125 балла на проверенных фактах.
4. Ошибка в любом наборе возвращает 422; AI недоступен — 503 без потери числовых результатов.
5. Включить флаг и пересобрать frontend; «Объяснить различия с AI» показывает выводы и evidence, повтор работает после ошибки.
6. Если API не реализован или не прошёл проверку, оставить флаг false. Отдельный разбор предложенного плана продолжает работать через существующий endpoint.

### Что проверено на стороне frontend

Автоматические проверки используют буквальные fixtures сервера из `shared/fixtures`, копии в `lib/test-fixtures`. Для совместного AI-маршрута тестируется предложенный контракт на тестовом ответе; это не проверка существующего backend или реального провайдера. Полная проверка нового маршрута остаётся у интегратора после его реализации.
