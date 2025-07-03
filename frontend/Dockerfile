FROM node:20 AS build

WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

FROM node:20-slim

WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist

EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]