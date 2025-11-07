import { FastifyPluginAsync } from 'fastify';
import { pool } from '../db';

interface TrafficEvent {
  timestamp: string;
  location_id: number;
  vehicle_count: number;
  avg_speed?: number;
  min_speed?: number;
  max_speed?: number;
  color_counts?: Record<string, number>;
  inter_arrival_stats?: Record<string, any>;
  traffic_density_score?: number;
  raw_features?: Record<string, any>;
}

const trafficEventSchema = {
  body: {
    type: 'object',
    required: ['timestamp', 'location_id', 'vehicle_count'],
    properties: {
      timestamp: { type: 'string', format: 'date-time' },
      location_id: { type: 'number' },
      vehicle_count: { type: 'number' },
      avg_speed: { type: 'number' },
      min_speed: { type: 'number' },
      max_speed: { type: 'number' },
      color_counts: { type: 'object' },
      inter_arrival_stats: { type: 'object' },
      traffic_density_score: { type: 'number' },
      raw_features: { type: 'object' }
    }
  }
};

export const trafficRoutes: FastifyPluginAsync = async (server) => {
  // POST /ingest/traffic - Ingest traffic events
  server.post<{ Body: TrafficEvent }>(
    '/ingest/traffic',
    { schema: trafficEventSchema },
    async (request, reply) => {
      const event = request.body;

      try {
        const query = `
          INSERT INTO traffic_events (
            timestamp, location_id, vehicle_count, avg_speed, min_speed, max_speed,
            color_counts, inter_arrival_stats, traffic_density_score, raw_features
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
          RETURNING id
        `;

        const values = [
          event.timestamp,
          event.location_id,
          event.vehicle_count,
          event.avg_speed || null,
          event.min_speed || null,
          event.max_speed || null,
          event.color_counts ? JSON.stringify(event.color_counts) : null,
          event.inter_arrival_stats ? JSON.stringify(event.inter_arrival_stats) : null,
          event.traffic_density_score || null,
          event.raw_features ? JSON.stringify(event.raw_features) : null
        ];

        const result = await pool.query(query, values);

        reply.code(201);
        return {
          success: true,
          id: result.rows[0].id
        };
      } catch (error) {
        server.log.error(error);
        reply.code(500);
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        };
      }
    }
  );

  // GET /metrics/traffic - Get aggregated traffic metrics
  server.get<{
    Querystring: { start?: string; end?: string }
  }>('/metrics/traffic', async (request, reply) => {
    const { start, end } = request.query;

    try {
      let query = `
        SELECT
          COUNT(*) as event_count,
          SUM(vehicle_count) as total_vehicles,
          AVG(avg_speed) as average_speed,
          MIN(timestamp) as period_start,
          MAX(timestamp) as period_end
        FROM traffic_events
      `;

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

      if (conditions.length > 0) {
        query += ` WHERE ${conditions.join(' AND ')}`;
      }

      const result = await pool.query(query, values);

      // Get timeseries data
      let timeseriesQuery = `
        SELECT
          DATE_TRUNC('hour', timestamp) as time_bucket,
          SUM(vehicle_count) as vehicle_count,
          AVG(avg_speed) as avg_speed
        FROM traffic_events
      `;

      if (conditions.length > 0) {
        timeseriesQuery += ` WHERE ${conditions.join(' AND ')}`;
      }

      timeseriesQuery += ` GROUP BY time_bucket ORDER BY time_bucket`;

      const timeseriesResult = await pool.query(timeseriesQuery, values);

      return {
        summary: result.rows[0],
        timeseries: timeseriesResult.rows
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
