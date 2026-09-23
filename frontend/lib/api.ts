import { z } from 'zod';
import {
  districtsSchema,
  measuresSchema,
  recommendationSchema,
  simulationSchema,
  type Decision,
  type Measure,
  type Simulation,
} from './types';
import {
  baseline,
  districts,
  exampleAnalysis,
  exampleDecisions,
  exampleResult,
  measures,
} from './fixtures';
import { aiResponseSchema, createAnalysisRequest, normalizeAnalysis } from './ai-contract';
export const isMock = process.env.NEXT_PUBLIC_API_MODE !== 'live';
export const recommendationsEnabled = process.env.NEXT_PUBLIC_ENABLE_RECOMMENDATIONS === 'true';
const origin = (process.env.NEXT_PUBLIC_API_BASE_URL ?? '').replace(/\/$/, '');
export class ApiError extends Error {
  constructor(
    message: string,
    public status = 0,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
export async function request<T>(path: string, schema: z.ZodType<T>, body?: unknown): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(`${origin}${path}`, {
      method: body === undefined ? 'GET' : 'POST',
      headers: {
        Accept: 'application/json',
        ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      signal: controller.signal,
      cache: 'no-store',
    });
    const data: unknown = await response.json().catch(() => {
      throw new ApiError('Сервер вернул ответ не в формате JSON.', response.status);
    });
    if (!response.ok) {
      const parsed = z
        .object({
          message: z.string().optional(),
          detail: z.union([z.string(), z.array(z.object({ msg: z.string() }))]).optional(),
        })
        .safeParse(data);
      const detail = parsed.success ? parsed.data.detail : undefined;
      throw new ApiError(
        parsed.success && parsed.data.message
          ? parsed.data.message
          : typeof detail === 'string'
            ? detail
            : Array.isArray(detail)
              ? detail.map((e) => e.msg).join('; ')
              : `Сервер не принял запрос (${response.status}).`,
        response.status,
      );
    }
    const parsed = schema.safeParse(data);
    if (!parsed.success)
      throw new ApiError(
        'Формат ответа сервера не совпадает с контрактом фронтенда. Проверьте интеграцию.',
        response.status,
      );
    return parsed.data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof Error && error.name === 'AbortError')
      throw new ApiError('Сервер не ответил за 20 секунд. Попробуйте ещё раз.');
    throw new ApiError('Не удалось связаться с сервером. Проверьте подключение и адрес API.');
  } finally {
    clearTimeout(timeout);
  }
}
export const decisionKey = (decisions: Decision[]) =>
  decisions
    .map((d) => `${d.measureId}:${d.districtId ?? ''}`)
    .sort()
    .join('|');
const isExample = (decisions: Decision[]) =>
  decisionKey(decisions) === decisionKey(exampleDecisions);
const delay = () => new Promise<void>((resolve) => setTimeout(resolve, 300));
export const api = {
  async districts() {
    return isMock ? structuredClone(districts) : request('/api/districts', districtsSchema);
  },
  async measures() {
    return isMock ? structuredClone(measures) : request('/api/measures', measuresSchema);
  },
  async simulate(decisions: Decision[]): Promise<Simulation> {
    if (!isMock) return request('/api/simulate', simulationSchema, { decisions });
    await delay();
    if (isExample(decisions)) return structuredClone(exampleResult);
    const spent = decisions.reduce(
      (sum, d) => sum + (measures.find((m) => m.id === d.measureId)?.cost ?? 0),
      0,
    );
    return {
      modelVersion: 'organizer-dataset-v1',
      source: 'fixture',
      decisions,
      validation: { status: decisions.length === 0 ? 'valid' : 'unverified', errors: [] },
      budget: { total: 100, spent, remaining: 100 - spent },
      before: structuredClone(baseline),
      after: decisions.length === 0 ? structuredClone(baseline) : null,
      scoreDelta: decisions.length === 0 ? 0 : null,
      synergies: [],
      contributions: [],
      notice:
        'Деморежим: произвольные наборы требуют backend. Для полного просмотра загрузите контрольный пример.',
    };
  },
  async finalize(decisions: Decision[]) {
    if (!isMock) return request('/api/scenario/finalize', simulationSchema, { decisions });
    await delay();
    if (!isExample(decisions))
      throw new ApiError(
        'В деморежиме итог доступен только для контрольного примера. Подключите backend для расчёта своего плана.',
      );
    return structuredClone(exampleResult);
  },
  async analyze(result: Simulation, catalog: Measure[] = []) {
    if (!isMock)
      return normalizeAnalysis(
        await request('/api/ai/analyze', aiResponseSchema, createAnalysisRequest(result, catalog)),
      );
    await delay();
    return structuredClone(exampleAnalysis);
  },
  async recommend(decisions: Decision[]) {
    if (isMock || !recommendationsEnabled)
      throw new ApiError('Поиск замены станет доступен после подключения расчётного API.');
    return request('/api/recommend', recommendationSchema, { decisions });
  },
};
