# Etapa 1: Build con dependencias controladas
FROM node:20 AS build

WORKDIR /app

# Solo copias los archivos necesarios primero (mejor cache)
COPY package.json package-lock.json ./
RUN npm install

# Ahora sí copias el resto
COPY . .

# Ejecutas el build usando vite de devDependencies
RUN npm run build

# Etapa 2: Contenedor mínimo para servir la app
FROM node:20-slim

WORKDIR /app
RUN npm install -g serve

COPY --from=build /app/dist ./dist

EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
