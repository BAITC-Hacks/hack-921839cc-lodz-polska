# AKIM AI API contract v1.0.0

Согласован с `frontend/INTEGRATION.md`, `frontend/lib/types.ts` и `frontend/lib/ai-contract.ts` из `feature/frontend` (проверенная версия `2412b1e16b10c892fa66b5eaeaf040c6795907e2`). Backend — единственный источник расчётных значений. Simulation JSON использует **camelCase**; текущий AI-адаптер фронтенда использует **snake_case**. ID района Есиль — **esil**. Все значения синтетические.

## Запуск и маршруты

Backend по умолчанию слушает `http://127.0.0.1:8000`. `/docs` — интерактивная документация, `/openapi.json` — машинная схема. CORS разрешает `http://127.0.0.1:3000` и `http://localhost:3000`; другие origin задаются через `CORS_ORIGINS` (список через запятую).

| Метод | URL | Вход | Выход |
|---|---|---|---|
| GET | /api/health | — | status, modelVersion, dataChecksum, aiConfigured |
| GET | /api/districts | — | District[5] без обёртки |
| GET | /api/measures | — | Measure[14] без обёртки |
| GET | /api/bootstrap | — | districts, measures, before, rules, modelVersion, dataChecksum, notice |
| POST | /api/simulate | ScenarioRequest | Simulation; preview от 0 до 5 решений |
| POST | /api/scenario/finalize | ScenarioRequest | Simulation; ровно 5 допустимых решений |
| POST | /api/recommend | ScenarioRequest | Recommendation; лучший вариант с одной заменой |
| POST | /api/ai/analyze | {scenario: ScenarioSnapshot, question?: string} | AnalysisResponse с Finding/evidence (текущий frontend) |
| POST | /api/explain | {decisions: Decision[], question?: string} | Analysis; эквивалентный компактный запрос |
| POST | /api/report/executive-brief | {decisions: Decision[], question?: string} | AI-owned ExecutiveBrief, snake_case |

`GET /api/health` не вызывает AI. `aiConfigured` означает наличие настроенного адаптера, а не успешную проверку внешнего сервиса.

## Основной запрос

```json
{"decisions":[{"measureId":"M7","districtId":"nura"},{"measureId":"M8","districtId":"nura"},{"measureId":"M10","districtId":"nura"},{"measureId":"M12"},{"measureId":"M5","districtId":"saryarka"}]}
```

Для городской меры `districtId` опускается. Входной null трактуется как отсутствие, ответ всегда опускает поле. Цены, индикаторы, веса и готовый Score в ScenarioRequest запрещены. Для Python-интеграции также принимаются snake_case имена полей; ответы только camelCase. Идентификаторы регистрозависимы, строки автоматически не исправляются. Технический предел массива запроса — 100, бизнес-предел — 5; это позволяет возвращать осмысленную ошибку для 6 решений.

## Формат Simulation

Базовые поля полностью соответствуют фронтенду:

```ts
type Decision = {measureId:string; districtId?:string};
type District = {
  id:'esil'|'almaty'|'saryarka'|'baikonur'|'nura'; name:string;
  populationShare:number; profile:string;
  indicators:Record<'T1'|'T2'|'E1'|'E2'|'S1'|'S2'|'B1'|'B2'|'C1'|'C2',number>;
  score:number;
};
type Snapshot = {
  score:number; cityAverage:number; weakestDistrictId:District['id'];
  criticalCount:number; districts:District[];
};
type Simulation = {
  modelVersion:string; scenarioId?:string; source:'backend';
  decisions:Decision[];
  validation:{status:'valid'|'invalid';errors:{code:string;message:string;measureIds?:string[]}[]};
  budget:{total:number;spent:number;remaining:number};
  before:Snapshot; after:Snapshot|null; scoreDelta:number|null;
  synergies:{measureIds:string[];districtId:District['id'];description:string}[];
  contributions:{measureId:string;districtId?:District['id'];scoreImpact:number}[];
  notice:string;
  // Дополнительные поля; текущие Zod-схемы фронтенда допускают их:
  dataChecksum:string; finalized:boolean; score:number|null;
  contributionMethod:'shapley';
  criticalIndicators:{districtId:District['id'];indicatorId:string;before:number;after:number;resolved:boolean}[];
};
```

Для preview `after.score` — **предварительный** расчёт, `finalized=false`, официальный `score=null`; notice явно это сообщает. UI не должен представлять preview как финальный результат. Вклады считаются только для finalize. После допустимого finalize `score=after.score`, `finalized=true`. До/после округляются только при отображении в UI, не при расчёте.

Для любого невалидного набора: `validation.status=invalid`, `after=null`, `scoreDelta=null`, `score=null`, `finalized=false`. Переданная стоимость в budget показывает сумму известных мер (включая повторы), это диагностическая сумма, а не одобренный бюджет. Остаток может быть отрицательным в ответе об ошибке. Неизвестные ID отражаются в ошибках и не участвуют в расчёте.

`scenarioId` — стабильный SHA-256 данных модели и упорядоченных решений. Это идентификатор содержимого, **не ключ серверного хранилища**. Порядок решений не меняет ID или результат. Сохранение сценариев остаётся в браузере; сервер stateless.

