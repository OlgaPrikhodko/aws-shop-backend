import * as http from "http";
import * as https from "https";
import { URL } from "url";
import * as dotenv from "dotenv";

dotenv.config();

// Basic console logger with timestamp
const logger = {
  info: (message: string, ...args: any[]) => {
    console.log(`[${new Date().toISOString()}] INFO: ${message}`, ...args);
  },
  error: (message: string, ...args: any[]) => {
    console.error(`[${new Date().toISOString()}] ERROR: ${message}`, ...args);
  },
};

// Service routes configuration
const serviceRoutes: Record<string, string> = {
  "/api/products": process.env.PRODUCT_SERVICE_URL || "http://localhost:3001",
  "/api/cart": process.env.CART_SERVICE_URL || "http://localhost:3004",
};

// Update CORS to allow frontend domain
const ALLOWED_ORIGINS = [process.env.FRONTEND_URL, "http://localhost:3000"];

const forwardRequest = (
  clientReq: http.IncomingMessage,
  clientRes: http.ServerResponse,
  targetUrl: string
): void => {
  const url = new URL(clientReq.url || "", targetUrl);

  // Special handling for import service
  const authURl = process.env.IMPORT_SERVICE_URL;
  if (authURl) {
    if (url.toString().includes(authURl)) {
      if (!clientReq.headers.authorization) {
        clientRes.writeHead(401, { "Content-Type": "application/json" });
        clientRes.end(
          JSON.stringify({ message: "Authorization header required" })
        );
        return;
      }
    }
  }

  const options: http.RequestOptions = {
    method: clientReq.method,
    headers: {
      ...clientReq.headers,
      host: url.host,
    },
  };

  const proxyReq = (url.protocol === "https:" ? https : http).request(
    url,
    options,
    (proxyRes) => {
      clientRes.writeHead(proxyRes.statusCode || 500, proxyRes.headers);
      proxyRes.pipe(clientRes, { end: true });
    }
  );

  proxyReq.on("error", (error) => {
    logger.error("Proxy request error:", error.message);
    clientRes.writeHead(500, { "Content-Type": "application/json" });
    clientRes.end(
      JSON.stringify({
        message: "Internal Server Error",
        error: error.message,
      })
    );
  });

  clientReq.pipe(proxyReq, { end: true });
};

const server = http.createServer((req, res) => {
  const reqUrl = new URL(req.url || "", `http://${req.headers.host}`);

  // Enhanced CORS handling with specific origin
  const origin = req.headers.origin;
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader("Access-Control-Allow-Origin", origin);
    res.setHeader(
      "Access-Control-Allow-Methods",
      "GET, POST, PUT, DELETE, OPTIONS"
    );
    res.setHeader(
      "Access-Control-Allow-Headers",
      "Content-Type, Authorization"
    );
    res.setHeader("Access-Control-Allow-Credentials", "true");
  }
  // Handle preflight requests
  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  // Log request
  logger.info(`${req.method} ${reqUrl.pathname}`);

  // Health check endpoint
  if (reqUrl.pathname === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "healthy" }));
    return;
  }

  // Find target service
  const targetService = Object.entries(serviceRoutes).find(([path]) =>
    reqUrl.pathname.startsWith(path)
  );

  if (!targetService) {
    res.writeHead(502, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ message: "Cannot process request" }));
    return;
  }

  const [basePath, targetUrl] = targetService;
  const targetPath = reqUrl.pathname.replace(basePath, "");
  const targetUrlWithPath = `${targetUrl}${targetPath}${reqUrl.search}`;

  try {
    forwardRequest(req, res, targetUrlWithPath);
  } catch (error) {
    logger.error("Request handling error:", error);
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end(
      JSON.stringify({
        message: "Internal Server Error",
        error: error instanceof Error ? error.message : "Unknown error",
      })
    );
  }
});

const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
  logger.info(`BFF Service listening on port ${PORT}`);
});

// Error handling for server
server.on("error", (error: NodeJS.ErrnoException) => {
  logger.error("Server error:", error);
  if (error.code === "EADDRINUSE") {
    logger.error(`Port ${PORT} is already in use`);
    process.exit(1);
  }
});

// Handle uncaught exceptions
process.on("uncaughtException", (error: Error) => {
  logger.error("Uncaught exception:", error);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on("unhandledRejection", (reason: unknown) => {
  logger.error("Unhandled Rejection:", reason);
  process.exit(1);
});
