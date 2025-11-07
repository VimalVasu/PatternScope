import { FastifyPluginAsync } from 'fastify';
import { pool } from '../db';

export const healthRoute: FastifyPluginAsync = async (server) => {
  server.get('/health', async (request, reply) => {
    try {
      // Check database connection
      await pool.query('SELECT 1');

      return {
        status: 'ok',
        timestamp: new Date().toISOString(),
        service: 'backend',
        database: 'connected'
      };
    } catch (error) {
      reply.code(503);
      return {
        status: 'error',
        timestamp: new Date().toISOString(),
        service: 'backend',
        database: 'disconnected',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  });
};
