FROM node:22-bookworm-slim
WORKDIR /app
COPY backend/package*.json ./
RUN npm install --no-audit --no-fund
COPY backend/ ./
RUN npx prisma generate && npm run build
ENV NODE_ENV=production
EXPOSE 3001
CMD ["node", "dist/main.js"]