`Measure.effects` — полные эффекты до лага; `description` и `notes` содержат охват, задержку, несовместимости и синергии. Полученные от API объекты содержат только числа JSON, не Decimal-строки.

## Ошибки

Бизнес-ошибки simulate/finalize: **HTTP 200 + Simulation с validation.status=invalid**. Это соответствует текущему UI. Рекомендации и AI требуют допустимого полного набора: иначе HTTP 422 с `{message,code,errors,score:null}`.

Неверные типы, лишние поля, некорректный JSON: HTTP 422 с тем же ErrorResponse. Отсутствующий/ошибочный AI или report: HTTP 503 `{message,code:'AI_UNAVAILABLE',errors:[],score:null}`. Расчётные маршруты продолжают работать. Исключения провайдера и ключи не отправляются клиенту.

Коды: DECISION_COUNT, DUPLICATE_MEASURE, CATEGORY_LIMIT, BUDGET_EXCEEDED, UNKNOWN_MEASURE, UNKNOWN_DISTRICT, DISTRICT_REQUIRED, DISTRICT_NOT_ALLOWED, INCOMPATIBLE_MEASURES, INVALID_REQUEST, INVALID_SCENARIO, AI_UNAVAILABLE. Сообщения бизнес-ошибок — на русском.

## Вклады и рекомендации

`scoreImpact` — точный Shapley-вклад: средний предельный вклад по всем порядкам добавления выбранных мер. Метод делит эффекты синергий и нелинейных штрафов между участниками. Сумма вкладов математически равна изменению Score (при суммировании JSON-float допустима погрешность машинного представления). Подмножества используются только как внутренние контрфактические расчёты.

Рекомендация перебирает замену ровно одной меры на любую допустимую меру/район, включая смену района той же меры. Сначала максимальный Score, при равенстве — меньшая стоимость, затем стабильный порядок ID. Улучшение должно быть строгим. Остаток не даёт бонус Score; стоимость служит только правилом выбора между равными результатами.

```ts
type Recommendation = {
  found:boolean; explanation:string; decisions?:Decision[]; result?:Simulation;
  candidatesChecked:number; validCandidates:number;
  costDelta:number|null; scoreDelta:number|null; weakestScoreDelta:number|null;
};
```

При found=false decisions/result опущены; остальные дельты null. Найденный вариант повторно финализируется. Можно включать `NEXT_PUBLIC_ENABLE_RECOMMENDATIONS=true`.

## Интеграция AI

Текущий фронтенд вызывает `{scenario: ScenarioSnapshot}` через `createAnalysisRequest()` из `frontend/lib/ai-contract.ts`. Backend извлекает **только measure_id/district_id из decisions**, заново валидирует и рассчитывает их, затем строит свой `ScenarioSnapshot` для AI. Присланные цены, названия, числовые поля, source, scenarioId и validation не используются как факты. Никакого доверия к клиентскому Score. Временная обратная совместимость: начальный вариант `{simulation: Simulation}` также принимается, но отвечает исходным упрощённым Analysis. Не передавайте обе обёртки одновременно.

Существующие AI `AnalysisRequest`, `AnalysisResponse`, `analyze_scenario()` и `build_executive_brief()` используются через адаптер `app/api/simulation/ai_bridge.py`. AI-файлы не изменяются. Вход `ScenarioSnapshot` остаётся snake_case, включает district/category before/after, бюджет, критические показатели, синергии и Shapley-вклады. Публичные роутеры AI, принимающие клиентские факты, **не подключать дополнительно**: иначе появятся дублирующиеся пути и обход пересчёта.

Выход для текущего `{scenario:...}`: `{strengths:Finding[],risks:Finding[],tradeoffs:Finding[],recommendations:string[],answer:string|null}`, где `Finding={text:string,evidence:string[]}`. Его принимает реальный `aiResponseSchema`, затем frontend сам нормализует формат. Для `/api/explain` и старой обёртки `{simulation:...}` возвращается `{source:'ai',summary,strengths:string[],risks:string[],tradeoffs:string[],recommendations:string[]}`. Шаблонный текст не выдаётся за AI. Фактическая работа провайдера требует объединённой AI-ветки, `requirements-ai.txt`, модели с доступом и ключа backend. `backend/.env` загружается без перезаписи переменных окружения. Таймаут SDK 15 секунд, автоматических повторов нет, чтобы укладываться в 20-секундный таймаут UI.

Отчёт получает решения и question; backend самостоятельно формирует и snapshot, и AI-анализ. Не принимаем от браузера числа отчёта. Формат ExecutiveBrief принадлежит AI-модулю, не фронтенд-схеме Simulation.

## Контроль и воспроизводимость

`shared/example-scenario.json` — запрос контрольного примера. Base Score = 52.55768, финал = 56.54307, стоимость = 95, delta = 3.98539. В `shared/fixtures/` находятся ответы, сгенерированные backend, для проверки UI без повторной реализации математики. Формулы и данные — `backend/docs/requirements-analysis.md` и JSON-файлы shared. Изменение данных меняет checksum; изменение семантики требует новой modelVersion.
