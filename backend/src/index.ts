import Fastify from 'fastify';
import cors from '@fastify/cors';
import dotenv from 'dotenv';
import { trafficRoutes } from './routes/traffic';
import { dashboardRoutes } from './routes/dashboard';
import { trendsRoutes } from './routes/trends';
import { healthRoute } from './routes/health';

dotenv.config();

const server = Fastify({
  logger: true
});

const PORT = parseInt(process.env.PORT || '3000', 10);
const HOST = process.env.HOST || '0.0.0.0';

async function start() {
  try {
    // Register CORS
    await server.register(cors, {
      origin: true
    });

    // Register routes
    await server.register(healthRoute);
    await server.register(trafficRoutes);
    await server.register(dashboardRoutes);
    await server.register(trendsRoutes);

    await server.listen({ port: PORT, host: HOST });
    console.log(`Backend server running on http://${HOST}:${PORT}`);
  } catch (err) {
    server.log.error(err);
    process.exit(1);
  }
}

start();
