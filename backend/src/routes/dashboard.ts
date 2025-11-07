import { FastifyPluginAsync } from 'fastify';
import { pool } from '../db';

export const dashboardRoutes: FastifyPluginAsync = async (server) => {
  // GET /dashboard/summary - Get dashboard summary
  server.get<{
    Querystring: { start?: string; end?: string }
  }>('/dashboard/summary', async (request, reply) => {
    const { start, end } = request.query;

    try {
      const values: any[] = [];
      const conditions: string[] = [];

      if (start) {
        conditions.push(`timestamp >= $${values.length + 1}`);
        values.push(start);
      }

      if (end) {
        conditions.push(`timestamp <= $${values.length + 1}`);
        values.push(end);
      }

      const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

      // Get traffic summary
      const trafficQuery = `
        SELECT
          COUNT(*) as event_count,
          SUM(vehicle_count) as total_vehicles,
          AVG(avg_speed) as average_speed,
          MIN(avg_speed) as min_speed,
          MAX(avg_speed) as max_speed
        FROM traffic_events
        ${whereClause}
      `;

      const trafficResult = await pool.query(trafficQuery, values);

      // Get anomaly count
      const anomalyConditions = conditions.map(c => c.replace('timestamp', 'detected_at'));
      const anomalyWhereClause = anomalyConditions.length > 0 ? `WHERE ${anomalyConditions.join(' AND ')}` : '';

      const anomalyQuery = `
        SELECT COUNT(*) as anomaly_count
        FROM anomalies
        ${anomalyWhereClause}
      `;

      const anomalyResult = await pool.query(anomalyQuery, values);

      return {
        ...trafficResult.rows[0],
        anomaly_count: parseInt(anomalyResult.rows[0].anomaly_count),
        period: {
          start: start || null,
          end: end || null
        }
      };
    } catch (error) {
      server.log.error(error);
      reply.code(500);
      return {
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  });

  // GET /dashboard/timeseries - Get timeseries data for charts
  server.get<{
    Querystring: { start?: string; end?: string }
  }>('/dashboard/timeseries', async (request, reply) => {
    const { start, end } = request.query;

    try {
      const values: any[] = [];
      const conditions: string[] = [];

      if (start) {
        conditions.push(`timestamp >= $${values.length + 1}`);
        values.push(start);
      }

      if (end) {
        conditions.push(`timestamp <= $${values.length + 1}`);
        values.push(end);
      }

      const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

      const query = `
        SELECT
          DATE_TRUNC('hour', timestamp) as time_bucket,
          SUM(vehicle_count) as vehicle_count,
          AVG(avg_speed) as avg_speed,
          COUNT(*) as event_count
        FROM traffic_events
        ${whereClause}
        GROUP BY time_bucket
        ORDER BY time_bucket
      `;

      const result = await pool.query(query, values);

      return {
        timeseries: result.rows
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
