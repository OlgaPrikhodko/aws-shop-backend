Go to the Elastic Beanstalk console:

Select your environment

Go to Configuration

Under Software, modify Environment properties to add:

PRODUCT_SERVICE_URL=https://6krhhlmu2l.execute-api.eu-west-1.amazonaws.com/prod
CART_SERVICE_URL=http://prod2.eba-pknfh9hv.eu-west-1.elasticbeanstalk.com
PORT=8081


Copy

Insert at cursor
Update your server.ts with proper CORS and error handling:

import * as http from "http";
import * as https from "https";
import { URL } from "url";
import * as dotenv from "dotenv";

dotenv.config();

const logger = {
  info: (message: string, ...args: any[]) => {
    console.log(`[${new Date().toISOString()}] INFO: ${message}`, ...args);
  },
  error: (message: string, ...args: any[]) => {
    console.error(`[${new Date().toISOString()}] ERROR: ${message}`, ...args);
  },
};

// Service routes configuration with validation
const serviceRoutes: Record<string, string | undefined> = {
  "/api/products": process.env.PRODUCT_SERVICE_URL,
  "/api/cart": process.env.CART_SERVICE_URL,
};

// Validate required environment variables
Object.entries(serviceRoutes).forEach(([key, value]) => {
  if (!value) {
    logger.error(`Missing environment variable for ${key}`);
    process.exit(1);
  }
});

const forwardRequest = (
  clientReq: http.IncomingMessage,
  clientRes: http.ServerResponse,
  targetUrl: string
): void => {
  const url = new URL(clientReq.url || "", targetUrl);

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
    clientRes.writeHead(502, { "Content-Type": "application/json" });
    clientRes.end(
      JSON.stringify({
        message: "Cannot process request",
        error: error.message,
      })
    );
  });

  clientReq.pipe(proxyReq, { end: true });
};

const server = http.createServer((req, res) => {
  const reqUrl = new URL(req.url || "", `http://${req.headers.host}`);

  // Set CORS headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader(
    "Access-Control-Allow-Methods",
    "GET, POST, PUT, DELETE, OPTIONS"
  );
  res.setHeader(
    "Access-Control-Allow-Headers",
    "Content-Type, Authorization"
  );

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  // Health check for Elastic Beanstalk
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
    res.writeHead(502, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ message: "Cannot process request" }));
  }
});

const PORT = process.env.PORT || 8081;

server.listen(PORT, () => {
  logger.info(`BFF Service listening on port ${PORT}`);
});

// Error handling
server.on("error", (error: NodeJS.ErrnoException) => {
  logger.error("Server error:", error);
  if (error.code === "EADDRINUSE") {
    logger.error(`Port ${PORT} is already in use`);
    process.exit(1);
  }
});

process.on("uncaughtException", (error: Error) => {
  logger.error("Uncaught exception:", error);
  process.exit(1);
});

process.on("unhandledRejection", (reason: unknown) => {
  logger.error("Unhandled Rejection:", reason);
  process.exit(1);
});


Copy

Insert at cursor
typescript
Deploy your application:

eb deploy


Copy

Insert at cursor
bash
To verify the deployment:

Check the health of your application in the Elastic Beanstalk console

Test the endpoints:

# Test Product Service
curl https://{yours_github_account_login}-bff-api-production.eu-west-1.elasticbeanstalk.com/api/products

# Test Cart Service
curl https://{yours_github_account_login}-bff-api-production.eu-west-1.elasticbeanstalk.com/api/cart


Copy

Insert at cursor
bash
Key features of this deployment:

Single instance environment

Custom domain name

Environment variables for service URLs

Health check endpoint

Proper error handling

CORS configuration

Request forwarding for both services

Logging for debugging

Remember to:

Replace {yours_github_account_login} with your actual GitHub username

Ensure all environment variables are set in Elastic Beanstalk

Test all endpoints after deployment

Monitor the application logs for any issues

The BFF service will now properly forward requests to both the Product Service and Cart Service while maintaining proper error handling and status codes.

