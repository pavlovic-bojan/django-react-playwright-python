import { setupServer } from "msw/node";

/**
 * MSW Node.js server used in Vitest tests.
 *
 * The server is started / reset / stopped in `setup.ts` for every test file.
 * Individual tests can add per-test overrides with `server.use(...)`.
 */
export const server = setupServer();
