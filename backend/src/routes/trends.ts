import { FastifyPluginAsync } from 'fastify';
import { pool } from '../db';

export const trendsRoutes: FastifyPluginAsync = async (server) => {
  // GET /trends/suggestions - Get trend suggestions
  server.get<{
    Querystring: { start?: string; end?: string }
  }>('/trends/suggestions', async (request, reply) => {
    const { start, end } = request.query;

    try {
      const values: any[] = [];
      const conditions: string[] = [];

      if (start) {
        conditions.push(`created_at >= $${values.length + 1}`);
        values.push(start);
      }

      if (end) {
        conditions.push(`created_at <= $${values.length + 1}`);
        values.push(end);
      }

      const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

      const query = `
        SELECT
          id,
          created_at,
          time_period_start,
          time_period_end,
          suggestion_type,
          confidence_level,
          description,
          related_anomalies,
          action_taken
        FROM trend_suggestions
        ${whereClause}
        ORDER BY created_at DESC
        LIMIT 50
      `;

      const result = await pool.query(query, values);

      return {
        suggestions: result.rows
      };
    } catch (error) {
      server.log.error(error);
      reply.code(500);
      return {
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  });
};
