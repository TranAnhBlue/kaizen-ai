FROM node:22-alpine
WORKDIR /app
COPY backend/package*.json ./
RUN npm install
COPY backend/ ./
RUN npx prisma generate && npm run build
EXPOSE 3001
CMD ["node", "dist/main.js"]
